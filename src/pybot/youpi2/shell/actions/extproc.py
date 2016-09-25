# -*- coding: utf-8 -*-

from pybot.youpi2.shell.actions.base import ExternalProcessAction

__author__ = 'Eric Pascual'

__all__ = ['MinitelUi', 'GamepadControl', 'HttpServer', 'DemoAuto', 'HanoiTowersDemo']

BIN_PATH = '/home/pi/.local/bin/'


class MinitelUi(ExternalProcessAction):
    COMMAND = BIN_PATH + "youpi2-minitel"
    TITLE = "Minitel control mode"


class GamepadControl(ExternalProcessAction):
    COMMAND = BIN_PATH + "youpi2-gamepad"
    TITLE = "Gamepad control mode"


class HttpServer(ExternalProcessAction):
    COMMAND = BIN_PATH + "youpi2-http-server"
    TITLE = "HTTP Server mode"


class DemoAuto(ExternalProcessAction):
    COMMAND = BIN_PATH + "youpi2-demo-auto"
    TITLE = "Automatic demo mode"


class HanoiTowersDemo(ExternalProcessAction):
    COMMAND = BIN_PATH + "youpi2-hanoi"
    TITLE = "Hanoi towers demo"
