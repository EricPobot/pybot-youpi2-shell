from pybot.fabtasks import *
from fabric.api import env
from fabric.state import output

output.output = False

PREFIX = '/home/pi/.local'
CMDE_BASE = "PYTHONPATH=%(prefix)s/lib/python2.7/site-packages %(prefix)s/bin/youpi2-shell-systemd-" % {'prefix': PREFIX}


@task()
def install_service():
    sudo(CMDE_BASE + 'install', shell=True)


@task()
def remove_service():
    sudo(CMDE_BASE + 'remove', shell=True)


@task()
def restart_service():
    sudo('systemctl restart youpi2-shell', shell=True)
