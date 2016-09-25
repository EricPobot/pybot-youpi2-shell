# -*- coding: utf-8 -*-

from pybot.youpi2.model import YoupiArm
from pybot.youpi2.ctlpanel.widgets import CH_OK, CH_CANCEL
from pybot.youpi2.ctlpanel.keys import Keys

from .base import Action

__author__ = 'Eric Pascual'

_all__ = ['Reset', 'Disable']


class Calibrate(Action):
    def execute(self):
        # disable Youpi motors so that the arm can be placed near the home position manually
        self.arm.hard_hi_Z()

        self.panel.clear()

        self.panel.write_at(
            chr(CH_CANCEL) + "Calibration".center(self.panel.width - 2) + chr(CH_OK),
            line=1
        )
        self.panel.center_text_at("Put Youpi near", line=2)
        self.panel.center_text_at("home position", line=3)
        self.panel.center_text_at("OK:go - ESC:cancel", line=4)

        key = self.panel.wait_for_key([Keys.OK, Keys.ESC])
        self.panel.leds_off()

        if key == Keys.OK:
            try:
                self.panel.please_wait("Seeking origins")
                self.arm.seek_origins(YoupiArm.MOTORS_ALL)

                self.panel.please_wait("Calibrating gripper")
                self.arm.calibrate_gripper()
            except Exception as e:
                self.display_error(e)
            else:
                self.panel.display_splash(['', 'Complete.'])

        else:
            self.panel.display_splash(['', 'Aborted.'])


class Disable(Action):
    def execute(self):
        # disable Youpi motors
        self.arm.hard_hi_Z()

        self.panel.clear()
        self.panel.display_splash("""
            Youpi motors
            are disabled now.
        """)


class Initialize(Action):
    def execute(self):
        self.arm.initialize()

        self.panel.clear()
        self.panel.display_splash("""
            Arm reinitialized.
        """)
