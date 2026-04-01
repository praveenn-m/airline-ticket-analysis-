import cv2 as cv
import numpy as np
import os
import module as htm

brushThickness = 15
eraserThickness = 150

folderPath = "images"
myList = os.listdir(folderPath)
print(myList)

overlayList = []
for imPath in myList:
    image = cv.imread(f'{folderPath}/{imPath}')
    if image is not None:
        # Resize image to match header dimensions (125 height x 1280 width)
        image = cv.resize(image, (1280, 125))
    overlayList.append(image)

print(len(overlayList))
if len(overlayList) > 0:
    images = overlayList[0]
else:
    print("Error: No images found in 'images' folder")
    exit()
drawColor = (255, 0, 255)

cap = cv.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = htm.handDetector(detectionCon=0.85)
xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

# Finger tip IDs: 4=Thumb, 8=Index, 12=Middle, 16=Ring, 20=Pinky
fingerTips = [4, 8, 12, 16, 20]
fingerNames = ["Thumb", "Index", "Middle", "Ring", "Pinky"]

while True:
    # 1. import image
    success, img = cap.read()
    img = cv.flip(img, 1)

    # 2. find hand landmarks
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # Draw all finger positions on screen
        for i, tipId in enumerate(fingerTips):
            if tipId < len(lmList):
                x, y = lmList[tipId][1], lmList[tipId][2]
                # Draw circle for each finger tip
                cv.circle(img, (x, y), 8, (0, 255, 255), cv.FILLED)
                # Draw finger name
                cv.putText(img, fingerNames[i], (x + 10, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        x1, y1 = lmList[8][1:]  # Index finger
        x2, y2 = lmList[12][1:]  # Middle finger
        
        # 3. check which fingers are up
        fingers = detector.fingersUP()
        
        # Display status of each finger
        status_y = 100
        for i, finger_up in enumerate(fingers):
            status = "UP" if finger_up else "DOWN"
            color = (0, 255, 0) if finger_up else (0, 0, 255)
            cv.putText(img, f"{fingerNames[i]}: {status}", (10, status_y), cv.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            status_y += 30

        # Check gesture conditions
        index_up = len(fingers) > 1 and fingers[1]
        middle_up = len(fingers) > 2 and fingers[2]
        
        # 4. If selection mode - two fingers are up in header area
        if index_up and middle_up and y1 < 125:
            xp, yp = 0, 0
            cv.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv.FILLED)
            cv.putText(img, "SELECTION MODE", (10, 70), cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            
            if 250 < x1 < 450 and len(overlayList) > 0:
                images = overlayList[0]
                drawColor = (255, 0, 255)
            elif 550 < x1 < 750 and len(overlayList) > 1:
                images = overlayList[1]
                drawColor = (0, 0, 255)
            elif 800 < x1 < 950 and len(overlayList) > 2:
                images = overlayList[2]
                drawColor = (255, 0, 0)
            elif 1050 < x1 < 1200 and len(overlayList) > 3:
                images = overlayList[3]
                drawColor = (0, 255, 0)
            elif 1200 < x1 < 1280 and len(overlayList) > 4:
                images = overlayList[4]
                drawColor = (0, 0, 0)

        # 5. If Eraser mode - Index and Middle fingers are up
        elif index_up and middle_up:
            cv.circle(img, (x1, y1), 15, (0, 0, 255), cv.FILLED)
            cv.putText(img, "ERASER MODE", (10, 70), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            cv.line(imgCanvas, (xp, yp), (x1, y1), (0, 0, 0), eraserThickness)
            xp, yp = x1, y1

        # 6. If Drawing mode - Only Index Finger is up
        elif index_up and not middle_up:
            cv.circle(img, (x1, y1), 15, (0, 255, 0), cv.FILLED)
            cv.putText(img, "DRAWING MODE", (10, 70), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            cv.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
            cv.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)
            xp, yp = x1, y1
        
        else:
            xp, yp = 0, 0

    # Blend canvas with camera feed - drawings persist until erased
    imgGray = cv.cvtColor(imgCanvas, cv.COLOR_BGR2GRAY)
    _, imgInv = cv.threshold(imgGray, 50, 255, cv.THRESH_BINARY_INV)
    imgInv = cv.cvtColor(imgInv, cv.COLOR_GRAY2BGR)
    img = cv.bitwise_and(img, imgInv)
    img = cv.bitwise_or(img, imgCanvas)

    # setting the header image
    if images is not None:
        img[0:125, 0:1280] = images
    
    # Add instructions
    cv.putText(img, "Q to quit | Two fingers up to select | Index finger only to draw | Index + Middle to erase", (10, 710), 
               cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    cv.imshow("Hand Tracking Painter", img)
    cv.imshow("Canvas", imgCanvas)
    
    # Press 'q' to exit
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
