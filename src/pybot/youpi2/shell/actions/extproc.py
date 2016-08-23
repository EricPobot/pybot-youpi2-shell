# -*- coding: utf-8 -*-

import time
import subprocess
import shlex

from pybot.lcd.lcd_i2c import LCD03

from pybot.youpi2.ctlpanel import Keys
from . import Action

__author__ = 'Eric Pascual'


class ExternalProcessAction(Action):
    COMMAND = None
    TITLE = None

    def execute(self):
        exit_key_combo = {Keys.ESC, Keys.OK}

        self.panel.clear()
        self.panel.center_text_at(self.TITLE, line=2)

        self.panel.clear_was_locked_status()
        self.panel.exit_key_message(msg="%(key)s key to kill", keys=exit_key_combo)
        time.sleep(3)
        self.panel.leds_off()

        # start the demonstration as a child process
        try:
            self.logger.info('starting "%s" as subprocess', self.COMMAND)
            app_proc = subprocess.Popen(shlex.split(self.COMMAND))
            self.logger.info('PID=%d', app_proc.pid)

        except OSError as e:
            self.panel.clear()
            self.panel.center_text_at("ERROR", line=1)
            msg = str(e)
            self.panel.write_at(msg[:20], line=3)
            self.panel.write_at(msg[20:40], line=4)
            self.panel.write_at(chr(LCD03.CH_OK), 1, self.panel.width)
            self.panel.wait_for_key([Keys.OK])

        else:
            self.logger.info('watching for keypad actions...')
            while True:
                keys = self.panel.get_keys()
                if keys == exit_key_combo:
                    self.logger.info('exit action caught')
                    self.logger.info('sending terminate signal to subprocess %d', app_proc.pid)
                    app_proc.terminate()
                    self.logger.info('waiting for completion')
                    app_proc.wait()
                    self.logger.info('terminated with rc=%d', app_proc.returncode)
                    return

                time.sleep(0.2)


class MinitelUi(ExternalProcessAction):
    COMMAND = "youpi2-minitel"
    TITLE = "Minitel control mode"


class GamepadControl(ExternalProcessAction):
    COMMAND = "youpi2-gamepad"
    TITLE = "Gamepad control mode"


class WebServicesControl(ExternalProcessAction):
    COMMAND = "youpi2-ws"
    TITLE = "Web Services mode"


class BrowserlUi(ExternalProcessAction):
    COMMAND = "youpi2-browser"
    TITLE = "Web Services mode"


class DemoAuto(ExternalProcessAction):
    COMMAND = "youpi2-demo-auto --pnldev /mnt/lcdfs"
    TITLE = "Automatic demo mode"
