import win32api, win32con
from threading import Thread, Lock
import random
from enum import Enum
import time

class FishingState(Enum):
    ROD_NOT_IN_HANDS = 0
    ROD_IN_HANDS = 1
    BOBBER_IS_STILL = 2
    GET_READY_TO_HOOK = 3
    SHOULD_BE_HOOKING = 4
    SHOULD_BE_REELING = 5
    SHOULD_NOT_BE_REELING = 6
    STOP_REELING = 7


class Fisher(Thread):

    state = None
    lock = Lock()
    stopped = False

    def __init__(self):
        super(Fisher,self).__init__(daemon=True)
        
    def update(self, state):
        self.lock.acquire()
        self.state = state
        self.lock.release()

    @staticmethod
    def leftClick(delay=round(random.uniform(0.5,1.0),2) ):
        # win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
        time.sleep(delay)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
    

    def hook(self):
        print('Hooking')
        self.leftClick(
            delay = round(random.uniform(0.1,0.2),2)
        )
        time.sleep(2)

    def throw_the_rod(self):
        print('Throwing the rod')
        self.leftClick(
            delay = round(random.uniform(2,4),2)
        )
        time.sleep(8)#sleep a bit so opencv will find bobber in the water and make sure we dont throw the rod again
    
    def reel(self):
        print('Reeling')
        self.leftClick(
            delay = round(random.uniform(0.1,0.5),2)
        )
    
    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            if self.state == FishingState.SHOULD_BE_HOOKING:
                self.hook()
            
            elif self.state == FishingState.GET_READY_TO_HOOK:
                time.sleep(0.5)
                self.hook()
                
            elif self.state == FishingState.SHOULD_BE_REELING:
                self.reel()
            
            elif self.state in [FishingState.SHOULD_NOT_BE_REELING, FishingState.STOP_REELING]:
                self.lock.acquire()
                time.sleep(round(random.uniform(0.1,0.5)))
                self.lock.release()

            elif self.state == FishingState.ROD_IN_HANDS:
                self.throw_the_rod()




        


        