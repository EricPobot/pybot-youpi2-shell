# -*- coding: utf-8 -*-

import shlex
import subprocess
import time

from pybot.core import log

from pybot.lcd.lcd_i2c import LCD03
from pybot.youpi2.ctlpanel import Keys
from pybot.youpi2.ctlpanel.widgets import CH_OK

__author__ = 'Eric Pascual'


class Action(object):
    """ Root class for actions. """
    def __init__(self, panel, arm, terminate_event, parent_logger=None, **kwargs):
        self.panel = panel
        self.arm = arm
        self.terminate_event = terminate_event

        parent_logger = parent_logger or log.getLogger()
        self.logger = parent_logger.getChild(self.__class__.__name__)

        for k, v in kwargs.iteritems():
            setattr(self, '_' + k, v)

    def execute(self):
        raise NotImplementedError()

    def display_error(self, e):
        self.logger.exception(e)

        self.panel.reset()
        self.panel.center_text_at("Unexpected error", line=1)

        msg = e.message.strip().split('\n')[-1]
        self.panel.center_text_at(msg[:20], line=3)
        self.panel.center_text_at(msg[20:40], line=4)

        self.panel.write_at(chr(CH_OK), line=1, col=self.panel.width)
        self.panel.wait_for_key(Keys.OK, blink=True)


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
            self.logger.exception(e)

            self.panel.clear()
            self.panel.center_text_at("ERROR", line=1)
            msg = str(e)
            self.panel.write_at(msg[:20], line=3)
            self.panel.write_at(msg[20:40], line=4)
            self.panel.write_at(chr(LCD03.CH_OK), 1, self.panel.width)
            self.panel.wait_for_key(Keys.OK, blink=True)

        else:
            self.logger.info('watching for keypad actions...')
            while not self.terminate_event.is_set():
                if app_proc.poll() is not None:
                    self.logger.info('terminated with rc=%d', app_proc.returncode)
                    return

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
