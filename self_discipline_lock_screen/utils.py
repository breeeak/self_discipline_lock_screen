# -*- coding: utf-8 -*-
# @Time    : 2022/1/6 13:53
# @Author  : Marshall
# @FileName: utils.py
import cv2
import dlib
from imutils import face_utils
from PIL import ImageGrab
import numpy as np


def face_detect():
    dnnFaceDetector = dlib.cnn_face_detection_model_v1("./model/mmod_human_face_detector.dat")
    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    for i in range(15):
        ret, img = video_capture.read()
    # img = cv2.imread('./log/2022-01-06/video_capture_15_09_56.png')
    video_capture.release()

    rects = dnnFaceDetector(img)
    have_face = False
    if len(rects) > 0:
        have_face = True
        for (i, rect) in enumerate(rects):
            x1 = rect.rect.left()
            y1 = rect.rect.top()
            x2 = rect.rect.right()
            y2 = rect.rect.bottom()
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
    return img, have_face


def screen_capture():
    im = ImageGrab.grab()
    img_np = np.array(im)
    img_np = cv2.cvtColor(np.array(img_np), cv2.COLOR_RGB2BGR)
    # cv2.imwrite("screenshot2.png", img_np)
    return img_np


def speech(reminder):
    import pyttsx3
    engine = pyttsx3.init()
    engine.say(reminder)
    engine.runAndWait()


if __name__ == '__main__':
    # img, have_face=face_detect()
    # print(have_face)
    face_detect()
