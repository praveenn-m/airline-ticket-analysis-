import cv2 as cv
import numpy as np
import module as htm
import time
import autopy

wCam, hCam = 1280, 720
frameR = 100

cap = cv.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
detector = htm.handDetector(maxHands=1)
screen_size = autopy.screen.size()

# Unpack the screen size
wScr, hScr = screen_size

while True:
    # 1
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img)

    #2
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        #3
        fingers = detector.fingersUP()
        #print(fingers)
        cv.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 0), 2)
        #4
        if len(fingers) > 2:
            if fingers[1] == 1 and fingers[2] == 1:

                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

                autopy.mouse.move(int(wScr-x3), int(y3))
                cv.circle(img, (x1, y1), 15, (255, 0, 255), cv.FILLED)
    else:
        cv.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 0), 2)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv.putText(img, f'FPS:{int(fps)}', (400, 70), cv.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    cv.imshow("img", img)
    key = cv.waitKey(1) & 0xFF
    if key == ord('q') or key == ord(' '):
        break

cap.release()
cv.destroyAllWindows()
