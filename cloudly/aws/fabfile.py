"""
Fabric file to handle status and deploy.

Usage:

Either use -H to specify a host, or -R for a role. Otherwise will prompt
you with list of hosts.
"""

import os
import getpass
import functools
from time import sleep

from fabric.api import (
    run, env, cd, settings, puts, runs_once, task
)
from fabric.operations import prompt

from cloudly.aws import ec2
from cloudly import deployment
import boto

DEFAULT_AMI = "ami-82fa58eb"
AWS_USERNAME = os.environ.get("AWS_USERNAME", "ubuntu")
GIT_WORK_TREE = os.environ.get("AWS_DEPLOY_DIR", "service")
DEPLOY_LOCATION = os.path.join(
    "/home", AWS_USERNAME, GIT_WORK_TREE
)

ROLES = ["development", "production"]

INSTANCES_HEADER = "{0:<4}  {1:<20} {2:<16} {3:<12} {4:<12} {5:<13}".format(
    "", "Name", "IP address", "Launch time", "Instance ID", "Image ID"
)


def get_role_def(rolename):
    """For the specific rolename, yields a list of hosts for that role."""
    for instance in ec2.all():
        if instance.public_dns_name:
            if instance.role == rolename:
                yield instance.public_dns_name

env.roledefs = dict([
    # Use a partial to create a callable that will only get called when a role
    # is requested.
    (n, functools.partial(get_role_def, n))
    for n in ROLES
])


def set_environment(fn):
    """Dynamically set fabric environment for wrapped tasks.
    The environment set-up include:
        - user
        - key_filename
        - key_name
    """
    @functools.wraps(fn)
    def wrapped_fn(*args, **kwargs):
        key_name = getpass.getuser()
        key_filename = "{}/key_pairs/{}.pem".format(
            os.environ["AWS_DIR"],
            key_name,
        )
        with settings(user=AWS_USERNAME,
                      key_filename=key_filename,
                      key_name=key_name):
            return fn(*args, **kwargs)

    return wrapped_fn


def print_instances(instances, show_terminated=False):
    """Print out list of hosts. Set only_running to false
    to also print out turned off machines."""
    for index, instance in enumerate(instances):
        if instance.state == "running" or show_terminated:
            format_str = ("{index:>4}: {name:<20} {instance.ip_address:<16} "
                          "{launch_time:<12} {instance.id:<12} "
                          "{instance.image_id:<13}")
            puts(format_str.format(
                index=index,
                instance=instance,
                launch_time=instance.launch_time[:10],
                name=instance.tags.get("Name", "no name")
            ))


# Please read http://stackoverflow.com/q/2326797 before modifying this.
@task
def ec2host(node_type=None):
    """Ask the user which running EC2 instance he wants to act upon."""
    # Grab instances of a certain type or all of them.
    if node_type:
        instances = ec2.get(node_type)
    else:
        instances = ec2.all()

    if len(instances) == 0:
        answer = prompt("\nType in hostname: ")
    else:
        # Print out list of hosts
        print_instances(instances)
        # Let user pick host
        answer = prompt(
            "\nChoose AMI instance [0-%d, or type in your own]: "
            % (len(instances) - 1,))

    if answer.isdigit():
        host = instances[int(answer)].public_dns_name
        instance_id = instances[int(answer)].id
    else:
        host = answer

    env.hosts = [host]
    env.instance_id = instance_id


def sv(command, services):
    """Executes the supervisor command."""
    with cd(DEPLOY_LOCATION):
        for service in services:
            run("%s service/%s" % (command, service))


@task
@set_environment
def up(*services):
    """Start remote services

        :param services: A list of services to be started.
    """
    sv("svc -u", services)


@task
@set_environment
def down(*services):
    """Shutdown remote services.

        :param services: A list of services to be started.
    """
    sv("svc -d", services)


@task
@set_environment
def restart(*services):
    """Restart remote services.

        :param services: A list of services to be started.
    """
    down(*services)
    up(*services)


@task
@set_environment
def status(*services):
    """Output the status of remote services.

        :param services: A list of services to be started.
    """
    # TODO: The output of this is not very readable. Should change.
    sv("svstat", services)


@task
@set_environment
@runs_once
def list():
    """Lists all the available hosts by role."""
    puts(INSTANCES_HEADER)
    print_instances(
        ec2.all(),
        False
    )


@task
@set_environment
def launch(ami_image_id=DEFAULT_AMI, count=1):
    """Launch a new AWS EC2 instance.

    The exact image is given by the global variable DEFAULT_AMI.
    """
    connection = boto.connect_ec2()
    reservation = connection.run_instances(ami_image_id,
                                           min_count=count,
                                           key_name=env.key_name,
                                           instance_type="t1.micro",
                                           security_groups=['basic'])
    ready = False
    instances = reservation.instances
    puts("Launching {!r} instance(s)".format(len(instances)))
    while not ready:
        puts(".", end='', flush=True)
        sleep(2)
        [instance.update() for instance in instances]
        ready = all([instance.state == 'running' for instance in instances])

    puts(" done")
    puts("Your new instance(s):")
    puts(INSTANCES_HEADER)
    print_instances(instances)
    puts("Now configuring.")
    with settings(hosts=[instance.public_dns_name for instance in instances]):
        puts(env.hosts)
        puts(env.user)
        deployment.standard_setup()


@task
@set_environment
def terminate():
    """Terminate the selected instance."""
    connection = boto.connect_ec2()
    connection.terminate_instances([env.instance_id])
