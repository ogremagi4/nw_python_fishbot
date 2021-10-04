import cv2 as cv
import numpy as np
import os
from time import time
from windowcapture import WindowCapture
from detection import Detection
from vision import Vision
from fisher import Fisher




if __name__ == '__main__':
    wincap = WindowCapture('New World')
    detector = Detection()
    vision = Vision()
    fisher = Fisher()

    wincap.start()
    detector.start()
    fisher.start()


while(True):
    # if we don't have a screenshot yet, don't run the code below this point yet
    if wincap.screenshot is None:
        continue
    # give detector the current screenshot to search for objects in
    detector.update(wincap.screenshot)
    #pass state to fisher so it makes decisions
    fisher.update(detector.state)
