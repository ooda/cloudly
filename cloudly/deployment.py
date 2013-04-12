"""Ease deployment of applications.

WARNING: to be deprecated.
"""
from fabric.api import run
from cuisine import (package_ensure, package_update, file_write,
                     python_package_ensure, mode_sudo, repository_ensure_apt,
                     dir_ensure, sudo)

PACKAGES = [
    "python-distribute",
    "python-dev",
    "gcc",
    "redis-server",
    "couchdb",
    "supervisor",
    "git"
]

BASH_LOGIN = """
export WORKON_HOME=$HOME/.virtualenvs
mkdir -p $WORKON_HOME

VIRTUALENVWRAPPER=/usr/local/bin/virtualenvwrapper.sh
if [ -f $VIRTUALENVWRAPPER ]; then
    source $VIRTUALENVWRAPPER
fi
"""


def standard_setup():
    """Set up an AWS EC2 instance:

        1. Update all packages
        2. Install packages we need
        3. Install pip
        4. Install virtualenvwrapper
    """
    print "Doing standard instance setup."
    package_update()
    package_ensure(PACKAGES)
    # Install pip
    run("curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | "
        "sudo python")
    # Install virtualenv and virtualenvwrapper
    with mode_sudo():
        python_package_ensure("virtualenvwrapper")
    # Add virtualenvwrapper initialization to bashrc
    file_write("$HOME/.bash_login", BASH_LOGIN)


def salt_init(name, salt_state_file):
    """ Initialize a server with a minimal Salt masterless setup.
    cf. http://docs.saltstack.com/topics/tutorials/quickstart.html

    Ensure the package `salt-minion` is installed.
    Create directory /srv/salt
    Write files top.sls and `name`.sls.
    Run salt-call
    """
    package_ensure("python-software-properties")
    repository_ensure_apt("ppa:saltstack/salt")
    package_update()
    package_ensure("salt-minion")
    with mode_sudo():
        dir_ensure("/srv/salt/", recursive=True)
        file_write("/srv/salt/top.sls", "base:\n  '*':\n    - {}".format(name))
        with open(salt_state_file) as f:
            content = f.readlines()
        file_write("/srv/salt/{}.sls".format(name), "".join(content))
    # Can't figure out why calling `run` under mode_sudo doesn't work.
    sudo("salt-call --local state.highstate")
