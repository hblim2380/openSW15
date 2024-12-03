import os
import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from flask import Flask, jsonify
import threading

app = Flask(__name__)

# result.txt 파일 경로
RESULT_FILE_PATH = 'result.txt'

class Custom_DeepSORT_Tracker:
    def __init__(self):
        self.tracker = DeepSort(max_age=100)

    def update_tracker(self, detections):
        bbs = []
        if detections[0].boxes.xyxy.tolist():
            for d in detections:
                box = d.boxes.xyxy.tolist()[0]
                conf = d.boxes.conf.tolist()[0]
                cls = int(d.boxes.cls.tolist()[0])
                bb = (box, conf, cls)
                bbs.append(bb)

        tracks = self.tracker.update_tracks(bbs, frame=detections[0].orig_img)
        return tracks

def calculate_movement(prev_bbox, current_bbox, frame=None, threshold=50):
    prev_center_x = (prev_bbox[0] + prev_bbox[2]) / 2
    prev_center_y = (prev_bbox[1] + prev_bbox[3]) / 2
    curr_center_x = (current_bbox[0] + current_bbox[2]) / 2
    curr_center_y = (current_bbox[1] + current_bbox[3]) / 2
    movement = np.sqrt((prev_center_x - curr_center_x)**2 + (prev_center_y - curr_center_y)**2)
    return movement < threshold

def calculate_area(bbox):
    return abs(bbox[2] - bbox[0]) * abs(bbox[3] - bbox[1])

def load_age_gender_models():
    prototxt_path = 'models/face_recognition/deploy.prototxt'
    model_path = 'models/face_recognition/res10_300x300_ssd_iter_140000_fp16.caffemodel'
    age_net_path = 'models/age_prediction/age_net.caffemodel'
    
    face_net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
    age_net = cv2.dnn.readNetFromCaffe('models/age_prediction/age_deploy.prototxt', age_net_path)
    
    return face_net, age_net

def detect_face(frame, face_net):
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
    face_net.setInput(blob)
    detections = face_net.forward()
    
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            return box.astype("int")
    
    return None

def predict_age(face_crop, age_net):
    blob = cv2.dnn.blobFromImage(face_crop, 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746))
    age_net.setInput(blob)
    age_preds = age_net.forward()
    age = int(np.argmax(age_preds))
    return age

def save_result(age):
    # 파일에 결과 저장
    if 0 <= age <= 8:
        with open('result.txt', 'w') as f:
            f.write('2')
    elif 8 < age <= 60:
        with open('result.txt', 'w') as f:
            f.write('1')
    else:
        with open('result.txt', 'w') as f:
            f.write('0')

def run_object_tracking():
    model = YOLO('yolov10n.pt')
    face_net, age_net = load_age_gender_models()
    cap = cv2.VideoCapture(0)
    tracker = Custom_DeepSORT_Tracker()
    selected_id = None
    selected_bbox = None
    state = 'initial'
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        results = model.predict(frame, device='cpu', classes=0)
        
        if state == 'initial':
            tracks = tracker.update_tracker(results)
            frame_width = frame.shape[1]
            frame_height = frame.shape[0]
            
            stationary_persons = []
            for track in tracks:
                if track.det_class == 0:
                    bbox = track.to_ltrb()
                    movement = calculate_movement((0, 0, frame_width, frame_height), bbox, frame=frame, threshold=250)
                    if movement:
                        stationary_persons.append((track, calculate_area(bbox)))
            
            if stationary_persons:
                selected_track, _ = max(stationary_persons, key=lambda x: x[1])
                selected_id = selected_track.track_id
                selected_bbox = selected_track.to_ltrb()
                
                x1, y1, x2, y2 = map(int, selected_bbox)
                x1, y1, x2, y2 = max(0, x1), max(0, y1), min(frame.shape[1], x2), min(frame.shape[0], y2)
                
                person_crop = frame[y1:y2, x1:x2]
                if person_crop.size == 0:
                    state = 'initial'
                    continue
                
                face_bbox = detect_face(person_crop, face_net)
                if face_bbox is not None:
                    fx1, fy1, fx2, fy2 = face_bbox
                    face_crop = person_crop[fy1:fy2, fx1:fx2]
                    if face_crop.size == 0:
                        state = 'initial'
                        continue
                    
                    age = predict_age(face_crop, age_net)
                    save_result(age)  # 결과 저장
                    
                    state = 'tracking'
                else:
                    state = 'initial'
        
        elif state == 'tracking':
            tracks = tracker.update_tracker(results)
            track_found = False
            for track in tracks:
                if track.track_id == selected_id:
                    track_found = True
                    current_bbox = track.to_ltrb()
                    if not calculate_movement(selected_bbox, current_bbox):
                        continue
                    state = 'initial'
                    selected_id = None
                    selected_bbox = None
                    break
            
            if not track_found:
                state = 'initial'
                selected_id = None
                selected_bbox = None
        
        cv2.imshow('Object Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Flask 서버에서 result.txt 반환하는 엔드포인트
@app.route('/result', methods=['GET'])
def get_result():
    """
    result.txt 파일의 내용을 반환하는 엔드포인트
    """
    if os.path.exists(RESULT_FILE_PATH):
        with open(RESULT_FILE_PATH, 'r') as file:
            result_content = file.read()
        return jsonify({'result': result_content}), 200
    else:
        return jsonify({'error': 'result.txt file not found'}), 404

# Flask 서버 실행을 위한 쓰레드 함수
def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

if __name__ == "__main__":
    # Flask 서버와 Object Tracking을 동시에 실행
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Object Tracking 함수 실행
    run_object_tracking()
