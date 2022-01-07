import numpy
import scipy.io.wavfile as wav
import scipy.signal
import scipy.signal as signal
import numpy as np
from scipy.fft import fft, fftfreq
import sys
from PIL import Image
import cv2
import matplotlib.pyplot as plt


#def sync_corrected(img):


def hilbert(d):
    analytical_signal = signal.hilbert(d)
    amplitude_envelope = np.abs(analytical_signal)
    return amplitude_envelope


# Settings

# Type of data. Contrast is used in float, norm (more = less contrast) in int16
bIsFloatIEEE = True
bIs2Channel = True
contrast = 500
norm = 50

# Signal
bResample = True
BaudRate = 4160
SampleRate = 4*BaudRate


# Should full file be rendered?
bFullFile = True
startSec = 30
endSec = 40

# Include file
#fs, data = wav.read('test/SDRSharp_20211231_085914Z_137915100Hz_IQ.wav')
#fs, data = wav.read('test/SDRSharp_20211231_090237Z_137914500Hz_IQ.wav')
#fs, data = wav.read('data/good_og.wav')
fs, data = wav.read('data/good_og.wav')

length = data.shape[0]//fs
dif = data.shape[0] - length*fs
data = data[:-1*dif]

if bIsFloatIEEE:
    data = data*contrast
else:
    data = data // norm
if not bFullFile:
    data = data[startSec*fs:endSec*fs]
if bIs2Channel:
    data = data[:, 0]
if bResample:
    data = signal.resample(data, SampleRate*length)
    fs = SampleRate

# Peak detector
data_am = hilbert(data)

# Draw Img
frame_width = int(fs*0.5)
w, h = frame_width, data_am.shape[0]//frame_width

img_arj = data_am.copy()
img_arj[img_arj > 255] = 255
img_arj[img_arj < 0] = 0

if img_arj.shape[0] != w*h:
    img_arj = img_arj[:-1*(img_arj.shape[0]-w*h)]

#img_arj = sync_corrected(img_arj)

img_arj = img_arj.reshape((h, w))
img_arj = img_arj.astype(np.uint8)

# Render with OpenCV
cv2.startWindowThread()
resized_image = cv2.resize(img_arj, (BaudRate//2, h))
cv2.imshow('NOAA', resized_image)
cv2.imwrite("out.png", resized_image)
cv2.waitKey(0)




'''
# Manual image mode, bad
#image = Image.new('RGB', (w, h), 0x000000)
img_data = np.zeros((h, w, 3), dtype=np.uint8)

px, py = 0, 0
for p in range(0, data_am.shape[0]):
    lum = int(data_am[p])
    if bIsFloatIEEE:
        lum = int(data_am[p])
    if lum < 0: lum = 0
    if lum > 255: lum = 255
    img_data[py][px] = lum
    px += 1
    if px >= w:
        if (py % 50) == 0:
            print(f"Line saved {py} of {h}")
        px = 0
        py += 1
        if py >= h:
            break

plt.imshow(img_data, aspect="auto")
plt.show()
#image = image.resize((w, 4*h))
#plt.imshow(image)
#plt.show()'''