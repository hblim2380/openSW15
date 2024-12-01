import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

# YOLO 모델 로드
yolo_model = YOLO('yolov10n.pt')  # YOLOv10 모델 가중치

# DeepSORT 초기화
deepsort = DeepSort()

# OpenCV 모델 로드
face_net = cv2.dnn.readNetFromCaffe("models/face_recognition/deploy.prototxt",
                                    "models/face_recognition/res10_300x300_ssd_iter_140000_fp16.caffemodel")

age_net = cv2.dnn.readNetFromCaffe("models/age_prediction/age_deploy.prototxt",
                                   "models/age_prediction/age_net.caffemodel")

# 원래 모델의 8개 범주 정의
CAFFE_AGE_GROUPS = [
    '(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60+)'
]

# 8개의 범주를 3개의 통합 범주로 매핑
AGE_GROUP_MAPPING = {
    0: '(0-8)',  # (0-2)
    1: '(0-8)',  # (4-6)
    2: '(8-60)', # (8-12)
    3: '(8-60)', # (15-20)
    4: '(8-60)', # (25-32)
    5: '(60+)', # (38-43)
    6: '(60+)', # (48-53)
    7: '(60+)'  # (60+)
}

# 비디오 캡처 (웹캠)
cap = cv2.VideoCapture(0)

# 추적 데이터 및 이동 임계값
selected_object = None  # 현재 선택된 객체
movement_threshold = 50  # 임계값 (픽셀 단위)
last_center = None       # 이전 중심 좌표
face_detected = False    # 얼굴이 탐지되었는지 여부
age_predicted = False    # 나이가 예측되었는지 여부

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO 객체 탐지
    results = yolo_model(frame, stream=True)
    detections = []
    for result in results:
        for box in result.boxes.cpu().numpy():
            x1, y1, x2, y2 = box.xyxy[0]
            confidence = float(box.conf[0])
            cls = int(box.cls[0])  # 클래스 ID (0: person)

            if confidence > 0.4 and cls == 0:  # person 클래스만
                detections.append([x1, y1, x2, y2, confidence])  # (x1, y1, x2, y2, confidence)

    print(f"Detections: {detections}")

    # DeepSORT에 맞는 형식으로 detection_boxes 준비
    detection_boxes = []
    for det in detections:
        x1, y1, x2, y2, confidence = det
        detection_boxes.append([float(x1), float(y1), float(x2), float(y2), float(confidence)])

    # DeepSORT 추적
    tracks = deepsort.update_tracks(detection_boxes, frame=frame)  # 트랙 업데이트

    for track in tracks:
        track_id = track[1]  # 추적 ID
        x1, y1, x2, y2 = track[0]
        x_center = (x1 + x2) // 2
        y_center = (y1 + y2) // 2

        # 객체 ID별 추적 처리
        if selected_object is None or selected_object[0] != track_id:
            # 객체 ID가 다르면, 새로운 객체를 추적
            selected_object = (track_id, (x1, y1, x2, y2))
            last_center = (x_center, y_center)

        # 이동 임계값 계산
        if last_center:
            movement = np.sqrt((x_center - last_center[0]) ** 2 + (y_center - last_center[1]) ** 2)
            if movement > movement_threshold:
                print(f"Object {track_id} moved. Reinitializing detection.")
                selected_object = None
                last_center = None
                face_detected = False
                age_predicted = False
                continue  # 새 객체 탐지로 진행

        last_center = (x_center, y_center)

        # 얼굴 인식 및 나이 예측 (한 번만 수행)
        if not face_detected or not age_predicted:
            cropped = frame[y1:y2, x1:x2]

            # 입력 이미지 검증
            if cropped is None or cropped.size == 0:
                print("Invalid cropped image!")
                with open("output.txt", "w") as f:
                    f.write("1")
                continue

            # 얼굴 인식
            blob = cv2.dnn.blobFromImage(cropped, 1.0, (300, 300), (104.0, 177.0, 123.0))
            face_net.setInput(blob)
            detections = face_net.forward()

            if detections.shape[2] == 0:
                print("No face detected!")
                with open("output.txt", "w") as f:
                    f.write("1")
                continue

            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > 0.5:
                    face_detected = True

                    # 얼굴 Bounding Box 추출
                    face_x1 = int(detections[0, 0, i, 3] * cropped.shape[1])
                    face_y1 = int(detections[0, 0, i, 4] * cropped.shape[0])
                    face_x2 = int(detections[0, 0, i, 5] * cropped.shape[1])
                    face_y2 = int(detections[0, 0, i, 6] * cropped.shape[0])

                    # 얼굴 크롭
                    face_crop = cropped[face_y1:face_y2, face_x1:face_x2]
                    
                    # 나이 예측 로직
                    try:
                        face_resized = cv2.resize(face_crop, (227, 227))
                        blob = cv2.dnn.blobFromImage(face_resized, 1.0, (227, 227), 
                                                    (78.4263377603, 87.7689143744, 114.895847746))
                        age_net.setInput(blob)
                        age_preds = age_net.forward()

                        # 원래 8개 범주에서 가장 높은 확률의 인덱스를 찾음
                        original_age_index = np.argmax(age_preds[0])

                        # 매핑 테이블을 사용하여 통합된 범주로 변환
                        age_group = AGE_GROUP_MAPPING[original_age_index]
                        age_predicted = True

                        # 얼굴 크롭 이미지에 나이 범주 추가
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        font_scale = 0.5
                        color = (0, 255, 0)  # 녹색
                        thickness = 1
                        labeled_face_crop = face_crop.copy()
                        cv2.putText(labeled_face_crop, age_group, (10, 20), font, font_scale, color, thickness)
                        cv2.imwrite("face_crop_labeled.jpg", labeled_face_crop)

                        # 나이 범위에 따라 output.txt에 저장
                        with open("output.txt", "w") as f:
                            if age_group == "(0-8)":
                                f.write("2")
                            elif age_group == "(8-60)":
                                f.write("1")
                            else:
                                f.write("0")

                    except Exception as e:
                        print(f"Error during age prediction: {e}")
                        with open("output.txt", "w") as f:
                            f.write("1")

    # 프레임 출력
    cv2.imshow("YOLO Detection with Face and Age Prediction", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):  # 'q' 키로 종료
        break

cap.release()
cv2.destroyAllWindows()
