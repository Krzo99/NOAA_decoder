import zmq
import numpy as np
import cv2
from PyQt5.QtWidgets import QApplication, QLabel

#  Settings
width = 2080
windowName = "NOAA decoder"
OutimgPath = r'H:\Projects\MeteorM2 listener\GNURadio\outImg.png'

#  GUI
cv2.namedWindow(windowName, cv2.WINDOW_AUTOSIZE)

Line = np.zeros((1, width), dtype=np.uint8)
img = np.zeros((1, width), dtype=np.uint8)
LineIndex = 0


#  Server
context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.connect("tcp://127.0.0.1:65443")

print("Server start!")

while True:
    #  Wait for next request from client
    try:
        # check for a message, this will not block
        message = socket.recv(flags=zmq.NOBLOCK)

        # a message has been received, Process data
        for i in message:

            Line[0][LineIndex] = i
            if LineIndex >= 2079:
                img = np.append(img, Line, axis=0)
                Line.fill(0)
                LineIndex = 0

                cv2.imwrite(OutimgPath, img)
                cv2.imshow(windowName, img)
                cv2.waitKey(1)
                print(img.shape[0])
            else:
                LineIndex += 1

    except zmq.Again as e:
        pass

    #  Do some 'work'
    #time.sleep(1)

    #  Send reply back to client
    #socket.send(b"World")


