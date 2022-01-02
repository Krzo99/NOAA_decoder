import numpy
import scipy.io.wavfile as wav
import scipy.signal as signal
import numpy as np
from scipy.fft import fft, fftfreq
import sys
from PIL import Image
import cv2
import matplotlib.pyplot as plt


def hilbert(d):
    analytical_signal = signal.hilbert(d)
    amplitude_envelope = np.abs(analytical_signal)
    return amplitude_envelope


# Settings
contrast = 500
bFullFile = True
startSec = 30
endSec = 40
BaudRate = 4160
SampleRate = 4*BaudRate
bIsFloatIEEE = True

#fs, data = wav.read('test/SDRSharp_20211231_085914Z_137915100Hz_IQ.wav')
#fs, data = wav.read('test/SDRSharp_20211231_090237Z_137914500Hz_IQ.wav')
fs, data = wav.read('test/good_onlyReal.wav')

length = data.shape[0]//fs
dif = data.shape[0] - length*fs
data = data[:-1*dif]

if bIsFloatIEEE:
    data = data*contrast
if not bFullFile:
    data = data[startSec*fs:endSec*fs]
#data = data[:, 0]

data = signal.resample(data, SampleRate*length) #2*BaudRate
fs = SampleRate

# Filtering
freq = BaudRate/fs/2
sos = signal.butter(10, freq, analog=False, output='sos')

#w, h = signal.sosfreqz(sos)
#db = 20*np.log10(np.maximum(np.abs(h), 1e-5))
#plt.plot(w/np.pi, db)
#plt.show()

filteredData = signal.sosfilt(sos, data)

# FFT
#xf = fftfreq(fs, 1/fs)[:fs//2]
#yf = fft(data)

#plt.plot(xf, 1/fs * np.abs(yf[0:fs//2]))
#plt.grid()
#plt.show()

# Peak detector
data_am = hilbert(filteredData)

# Draw Img
frame_width = int(fs*0.5)
w, h = BaudRate//2, data_am.shape[0]//frame_width

img_arj = signal.resample(data_am, BaudRate*length)
img_arj[img_arj > 255] = 255
img_arj[img_arj < 0] = 0

img_arj = img_arj.reshape((h, w))
img_arj = img_arj.astype(np.uint8)

#img = Image.fromarray(img_arj, 'L')
#img.show()

# With OpenCV
cv2.startWindowThread()
cv2.imshow('NOAA', img_arj)
cv2.waitKey(0)



'''
# Manual image mode, bad
image = Image.new('RGB', (w, h), 0x000000)

px, py = 0, 0
for p in range(0, data_am.shape[0], int(SampleRate/BaudRate)):
    lum = int(data_am[p] / 16)
    if bIsFloatIEEE:
        lum = int(data_am[p])
    if lum < 0: lum = 0
    if lum > 255: lum = 255
    image.putpixel((px, py), (0, lum, 0))
    px += 1
    if px >= w:
        if (py % 50) == 0:
            print(f"Line saved {py} of {h}")
        px = 0
        py += 1
        if py >= h:
            break

image = image.resize((w, 4*h))
plt.imshow(image)
plt.show()'''