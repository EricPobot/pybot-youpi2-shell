# -*- coding: utf-8 -*-

""" Youpi top level controller

Manages the arm and the user interactions.
"""

import subprocess
import logging.config
import signal
import time
import argparse
import os
import threading

from pybot.core import log

from nros.youpi2.client import ArmClient

from pybot.youpi2.shell.__version__ import version

from pybot.youpi2.ctlpanel.widgets import Selector
from pybot.youpi2.ctlpanel.api import ControlPanel, Interrupted
from pybot.youpi2.ctlpanel.devices.fs import FileSystemDevice

from pybot.youpi2.shell.actions.info import *
from pybot.youpi2.shell.actions.extproc import *
from pybot.youpi2.shell.actions.system import *

__author__ = 'Eric Pascual'

_logging_config = log.get_logging_configuration({
    'handlers': {
        'file': {
            'filename': log.log_file_path('youpi2-shell')
        }
    },
    'root': {
        'handlers': ['file']
    }
})
logging.config.dictConfig(_logging_config)

LCDFS_MOUNT_POINT = '/mnt/lcdfs'
ARM_NODE_NAME = 'nros.youpi2'


class TopLevel(log.LogMixin):
    SHUTDOWN = -9
    QUIT = -10

    def __init__(self, can_quit_to_shell=False):
        log.LogMixin.__init__(self)

        self._is_root = os.getuid() == 0

        self.terminate_event = threading.Event()
        self.can_quit_to_shell = can_quit_to_shell

        self.panel = ControlPanel(FileSystemDevice(LCDFS_MOUNT_POINT))

        self.arm = ArmClient(ARM_NODE_NAME)

    def display_system_info(self):
        DisplaySystemInfo(self).execute()

    def _terminate_sig_handler(self, sig, frame):
        self.logger.info("signal %s received", {
                signal.SIGINT: 'SIGINT',
                signal.SIGTERM: 'SIGTERM',
                signal.SIGKILL: 'SIGKILL',
            }.get(sig, str(sig))
        )
        self.terminate_event.set()
        self.panel.terminate()

    def run(self):
        signal.signal(signal.SIGTERM, self._terminate_sig_handler)
        signal.signal(signal.SIGINT, self._terminate_sig_handler)

        self.log_starting_banner(version=version)

        self.panel.reset()
        self.log_info('displaying splash screen')
        DisplayAbout(self, version=version, long_text=False).execute()

        try:
            self.log_info('displaying main menu')
            self.sublevel(
                'Main menu',
                choices=(
                    ('Mode select', self.mode_selector),
                    ('System functions', self.system_functions),
                    ('About', self.display_about_long),
                    ('Info', self.display_system_info),
                ),
                is_toplevel=True
            )

        except Interrupted:
            self.logger.info('program interrupted')
            self.panel.reset()
            self.panel.center_text_at("External interrupt", line=2)
            self.panel.center_text_at("received", line=3)
        except ShellException:
            self.logger.critical('unrecoverable error occurred, aborting application')
            self.panel.reset()
            self.panel.center_text_at("Fatal error", line=2)
            self.panel.center_text_at("Application aborted", line=3)
        else:
            self.panel.reset()
            self.panel.center_text_at("Application exited", line=2)
            self.panel.center_text_at("I'll be back...", line=3)
            self.logger.info('terminated')
        finally:
            self.panel.leds_off()

    def sublevel(self, title, choices, is_toplevel=False):
        """ Displays a navigation sub-level page with an action spinner, and executes
        the selected ones until the user chooses to return from this level
        by using the ESC/Cancel key.

        :param str title: the title displayed for the sub-level page
        :param iterable choices: the selector choices specification (see `Selector` class documentation)
        :param bool is_toplevel: True if this level is the top-most one
        """
        self.logger.info('entering sub-level "%s"', title)

        sel = Selector(
            title=title,
            choices=choices,
            panel=self.panel,
            cancelable=not is_toplevel
        )

        try:
            while not self.terminate_event.is_set():
                sel.display()
                if sel.handle_choice():
                    return

        except Interrupted:
            self.logger.info('exiting from sub-level "%s" after external interruption', title)
            raise

        except Exception as e:
            self.logger.exception(e)
            self.logger.error('exiting from sub-level "%s" due to unexpected error', title)
            if is_toplevel:
                raise ShellException(e)

        else:
            self.logger.info('exiting from sub-level "%s"', title)

    def mode_selector(self):
        self.sublevel(
            title='Select mode',
            choices=(
                ('Automatic demo', DemoAuto(self, self.logger).execute),
                ('Minitel UI', MinitelUi(self, self.logger).execute),
                ('HTTP server', HttpServer(self, self.logger).execute),
                ('Gamepad control', GamepadControl(self, self.logger).execute),
            )
        )

    def _system_action(self, title, command):
        if self.panel.countdown(title, delay=3, can_abort=True):
            self.logger.info("executing : %s", command)
            if not self._is_root:
                command = 'sudo ' + command
            subprocess.call('(sleep 1 ; %s) &' % command, shell=True)

    def system_functions(self):
        self.sublevel(
            title='System',
            choices=(
                ('Calibrate arm', Calibrate(self, self.logger).execute),
                ('Disable arm', Disable(self, self.logger).execute),
                ('Re-init arm', Initialize(self, self.logger).execute),
                ('Restart app.', lambda: self._system_action(
                    'Application restart', 'systemctl restart youpi2-shell.service'
                )),
                ('Shutdown', self.shutdown),
            )
        )

    def display_about_long(self):
        DisplayAbout(self, version=version, long_text=True).execute()

    def _quit_to_shell(self):
        self.logger.info('"quit to shell" requested')
        self.panel.clear()
        self.panel.write_at("I'll be back...")
        time.sleep(1)

    def shutdown(self):
        choices = [
            ('Power off', lambda: self._system_action('Power off', 'systemctl poweroff')),
            ('Reboot', lambda: self._system_action('Reboot', 'systemctl reboot')),
            # ('Halt', lambda: self._system_action('Halt', 'systemctl halt')),
        ]
        if self.can_quit_to_shell:
            choices.append(('Quit to shell', self._quit_to_shell))

        self.sublevel(
            title='Shutdown',
            choices=choices
        )


class ShellException(Exception):
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--can-quit-to-shell',
        dest='can_quit_to_shell',
        action='store_true'
    )
    args = parser.parse_args()
    TopLevel(can_quit_to_shell=args.can_quit_to_shell).run()
