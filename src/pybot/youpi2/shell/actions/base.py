# -*- coding: utf-8 -*-

import shlex
import subprocess
import time

from pybot.core import log

from pybot.lcd.lcd_i2c import LCD03
from pybot.youpi2.ctlpanel import Keys
from pybot.youpi2.ctlpanel.widgets import CH_OK

__author__ = 'Eric Pascual'


class Action(log.LogMixin):
    """ Root class for actions. """
    def __init__(self, owner, parent_logger=None, log_level=None, **kwargs):
        """
        :param TopLevel owner: the top level of he application
        :param parent_logger: the (optional) parent logger
        :param log_level: the logging level (defaulted to parent's one or to INFO as fallback)
        :param kwargs: stored as underscore prefixed attributes
        """
        if log_level is None:
            if parent_logger:
                log_level = parent_logger.getEffectiveLevel()
            else:
                log_level = log.INFO

        log.LogMixin.__init__(self, parent=parent_logger, name=self.__class__.__name__, level=log_level)
        self.panel = owner.panel
        self.arm = owner.arm
        self.terminate_event = owner.terminate_event

        for k, v in kwargs.iteritems():
            setattr(self, '_' + k, v)

    def execute(self):
        raise NotImplementedError()

    def display_error(self, e):
        self.log_exception(e)

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

        # start the action as a child process
        try:
            cmde = self.COMMAND
            if self.log_getEffectiveLevel() == log.DEBUG:
                cmde += ' -v'
            self.log_info('starting "%s" as subprocess', cmde)
            app_proc = subprocess.Popen(shlex.split(cmde))
            self.log_info('PID=%d', app_proc.pid)

        except OSError as e:
            self.log_exception(e)

            self.panel.clear()
            self.panel.center_text_at("ERROR", line=1)
            msg = str(e)
            self.panel.write_at(msg[:20], line=3)
            self.panel.write_at(msg[20:40], line=4)
            self.panel.write_at(chr(LCD03.CH_OK), 1, self.panel.width)
            self.panel.wait_for_key(Keys.OK, blink=True)

        else:
            self.log_info('watching for keypad actions...')
            while not self.terminate_event.is_set():
                if app_proc.poll() is not None:
                    self.log_info('terminated with rc=%d', app_proc.returncode)
                    return

                keys = self.panel.get_keys()
                if keys == exit_key_combo:
                    self.log_info('exit action caught')
                    break

                time.sleep(0.2)

            # If here, either we got a shell termination signal or the exit combo has
            # been used. In either case we need to stop our child process and wait for
            # its termination.
            self.log_info('sending terminate signal to subprocess %d', app_proc.pid)
            app_proc.terminate()
            self.log_info('waiting for completion')
            app_proc.wait()
            self.log_info('terminated with rc=%d', app_proc.returncode)
