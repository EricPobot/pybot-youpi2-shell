# -*- coding: utf-8 -*-

from pybot.youpi2.shell.actions.base import ExternalProcessAction

__author__ = 'Eric Pascual'

__all__ = ['MinitelUi', 'GamepadControl', 'WebServicesControl', 'BrowserlUi', 'DemoAuto']


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
    COMMAND = "/home/pi/.local/bin/youpi2-demo-auto"
    TITLE = "Automatic demo mode"
