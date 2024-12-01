import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
else:
    print("Camera opened successfully")
cap.release()
