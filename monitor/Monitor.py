"""
Created on Sat Jan 16 22:47:45 2021

@author: Elva Shang
"""

# import schedule
import sys
from pynput.mouse import Controller
import time

from monitor.TimeWindow import TimeWindow


class Monitor:
    def __init__(self, mouse_timeout):
        self.last_mousex = 0
        self.last_mousey = 0
        self.last_window_name = ""
        self.time_window = []
        self.mouse_counter = 0
        self.mouse_timeout = mouse_timeout

    # def start_schedule(self):
    #     schedule.every(1).seconds.do(lambda: self.update_time_window())
    #     schedule.every(10).seconds.do(lambda: self.print_time_window())
    #
    #     while 1:
    #         schedule.run_pending()
    #         time.sleep(1)

    def get_mouse_pos(self):
        mouse = Controller()
        return mouse.position

    def get_active_window(self):
        active_window_name = (None, None)
        if sys.platform in ['Windows', 'win32', 'cygwin']:
            import win32gui
            import psutil
            import win32process
            window = win32gui.GetForegroundWindow()
            pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
            psutil.Process(pid[-1]).name()
            active_window_name = (win32gui.GetWindowText(window), psutil.Process(pid[-1]).name())

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
                    active_window_name = (str(title)[2:len(str(title)) - 1] + " - " + str(ownerName), "")
        return active_window_name

    def update_time_window(self):
        # print("Active window: %s" % str(self.get_active_window()))
        (window_name, process_name) = self.get_active_window()
        print(window_name)
        print(process_name)

        out = False

        (x, y) = self.get_mouse_pos()
        if not Monitor.in_bypassed_window(window_name):
            if x != self.last_mousex or y != self.last_mousey:
                self.mouse_counter = 0
                self.last_mousex = x
                self.last_mousey = y
            else:
                self.mouse_counter += 1
        if self.mouse_counter < self.mouse_timeout:
            if len(self.time_window) == 0:
                self.time_window.append(TimeWindow(window_name, process_name, self.mouse_timeout))
            else:
                if window_name == self.last_window_name and self.time_window[len(self.time_window) - 1].can_be_updated():
                    self.time_window[len(self.time_window) - 1].update_time_window()
                else:
                    out = self.finalize()
                    self.time_window.append(TimeWindow(window_name, process_name, self.mouse_timeout))
        else:
            out = self.finalize()

        self.last_window_name = window_name
        return out

    @staticmethod
    def in_bypassed_window(window):
        if window == "Zoom":
            return True
        return False

    def finalize(self):
        return self.time_window[len(self.time_window) - 1].finalize()

    def print_time_window(self):
        print("calc: [")
        for tw in self.time_window:
            print(tw)
        print("]")
