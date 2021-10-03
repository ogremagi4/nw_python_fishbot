import win32api, win32con
from threading import Thread, Lock
import random

class Clicker:

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True
    
    def leftClick(self, x=0,y=0, delay=round(random.uniform(0.5,1.0),2) ):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
        time.sleep(delay)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
