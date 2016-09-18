# -*- coding: utf-8 -*-

from pybot.youpi2.shell.actions.base import ExternalProcessAction

__author__ = 'Eric Pascual'

__all__ = ['MinitelUi', 'GamepadControl', 'WebServicesControl', 'BrowserlUi', 'DemoAuto']

BIN_PATH = '/home/pi/.local/bin/'


class MinitelUi(ExternalProcessAction):
    COMMAND = BIN_PATH + "youpi2-minitel"
    TITLE = "Minitel control mode"


class GamepadControl(ExternalProcessAction):
    COMMAND = BIN_PATH + "youpi2-gamepad"
    TITLE = "Gamepad control mode"


class WebServicesControl(ExternalProcessAction):
    COMMAND = BIN_PATH + "youpi2-restapi"
    TITLE = "Web Services mode"


class BrowserlUi(ExternalProcessAction):
    COMMAND = BIN_PATH + "youpi2-browser"
    TITLE = "Web Services mode"


class DemoAuto(ExternalProcessAction):
    COMMAND = BIN_PATH + "youpi2-demo-auto"
    TITLE = "Automatic demo mode"
