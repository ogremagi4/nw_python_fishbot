import cv2 as cv
from threading import Thread, Lock
from enum import Enum
import numpy as np
import os
import time
from fisher import FishingState
from collections import OrderedDict
from queue import Queue


IMAGES_DIR = 'images'

class Detection:

    # threading properties
    stopped = True
    lock = None
    rectangles = []
    # properties
    cascade = None
    screenshot = None

    def __init__(self):
        # create a thread lock object
        self.lock = Lock()
        # load the trained model
        self.state = None
        self.rectangles = []
        self.states_queue = Queue(maxsize=5)#store states in queue to refresh the state in case the bot gets stuck

        self.states_map = {
            FishingState.SHOULD_BE_HOOKING : self.imread('hook_2.jpg'),
            FishingState.SHOULD_NOT_BE_REELING : self.imread('should_not_be_reeling.jpg'),
            FishingState.STOP_REELING: self.imread('stop_reeling_2.jpg'),
            FishingState.SHOULD_BE_REELING : self.imread('pull_2.jpg'),
            FishingState.BOBBER_IS_STILL : self.imread('waiting_for_fish.jpg'),
            FishingState.ROD_IN_HANDS : self.imread('nail.jpg'),
            FishingState.GET_READY_TO_HOOK : self.imread('get_ready_to_hook.jpg')
        }

            
        

    @staticmethod
    def imread(img_name, mode=cv.IMREAD_UNCHANGED):
        return cv.imread(
            os.path.join(IMAGES_DIR, img_name), 
            mode
        )

    def find(self, haystack, needle, threshold = 0.75):
        result = cv.matchTemplate(haystack, needle, cv.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))

        needle_w, needle_h, needle_d = needle.shape

        rects = [[int(loc[0]), int(loc[1]), needle_w, needle_h] for loc in locations]

        #draw it
        line_color = (0, 255, 0)#green
        line_type = cv.LINE_4

        return rects
    
    

    def update(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        # TODO: you can write your own time/iterations calculation to determine how fast this is
        while not self.stopped:
            if not self.screenshot is None:
                # do object detection
                #either find nothing, a bobber, a hook indicator, a fishing indicator
                image_found=False

                if self.states_queue.full():     
                    last_states = [self.states_queue.get() for _ in range(self.states_queue.qsize())]
                    if len(set(last_states)) == 1:
                        states_to_check = [
                            state for state in FishingState if not state == FishingState.ROD_NOT_IN_HANDS
                        ]
                else:
                    states_to_check = []
                    if self.state == FishingState.BOBBER_IS_STILL:
                        states_to_check = [
                            FishingState.SHOULD_BE_HOOKING, 
                            FishingState.GET_READY_TO_HOOK, 
                            FishingState.ROD_IN_HANDS]
                    elif self.state == FishingState.GET_READY_TO_HOOK:
                        states_to_check = [FishingState.SHOULD_BE_HOOKING, FishingState.SHOULD_BE_REELING, FishingState.ROD_IN_HANDS]
                    elif self.state in [FishingState.SHOULD_BE_HOOKING]:
                        states_to_check = [FishingState.SHOULD_BE_REELING]
                    elif self.state in [FishingState.SHOULD_BE_REELING, FishingState.STOP_REELING, FishingState.SHOULD_NOT_BE_REELING]:
                        states_to_check = [
                            FishingState.STOP_REELING,
                            FishingState.SHOULD_NOT_BE_REELING,
                            FishingState.SHOULD_BE_REELING
                        ]
                    else:
                        states_to_check = [
                            FishingState.BOBBER_IS_STILL,
                            FishingState.ROD_IN_HANDS
                        ]

                for state in states_to_check:
                    rectangles = self.find(self.screenshot, self.states_map[state])
                    if rectangles:
                        image_found = True
                        self.state, self.rectangles = state, rectangles
                        break

                self.states_queue.put(self.state)

                print(f'{self.state}')
                self.rectangles = rectangles
            # lock the thread while updating the results
