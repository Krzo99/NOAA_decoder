import zmq
import numpy as np
import cv2
import time

#  Settings
inBaud = 11025
imgWidth = 2080

date_string = time.strftime("%Y-%m-%d-%H_%M_%S")
windowName = date_string
OutImgPath = r"H:\Projects\NOAA_listener\out\\" + date_string + ".png"

#  GUI
cv2.namedWindow(windowName, cv2.WINDOW_AUTOSIZE)

# Data
Line = np.zeros((1, inBaud), dtype=np.uint8)
img = np.zeros((1, imgWidth), dtype=np.uint8)
LineIndex = 0
bEnd = False

#  Server
context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.connect("tcp://127.0.0.1:65443")

print("Server start!")

while not bEnd:
    #  Wait for next request from client
    try:
        # check for a message, this will not block
        message = socket.recv(flags=zmq.NOBLOCK)

        # a message has been received, Process data
        for i in message:
            Line[0][LineIndex] = i

            if LineIndex >= inBaud - 1:

                if Line.any():
                    resized_Line = cv2.resize(Line, (imgWidth, 1))
                    img = np.append(img, resized_Line, axis=0)

                    cv2.imwrite(OutImgPath, img)
                    cv2.imshow(windowName, img)

                    if cv2.waitKey(33) == ord('x'):
                        print("Decoding ended, Image saved to", OutImgPath)

                        cv2.imshow(windowName, img)
                        cv2.waitKey(0)

                        bEnd = True
                    print("Lines:", img.shape[0])
                Line.fill(0)
                LineIndex = 0
            else:
                LineIndex += 1

    except zmq.Again as e:
        pass


