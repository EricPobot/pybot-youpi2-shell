# -*- coding: utf-8 -*-

from pybot.youpi2.model import YoupiArm

from .base import Action

__author__ = 'Eric Pascual'

_all__ = ['Reset', 'Disable']


class Reset(Action):
    def execute(self):
        # disable Youpi motors
        self.arm.hard_hi_Z()

        self.panel.clear()
        self.panel.display_splash(
            """Place Youpi in
            home position, then
            press a button.
        """, delay=0)
        self.panel.wait_for_key()
        self.panel.leds_off()

        self.panel.display_splash("Seeking origins\n...", delay=0)
        self.arm.seek_origins(YoupiArm.MOTORS_ALL)

        self.panel.display_splash("Calibrating gripper\n...", delay=0)
        self.arm.calibrate_gripper(wait=True)

        self.panel.display_splash('Complete.')


class Disable(Action):
    def execute(self):
        # disable Youpi motors
        self.arm.hard_hi_Z()

        self.panel.clear()
        self.panel.display_splash("""
            Youpi motors
            are disabled
        """)
