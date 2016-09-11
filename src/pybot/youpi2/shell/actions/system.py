# -*- coding: utf-8 -*-

from pybot.youpi2.model import YoupiArm

from .base import Action

__author__ = 'Eric Pascual'

_all__ = ['Reset', 'Disable']


class Calibrate(Action):
    def execute(self):
        # disable Youpi motors so that the arm can be placed near the home position manually
        self.arm.hard_hi_Z()

        self.panel.clear()
        self.panel.display_splash(
            """Place Youpi near
            its home position,
            then press a button.
        """, delay=0)
        self.panel.wait_for_key()
        self.panel.leds_off()

        try:
            self.panel.please_wait("Seeking origins")
            self.arm.seek_origins(YoupiArm.MOTORS_ALL, timeout=YoupiArm.TimeOuts.DEFAULT * YoupiArm.MOTORS_COUNT)

            self.panel.please_wait("Calibrating gripper")
            self.arm.calibrate_gripper(True, timeout=YoupiArm.TimeOuts.CALIBRATE_GRIPPER)
        except Exception as e:
            self.display_error(e)
        else:
            self.panel.display_splash('Complete.')


class Disable(Action):
    def execute(self):
        # disable Youpi motors
        self.arm.hard_hi_Z()

        self.panel.clear()
        self.panel.display_splash("""
            Youpi motors
            are disabled now.
        """)
