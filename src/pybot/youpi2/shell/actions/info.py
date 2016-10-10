# -*- coding: utf-8 -*-

import subprocess
import socket

from pybot.youpi2.ctlpanel import Keys
from pybot.youpi2.ctlpanel.widgets import CH_OK
from .base import Action

__author__ = 'Eric Pascual'

__all__ = ['DisplayAbout', 'DisplaySystemInfo']


class DisplayAbout(Action):
    _version = 'none'
    _long_text = False

    def execute(self):
        text = [
            "Youpi 2.0 Shell",
            "by POBOT",
            "",
            "version %(version)s" % {
                'version': self._version.split('+')[0]
            }
        ]
        if self._long_text:
            text += [
                "",
                "Powered by",
                "RaspberryPi 3",
                "",
                "6 STMicro L6470",
                "Stepper motor",
                "drivers inside",
                "",
                "100% Python software",
                "",
                "Embedded Web server",
                "based on Bottle",
                "",
                "designed, built and",
                "developped by",
                "E. PASCUAL",
            ]

        self.panel.scroll_text(text, from_bottom=False)


class DisplaySystemInfo(Action):
    def execute(self):
        self.panel.clear()
        self.panel.center_text_at('System info', line=1)

        self.panel.write_at('host:' + socket.gethostname(), line=2)

        out = subprocess.check_output("ip -4 -o addr".split(), bufsize=-1)
        y_pos = 3
        for line in out.strip().split('\n'):
            _, ifname, tail = line.strip().split(' ', 2)
            if ifname.startswith('eth') or ifname.startswith('wlan'):
                _, addr, _ = tail.strip().split(' ', 2)
                self.panel.write_at("%s:%s" % (ifname.strip(), addr.split('/')[0]), line=y_pos)
                y_pos += 1
                if y_pos > self.panel.height:
                    break

        self.panel.write_at(chr(CH_OK), line=1, col=self.panel.width)
        self.panel.wait_for_key(Keys.OK)
