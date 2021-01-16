#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 22:47:45 2021

@author: Elva
"""

import schedule
import time
import sys
from pynput.mouse import Controller
import time


class TW:
    def __init__(self, window_name):
        self.name = window_name
        self.start_time = int(time.time())
        self.end_time = self.start_time + 1000
        self.ended = False

    def update_TW(self):
        self.end_time = int(time.time())

    def can_be_updated(self):
        if (int(time.time()) - self.end_time > 5 or self.ended):
            return False
        return True

    def finalize(self):
        if not self.ended:
            self.update_TW()
            self.ended = True

    def __str__(self):
        return "Name: " + self.name + " Start: " + str(self.start_time) + " End: " + str(self.end_time) + " Ended: " + ("True" if self.ended else "False")

class Calculator:
    def __init__(self):
        self.last_mousex = 0
        self.last_mousey = 0
        self.last_window_name = ""
        self.time_window = []
        self.mouse_counter = 0

    def get_mouse_pos(self):
        mouse = Controller()
        return mouse.position

    def get_active_window(self):
        active_window_name = None
        if sys.platform in ['Windows', 'win32', 'cygwin']:
            import win32gui
            window = win32gui.GetForegroundWindow()
            active_window_name = win32gui.GetWindowText(window)
        elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
            from AppKit import NSWorkspace
            from Quartz import (
                CGWindowListCopyWindowInfo,
                kCGWindowListOptionOnScreenOnly,
                kCGNullWindowID
            )
            curr_pid = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationProcessIdentifier']
            options = kCGWindowListOptionOnScreenOnly
            windowList = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
            for window in windowList:
                pid = window['kCGWindowOwnerPID']
                ownerName = window['kCGWindowOwnerName']
                windowTitle = window.get('kCGWindowName', u'Unknown')
                if curr_pid == pid:
                    title = windowTitle.encode('ascii', 'ignore')
                    active_window_name = str(title)[2:len(str(title)) - 1] + " - " + str(ownerName)
        return active_window_name

    def in_bypassed_window(self, window):
        return False

    def update_time_window(self):
        print("Active window: %s" % str(self.get_active_window()))
        window_name = str(self.get_active_window())

        (x, y) = self.get_mouse_pos()
        if not self.in_bypassed_window(window_name):
            if x != self.last_mousex or y != self.last_mousey:
                self.mouse_counter = 0
                self.last_mousex = x
                self.last_mousey = y
            else:
                self.mouse_counter += 1
        if self.mouse_counter < 5:
            if len(self.time_window) == 0:
                self.time_window.append(TW(window_name))
            else:
                if window_name == self.last_window_name and self.time_window[len(self.time_window) - 1].can_be_updated():
                    self.time_window[len(self.time_window) - 1].update_TW()
                else:
                    self.time_window[len(self.time_window) - 1].finalize()
                    self.time_window.append(TW(window_name))
        else:
            self.time_window[len(self.time_window) - 1].finalize()

        self.last_window_name = window_name
        return

    def print_time_window(self):
        print("calc: [")
        for tw in self.time_window:
            print(tw)
        print("]")

calc = Calculator()
schedule.every(1).seconds.do(lambda: calc.update_time_window())
schedule.every(10).seconds.do(lambda: calc.print_time_window())

while 1:
    schedule.run_pending()
    time.sleep(1)