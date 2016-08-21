# -*- coding: utf-8 -*-

""" Youpi top level controller

Manages the arm and the user interactions.
"""

import subprocess
import logging.config
import os

from pybot.core import log

from pybot.youpi2.shell.__version__ import version

from pybot.youpi2.ctlpanel.widgets import Menu, Selector
from pybot.youpi2.ctlpanel.api import ControlPanel
from pybot.youpi2.ctlpanel.devices.fs import FileSystemDevice
from pybot.youpi2.ctlpanel.keys import Keys

from pybot.youpi2.shell.actions.about import DisplayAbout
from pybot.youpi2.shell.actions.extproc import DemoAuto, WebServicesControl, BrowserlUi, GamepadControl, MinitelUi
from pybot.youpi2.shell.actions.youpi_system_actions import Reset, Disable

__author__ = 'Eric Pascual'

_logging_config = log.get_logging_configuration({
    'handlers': {
        'file': {
            'filename': os.path.expanduser('~/youpi2.log')
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

    def __init__(self):
        self.logger = log.getLogger()
        self.panel = ControlPanel(FileSystemDevice('/mnt/lcdfs'))
        # TODO
        self.arm = None

    def display_about(self):
        DisplayAbout(self.panel, None, version=version).execute()

    def run(self):
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

        while True:
            menu.display()
            action = menu.handle_choice()
            if action == self.QUIT:
                self.logger.info('QUIT key used')
                self.panel.leds_off()
                break

        self.logger.info('terminated')

    def sublevel(self, title, choices, exit_on=None):
        self.logger.info('entering sub-level "%s"', title)
        sel = Selector(
            title=title,
            choices=choices,
            panel=self.panel
        )

        try:
            exit_on = exit_on or [Selector.ESC]
            while True:
                sel.display()
                action = sel.handle_choice()
                if action in exit_on:
                    return action

        finally:
            self.logger.info('exiting from sub-level "%s" with action=%s', title, action)

    def mode_selector(self):
        action = self.sublevel(
            title='Select mode',
            choices=(
                ('Demo', DemoAuto(self.panel, self.arm, self.logger).execute),
                ('Gamepad', GamepadControl(self.panel, self.arm, self.logger).execute),
                ('Minitel UI', MinitelUi(self.panel, self.arm, self.logger).execute),
                ('Network', self.network_control),
            )
        )
        if action != Selector.ESC:
            return action

    def network_control(self):
        action = self.sublevel(
            title='Network mode',
            choices=(
                ('Web services', WebServicesControl(self.panel, self.arm, self.logger).execute),
                ('Browser UI', BrowserlUi(self.panel, self.arm, self.logger).execute),
            )
        )
        if action != Selector.ESC:
            return action

    def system_functions(self):
        return self.sublevel(
            title='System',
            choices=(
                ('About', self.display_about_modal),
                ('Reset Youpi', Reset(self.panel, self.arm, self.logger).execute),
                ('Disable Youpi', Disable(self.panel, self.arm, self.logger).execute),
                ('Shutdown', self.shutdown),
            ),
            exit_on=(Selector.ESC, self.SHUTDOWN, self.QUIT)
        )

    def display_about_modal(self):
        self.display_about()

    def shutdown(self):
        action = self.sublevel(
            title='Shutdown',
            choices=(
                ('Quit to shell', 'Q'),
                ('Reboot', 'R'),
                ('Power off', 'P'),
            ),
            exit_on=(Selector.ESC, 'Q', 'R', 'P')
        )

        if action == Selector.ESC:
            return

        elif action == 'Q':
            self.panel.clear()
            self.panel.write_at("I'll be back...")
            return self.QUIT

        elif action == 'R':
            self.panel.display_progress("Reboot")
            subprocess.call('sudo reboot', shell=True)
        elif action == 'P':
            self.panel.display_progress("Shutdown")
            subprocess.call('sudo poweroff', shell=True)

        return self.SHUTDOWN


def main():
    TopLevel().run()
