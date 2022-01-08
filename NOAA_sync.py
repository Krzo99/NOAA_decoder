import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal


# Settings
sampleRate_l = 11025
vHi_l = 50
vLo_l = 35
minPoint_l = 1
maxPoint_l = 4
img_name = "2022-01-07-17_06.png"
img_l = cv2.imread("out/" + img_name)
outImgPath_l = r"H:\Projects\NOAA_listener\out\corrected" + img_name


def isNextPointSync(indexOfPrev, lookingFor, PandV, minInd, maxInd):
    if lookingFor == 1 and PandV[indexOfPrev+1] >= 0:
        dif = PandV[indexOfPrev+1] - -1*PandV[indexOfPrev]
        if minInd <= dif <= maxInd:
            return 1
    elif lookingFor == -1 and PandV[indexOfPrev+1] <= 0:
        dif = -1*PandV[indexOfPrev + 1] - PandV[indexOfPrev]
        if minInd <= dif <= maxInd:
            return 1
    return 0


def AlignWithSync(dataIn, line, vHi, vLo, minPoint, maxPoint, bIsRGB):

    # Find Peaks & valleys
    dataInSingle = dataIn[:, 0] if bIsRGB else dataIn
    peaks, _ = signal.find_peaks(dataInSingle, height=vHi)                  # local max
    valleys, _ = signal.find_peaks(dataInSingle * -1, height=-1 * vLo)      # local min

    # Add them to same array, faster computing
    peaksAndValleys = np.append(peaks, -1 * valleys, axis=0)
    peaksAndValleys = sorted(peaksAndValleys, key=lambda item: np.abs(item))

    # State machine
    state = 0
    startIndex = -1
    SyncsFound = []

    # We go over the whole line, and find sync bits
    for p in range(len(peaksAndValleys) - 1):

        if state % 2 == 0:
            if state == 0:
                if np.sign(peaksAndValleys[p]) == -1:
                    if isNextPointSync(p, 1, peaksAndValleys, minPoint, maxPoint):
                        state += 1
                        startIndex = -1 * peaksAndValleys[p]
            else:
                if isNextPointSync(p, 1, peaksAndValleys, minPoint, maxPoint):
                    state += 1
                else:
                    state = 0
        elif state % 2 == 1:
            if isNextPointSync(p, -1, peaksAndValleys, minPoint, maxPoint):
                state += 1
            else:
                state = 0

        # If Sync was found
        if state >= 12:
            SyncsFound.append((startIndex, peaksAndValleys[p], peaksAndValleys[p] - startIndex))
            # print("Sync found at line:", line, "at:", startIndex, "took:", peaksAndValleys[p] - startIndex, "samples")
            startIndex = -1
            state = 0

    # Sync of channel A is shorter
    ASync = -1
    if 0 < len(SyncsFound) <= 2:
        if len(SyncsFound) == 1:
            ASync = SyncsFound[0]
        else:
            ASync = SyncsFound[0] if SyncsFound[0][2] < SyncsFound[1][2] else SyncsFound[1]
    else:
        # print("Invalid number of Syncs found:", len(SyncsFound), "on line:", line)
        return None

    # We Align Image with sync
    multiPlier = -3 if bIsRGB else -1
    dataOut = np.roll(dataIn, multiPlier*ASync[0])
    return dataOut


def run(img, outImgPath, sampleRate, vHi, vLo, minPoint, maxPoint, bIsRGB):

    # We go over the image and fix each line
    outImg = img.copy()
    c = 0
    f = 0
    for i in range(outImg.shape[0]):
        data = outImg[i, :, :] if bIsRGB else outImg[i, :]

        fixed = AlignWithSync(data, i, vHi, vLo, minPoint, maxPoint, bIsRGB)

        if fixed is not None:
            if bIsRGB:
                outImg[i, :, :] = fixed
            else:
                outImg[i, :] = fixed
            c += 1
        else:
            f += 1

    print("c:", c, "f:", f, "Success:{:.2f}%".format(float(1-f/c)*100))

    cv2.imwrite(outImgPath, outImg)
    cv2.imshow('after', outImg)
    cv2.waitKey(0)


if __name__ == "__main__":
    run(img_l, outImgPath_l, sampleRate_l, vHi_l, vLo_l, minPoint_l, maxPoint_l, True)
