import zmq
import numpy as np
import cv2
import time
import NOAA_sync

#  Settings
sampleRate = 11025
imgWidth = 2080

date_string = time.strftime("%Y-%m-%d-%H_%M_%S")
windowName = date_string
OutImgPath = r"H:\Projects\NOAA_listener\out\raw" + date_string + ".png"
CorrectedOutPath = r"H:\Projects\NOAA_listener\out\corrected" + date_string + ".png"

# Corrected Img Settings
vHi = 50
vLo = 35
minPointsBetweenSync = 1
maxPointsBetweenSync = 4

#  GUI
cv2.namedWindow(windowName, cv2.WINDOW_AUTOSIZE)

# Data
Line = np.zeros((1, sampleRate), dtype=np.uint8)
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

            if LineIndex >= sampleRate - 1:

                if Line.any():
                    resized_Line = cv2.resize(Line, (imgWidth, 1))
                    img = np.append(img, resized_Line, axis=0)

                    cv2.imwrite(OutImgPath, img)

                    # Ready for display
                    displayedImg = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
                    cv2.imshow(windowName, displayedImg)

                    if cv2.waitKey(33) == ord('x'):
                        print("Decoding ended, Raw image saved to", OutImgPath)
                        print("Trying to align syncs...")
                        NOAA_sync.run(img, OutImgPath, sampleRate, vHi, vLo, minPointsBetweenSync, maxPointsBetweenSync, False)

                        #displayedImg = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
                        #cv2.imshow(windowName, displayedImg)
                        #cv2.waitKey(0)

                        bEnd = True
                        break

                    print("Lines:", img.shape[0])
                Line.fill(0)
                LineIndex = 0
            else:
                LineIndex += 1

    except zmq.Again as e:
        pass


