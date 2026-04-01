import cv2 as cv
import time
import os
import module as htm

wCam, hCam = 1280, 720

cap = cv.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector()

tipIds = [4, 8, 12, 16, 20]

folderPath = "imgs"
myList = os.listdir(folderPath)
print(myList)
overlayList = []
for imPath in myList:
    image = cv.imread(f'{folderPath}/{imPath}')
    #print(f'{folderPath}/{imPath}')
    overlayList.append(image)


while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    handType = detector.getHandType()
    #print(lmList)

    if len(lmList) != 0:
        fingers = []
        
        # Get hand type (Left or Right)
        if handType == "Right":
            # Right hand: thumb is on the right side
            if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        else:
            # Left hand: thumb is on the left side (inverted logic)
            if lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

        for id in range(1,5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
           # print(fingers)

        totalfingers = fingers.count(1)
        print(f"Hand: {handType}, Fingers: {totalfingers}")

        h, w, c = overlayList[0].shape
        img[0:h, 0:w] = overlayList[totalfingers-1]

        cv.rectangle(img, (20,225), (170,425), (0, 255, 0), cv.FILLED)
        cv.putText(img, str(totalfingers), (45,375), cv.FONT_HERSHEY_PLAIN, 10, (255, 0, 0), 25)
        cv.putText(img, f"Hand: {handType}", (20, 200), cv.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv.putText(img, f'FPS:{int(fps)}', (400, 70), cv.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    cv.imshow("image", img)
    if cv.waitKey(10) & 0xFF == ord('q'):
        break
