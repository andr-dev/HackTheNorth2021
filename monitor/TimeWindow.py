import time


class TimeWindow:
    def __init__(self, window_name, process_name, mouse_timeout):
        self.name = window_name
        self.process = process_name
        self.start_time = int(time.time())
        self.end_time = self.start_time + 1
        self.ended = False
        self.mouse_timeout = mouse_timeout

    def update_time_window(self):
        self.end_time = int(time.time())

    def can_be_updated(self):
        if int(time.time()) - self.end_time > self.mouse_timeout or self.ended:
            return False
        return True

    def finalize(self):
        if not self.ended:
            self.update_time_window()
            self.ended = True
            return self
        return False

    def __str__(self):
        return "Name: " + self.name + " Start: " + str(self.start_time) + " End: " + str(self.end_time) + " Ended: " + (
            "True" if self.ended else "False")
