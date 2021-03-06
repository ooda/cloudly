import os
import sys
import itertools
import urllib

import boto
from boto import ec2
from boto.exception import EC2ResponseError

from cloudly.decorators import Memoized
from cloudly import logger

EC2_METADATA_URL = "http://169.254.169.254/latest/meta-data/"
DEFAULT_AMI_ID = "ami-0cdf4965"

log = logger.init(__name__)


class NoEc2Instance(Exception):
    """Raised when we could not find an EC2 instance for this host, either
    because we are not running under EC2 or because of a network outage
    preventing us from fetching instance data."""


def all():
    """Fetches all EC2 instances currently running."""
    connection = ec2.connection.EC2Connection()
    instance_list = itertools.chain.from_iterable(
        [r.instances for r in connection.get_all_instances()])
    running = [i for i in instance_list if i.state == "running"]
    return map(augment, running)


def get(node_type):
    return [host for host in all() if host.node_type == node_type]


def get_own():
    """Returns the instance on which the caller is running.

    Returns a boto.ec2.instance.Instance object augmented by tag attributes.

    IMPORTANT: This method will raise an exception if the network
    fails. Don't forget to catch it early because we must recover from
    this, fast. Also, it will throw an exception if you are not running
    under EC2, so it is preferable to use is_running_on_ec2 before calling
    this method.
    """
    try:
        instance_id = _query("instance-id")
        if not instance_id:
            raise NoEc2Instance(
                "Can't find own instance id. Are you running under EC2?")
        return filter(lambda i: i.id == instance_id, all())[0]
    except EC2ResponseError:
        raise NoEc2Instance("Cannot find instance %r" % instance_id)


def find_service_ip(service):
    """Return a list of ip addresses offering the given service. This uses the
    'services' tag of an EC2 instance.
    """
    hosts = filter(lambda h: service in h.services, all())
    return [get_best_ip_addresse(host) for host in hosts]


def get_hostname(service):
    """Return the first host's IP address hosting the given service.
    """
    try:
        hosts = find_service_ip(service)
    except Exception, exception:
        # An exception is thrown whenever AWS credentials are not presented
        # in the environment. That's ok. We'll use localhost.
        log.info(exception)
        hosts = []
    # Use the first host in the returned list. Could be changed by adding an
    # argument which would be a function for choosing amidst the list.
    return hosts[0] if hosts else None


@Memoized
def is_running_on_ec2():
    """Return true if the current process is running on an EC2 instance."""
    if _query():
        return True
    else:
        return False


def get_best_ip_addresse(instance):
    """Return the private ip address if running under EC2 or the public one
    otherwise.
    """
    if is_running_on_ec2():
        return instance.private_ip_address
    else:
        return instance.ip_address


def _query(meta=""):
    """Query an EC2 instance using the local EC2 URL.

    Don't use this method outside this class, use the class attributes
    instead.

        :param meta: The metadata to query.
    """
    try:
        metadata = urllib.urlopen(EC2_METADATA_URL + meta).read()
    except IOError:
        metadata = None
    return metadata


class TagAttribute(object):
    """A class attribute mapped to an EC2 tag.

    The instance tag is updated as soon as the attribute is mutated.
    """
    def __init__(self, key):
        self.key = key

    def __get__(self, instance, owner):
        return instance.tags.get(self.key)

    def __set__(self, instance, value):
        instance.add_tag(self.key, value)

    def __delete__(self, instance):
        instance.remove_tag(self.key)


class TagList(list):
    """A list tag, mapped to an EC2 instance tag.

    NOTE: this is not a list of tags, but rather a tag which is a list of
    values. It is represented on EC2 by a comma delimited string.
    The tag is updated as soon as the list is mutated.
    """
    def __init__(self, attribute, instance, values):
        super(TagList, self).__init__(values)
        self.attribute = attribute
        self.instance = instance

    def update(self):
        self.attribute.__set__(self.instance, self)

    def __setitem__(self, index, value):
        super(TagList, self).__setitem__(index)
        self.update()

    def __delitem__(self, index):
        super(TagList, self).__delitem__(index)
        self.update()

    def append(self, value):
        super(TagList, self).append(value)
        self.update()

    def remove(self, index):
        super(TagList, self).remove(index)
        self.update()


class TagListAttribute(TagAttribute):
    """A descriptor: a class attribute mapped to an EC2 list tag.

    The attribute is a list and is represented by a comma delimited string.
    The EC2 instance tag is updated as soon as the attribute is mutated.
    NOTE: the comma delimited string should not contain spaces.
    """
    def __init__(self, key):
        self.key = key

    def __get__(self, instance, owner):
        if self.key not in instance.tags:
            instance.add_tag(self.key, '')
            return TagList(self, instance, [])
        value = instance.tags.get(self.key)
        value = value.split(',') if value else []
        return TagList(self, instance, value)

    def __set__(self, instance, values):
        instance.add_tag(self.key, ",".join(values))

    def __delete__(self, instance):
        instance.remove_tag(self.key)


# NOTE: This is kind of a hack. A formal delegation pattern would probably be
# better in the long run.
def augment(instance):
    """Adds class attributes to the given instance.

    These attributes map to instance tags. There are two different types of tag
    attributes: simple strings and lists of strings.
    """
    setattr(instance.__class__, "services", TagListAttribute("services"))
    setattr(instance.__class__, "status", TagAttribute("status"))
    setattr(instance.__class__, "node_type", TagAttribute("node_type"))
    setattr(instance.__class__, "role", TagAttribute("role"))
    return instance


def launch(ami_id=None, instance_type=None,
           security_group=None, count=1, key_name=None, user_data=None):
    """Launch a new AWS EC2 instance.
    Parameters are taken from the function arguments or the environment.
    """
    ami_id = ami_id or os.environ.get("EC2_AMI_ID", DEFAULT_AMI_ID)
    instance_type = instance_type or os.environ.get("EC2_INSTANCE_TYPE",
                                                    'm1.small')
    security_group = security_group or os.environ.get("EC2_SECURITY_GROUP",
                                                      "default")
    key_name = key_name or os.environ.get("USER")

    connection = boto.connect_ec2()
    reservation = connection.run_instances(ami_id,
                                           min_count=count,
                                           key_name=key_name,
                                           instance_type=instance_type,
                                           security_groups=[security_group],
                                           user_data=user_data)
    return reservation.instances


def print_instances(instances, show_terminated=False):
    """Print out list of hosts. Set only_running to false
    to also print out turned off machines."""
    for index, instance in enumerate(instances):
        if instance.state == "running" or show_terminated:
            sys.stdout.write(("{index:>4}: {name:<20} "
                              "{instance.ip_address:<16} "
                              "{launch_time:<12} {instance.id:<12} "
                              "{instance.image_id:<13}\n").format(
                                  index=index,
                                  instance=instance,
                                  launch_time=instance.launch_time[:10],
                                  name=instance.tags.get("Name", "no name")
                              ))


def choose_instance():
    instances = all()
    if len(instances) == 1:
        return instances[0]

    print_instances(instances)
    index = raw_input("\nChoose AMI instance (None): ")
    instance = None
    if index.isdigit() and int(index) < len(instances):
        instance = instances[int(index)]
    return instance
