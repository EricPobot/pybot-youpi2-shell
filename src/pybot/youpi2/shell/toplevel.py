# -*- coding: utf-8 -*-

""" Youpi top level controller

Manages the arm and the user interactions.
"""

import subprocess
import logging.config
import signal
import time
import argparse

from pybot.core import log

from pybot.youpi2.shell.__version__ import version

from pybot.youpi2.ctlpanel.widgets import Menu, Selector
from pybot.youpi2.ctlpanel.api import ControlPanel, Interrupted
from pybot.youpi2.ctlpanel.devices.fs import FileSystemDevice
from pybot.youpi2.ctlpanel.keys import Keys

from pybot.youpi2.shell.actions.about import DisplayAbout
from pybot.youpi2.shell.actions.extproc import DemoAuto, WebServicesControl, BrowserlUi, GamepadControl, MinitelUi
from pybot.youpi2.shell.actions.youpi_maint import Reset, Disable

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


class TopLevel(object):
    SHUTDOWN = -9
    QUIT = -10

    def __init__(self, can_quit_to_shell=False):
        self.logger = log.getLogger()

        self._active = True
        self.can_quit_to_shell = can_quit_to_shell

        self.panel = ControlPanel(FileSystemDevice('/mnt/lcdfs'))
        # TODO
        self.arm = None

    def display_about(self):
        DisplayAbout(self.panel, None, version=version).execute()

    def _terminate_sig_handler(self, sig, frame):
        self.logger.info("signal %s received", {
                signal.SIGINT: 'SIGINT',
                signal.SIGTERM: 'SIGTERM',
                signal.SIGKILL: 'SIGKILL',
            }.get(sig, str(sig))
        )
        self._active = False
        self.panel.terminate()

    def run(self):
        signal.signal(signal.SIGTERM, self._terminate_sig_handler)
        signal.signal(signal.SIGINT, self._terminate_sig_handler)

        self.logger.info('-' * 40)
        self.logger.info('started')
        self.logger.info('version: %s', version)
        self.logger.info('-' * 40)
        self.panel.reset()
        self.display_about()

        menu = Menu(
            title='Main menu',
            choices={
                Keys.PREVIOUS: ('System', self.system_functions),
                Keys.NEXT: ('Mode', self.mode_selector),
            },
            panel=self.panel
        )

        try:
            while self._active:
                menu.display()
                action = menu.handle_choice()
                if action == self.QUIT:
                    self.logger.info('QUIT key used')
                    self.panel.leds_off()
                    break

        except Interrupted:
            self.logger.info('program interrupted')

        self.panel.reset()
        self.logger.info('terminated')

    def sublevel(self, title, choices):
        """ Displays a navigation sub-level page with an action spinner, and executes
        the selected ones until the user chooses to return from this level
        by using the ESC/Cancel key.

        :param str title: the title displayed for the sub-level page
        :param iterable choices: the selector choices specification (see `Selector` class documentation)
        """
        self.logger.info('entering sub-level "%s"', title)

        sel = Selector(
            title=title,
            choices=choices,
            panel=self.panel
        )

        try:
            while self._active:
                sel.display()
                if sel.handle_choice():
                    return

        except Interrupted:
            self.logger.info('exiting from sub-level "%s" after external interruption', title)
            raise

        except Exception as e:
            self.logger.info('exiting from sub-level "%s" with unexpected error %s', title, e)

        else:
            self.logger.info('exiting from sub-level "%s"', title)

    def mode_selector(self):
        self.sublevel(
            title='Select mode',
            choices=(
                ('Demo', DemoAuto(self.panel, self.arm, self.logger).execute),
                ('Gamepad', GamepadControl(self.panel, self.arm, self.logger).execute),
                ('Minitel UI', MinitelUi(self.panel, self.arm, self.logger).execute),
                ('Network', self.network_control),
            )
        )

    def network_control(self):
        self.sublevel(
            title='Network mode',
            choices=(
                ('Web services', WebServicesControl(self.panel, self.arm, self.logger).execute),
                ('Browser UI', BrowserlUi(self.panel, self.arm, self.logger).execute),
            )
        )

    def system_functions(self):
        self.sublevel(
            title='System',
            choices=(
                ('About', self.display_about_modal),
                ('Reset Youpi', Reset(self.panel, self.arm, self.logger).execute),
                ('Disable Youpi', Disable(self.panel, self.arm, self.logger).execute),
                ('Shutdown', self.shutdown),
            )
        )

    def display_about_modal(self):
        self.display_about()

    def _shutdown_action(self, title, command):
        if self.panel.countdown(title, delay=3, can_abort=True):
            self.logger.info("executing : %s", command)
            subprocess.call('(sleep 1 ; sudo %s) &' % command, shell=True)

    def _quit_to_shell(self):
        self.logger.info('"quit to shell" requested')
        self.panel.clear()
        self.panel.write_at("I'll be back...")
        time.sleep(1)

    def shutdown(self):
        choices = [
            ('Reboot', lambda: self._shutdown_action('Reboot', 'reboot')),
            ('Halt', lambda: self._shutdown_action('Halt', 'halt')),
            ('Power off', lambda: self._shutdown_action('Power off', 'poweroff')),
        ]
        if self.can_quit_to_shell:
            choices.append(('Quit to shell', self._quit_to_shell))

        self.sublevel(
            title='Shutdown',
            choices=choices
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--can-quit-to-shell',
        dest='can_quit_to_shell',
        action='store_true'
    )
    args = parser.parse_args()
    TopLevel(can_quit_to_shell=args.can_quit_to_shell).run()
