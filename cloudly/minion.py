"""Ease deployment of applications with Salt Stack.

Cf. http://docs.saltstack.com

"""
from time import sleep
from subprocess import check_output
import json
import sys

from cloudly.aws import ec2

SALT_BOOTSTRAP_SCRIPT = """#!/bin/bash

# Install saltstack
add-apt-repository ppa:saltstack/salt -y
apt-get update -y
apt-get install salt-minion -y
apt-get upgrade -y

HOSTNAME=`hostname`

# Set salt master location and start minion
sed -i "s/#master: salt/master: {master_hostname}/" /etc/salt/minion
sed -i "s/#id:/id: $HOSTNAME-{minion_id_postfix}/" /etc/salt/minion
restart salt-minion
"""


def launch(master_hostname, minion_id_postfix, ami_id=None, instance_type=None,
           security_group=None, count=1, key_name=None):
    """Launch an EC2 AMI instance and bootstrap Salt Stack.
    This function:
        - launch one or more EC2 AMI instances;
        - bootstrap a Salt minion on each;
        - wait for all minions to contact the master;
        - accept all minions' keys.

    WARNING: all instances will have the same postfix `minion-id`

    cf. http://docs.saltstack.com/topics/tutorials/bootstrap_ec2.html
    """
    user_data = SALT_BOOTSTRAP_SCRIPT.format(
        master_hostname=master_hostname, minion_id_postfix=minion_id_postfix)

    instances = ec2.launch(ami_id=ami_id, instance_type=instance_type,
                           security_group=security_group, key_name=key_name,
                           user_data=user_data, count=count)

    ready = False
    while not ready:
        sleep(3)
        keys = jshell("/usr/bin/salt-key -L --out json")
        [instance.update() for instance in instances]
        minion_ids = [get_minion_id(i, minion_id_postfix) for i in instances]
        ready = all([minion_id in keys['minions_pre']
                     for minion_id in minion_ids])

    for key in minion_ids:
        shell("/usr/bin/salt-key -ya {}".format(key))

    for instance in instances:
        instance.add_tag("minion_id", get_minion_id(instance,
                                                    minion_id_postfix))
    return instances


def reboot(instances):
    for instance in instances:
        instance.reboot()

    sleep(5)
    ready = False
    cmd = "/usr/bin/salt '{}' test.ping --out json"
    while not ready:
        results = []
        for instance in instances:
            minion_id = instance.tags['minion_id']
            result = shell(cmd.format(minion_id))
            if result:
                running = json.loads(result)[minion_id]
            else:
                running = False
            results.append(running)
        ready = all(results)


def salt_state(state, minion_id, env):
    # TODO: Salt returns an error code 0 even when it errors out. Bummer.
    return shell("/usr/bin/salt {} state.sls {} {}".format(minion_id, state,
                                                           env))


def salt_cmd(cmd, minion):
    return jshell("/usr/bin/salt '{}' {}".format(minion, cmd))


def jshell(cmd):
    return json.loads(shell(cmd))


def shell(cmd):
    # Note: shell=True is necessary for salt commands to be executed as the
    # authorized user. See the *user* option in /etc/salt/master.
    return check_output(cmd, shell=True)


def pip_upgrade(pkg, minions="*", venv=".virtualenv"):
    shell("salt '{}' pip.install {} upgrade=True bin_env={}".format(
        minions, pkg, venv))


def get_minion_id(instance, minion_id_postfix):
    return "{}-{}".format(instance.private_dns_name.split('.')[0],
                          minion_id_postfix)


def print_minions(instances, show_terminated=False):
    """Print out list of hosts. Set only_running to false
    to also print out turned off machines."""
    for index, instance in enumerate(instances):
        minion_id = instance.tags.get('minion_id')
        if instance.state == "running" and minion_id:
            sys.stdout.write(("{index:>4}: {name:<20} "
                              "{instance.ip_address:<16} "
                              "{launch_time:<12} {instance.id:<12} "
                              "{instance.image_id:<13} {minion_id:<15}"
                              "\n").format(
                                  minion_id=minion_id,
                                  index=index,
                                  instance=instance,
                                  launch_time=instance.launch_time[:10],
                                  name=instance.tags.get("Name", "no name"),
                              ))


def terminate(instance):
    minion_id = instance.tags['minion_id']
    shell("/usr/bin/salt-key -yd {}".format(minion_id))
    instance.terminate()
