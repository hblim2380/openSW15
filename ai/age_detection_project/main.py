import os
import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

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
    """
    Calculate the movement between two bounding boxes.
    Returns True if movement is less than the threshold.
    """
    prev_center_x = (prev_bbox[0] + prev_bbox[2]) / 2
    prev_center_y = (prev_bbox[1] + prev_bbox[3]) / 2
    curr_center_x = (current_bbox[0] + current_bbox[2]) / 2
    curr_center_y = (current_bbox[1] + current_bbox[3]) / 2
    print(f"prev_center_x: {prev_center_x}, prev_center_y: {prev_center_y}")
    
    movement = np.sqrt((prev_center_x - curr_center_x)**2 + (prev_center_y - curr_center_y)**2)
    print(f"Movement: {movement}")
    return movement < threshold

def calculate_area(bbox):
    """
    Calculate the area of a bounding box.
    """
    return abs(bbox[2] - bbox[0]) * abs(bbox[3] - bbox[1])

def load_age_gender_models():
    """
    Load pre-trained age and gender detection models.
    """
    prototxt_path = 'models/face_recognition/deploy.prototxt'
    model_path = 'models/face_recognition/res10_300x300_ssd_iter_140000_fp16.caffemodel'
    age_net_path = 'models/age_prediction/age_net.caffemodel'
    
    face_net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
    age_net = cv2.dnn.readNetFromCaffe('models/age_prediction/age_deploy.prototxt', age_net_path)
    
    return face_net, age_net

def detect_face(frame, face_net):
    """
    Detect face in the given frame using the face detection model.
    """
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
    """
    Predict age of the detected face.
    """
    blob = cv2.dnn.blobFromImage(face_crop, 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746))
    
    age_net.setInput(blob)
    age_preds = age_net.forward()
    age = int(np.argmax(age_preds))
    
    return age
def main():
    # Load models
    model = YOLO('yolov10n.pt')
    face_net, age_net = load_age_gender_models()
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    # DeepSORT tracker
    tracker = Custom_DeepSORT_Tracker()
    
    # State variables
    selected_id = None
    selected_bbox = None
    state = 'initial'
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # YOLO detection with person class only
        results = model.predict(frame, device='cpu', classes=0)
        
        if state == 'initial':
            # Detect tracks
            tracks = tracker.update_tracker(results)
            # 영상의 크기 얻기 (너비, 높이)
            frame_width = frame.shape[1]  # frame.shape[1]은 영상의 너비
            frame_height = frame.shape[0]  # frame.shape[0]은 영상의 높이
            
            # Find stationary person with largest area
            stationary_persons = []
            for track in tracks:
                if track.det_class == 0:  # person class
                    bbox = track.to_ltrb()
                    movement = calculate_movement((0, 0, frame_width, frame_height), bbox, frame=frame, threshold=250)
                    if movement:
                        stationary_persons.append((track, calculate_area(bbox)))
                        print(f"stationary_persons: {stationary_persons}")
            
            if stationary_persons:
                # Select person with largest area
                selected_track, _ = max(stationary_persons, key=lambda x: x[1])
                selected_id = selected_track.track_id
                selected_bbox = selected_track.to_ltrb()
                print(f"selected_id: {selected_id}, selected_bbox: {selected_bbox}")
                
                # Crop the region
                x1, y1, x2, y2 = map(int, selected_bbox)
                
                # Ensure the cropping coordinates are within the valid image range
                x1, y1, x2, y2 = max(0, x1), max(0, y1), min(frame.shape[1], x2), min(frame.shape[0], y2)
                
                person_crop = frame[y1:y2, x1:x2]
                
                # Check if the cropped image is empty
                if person_crop.size == 0:
                    print("Error: Cropped person image is empty!")
                    with open('result.txt', 'w') as f:
                        f.write('1')
                    state = 'initial'  # Reset state for re-detection
                    continue
                
                cv2.imwrite("cropped.jpg", person_crop)
                
                # Face detection
                face_bbox = detect_face(person_crop, face_net)
                
                if face_bbox is not None:
                    # Crop face
                    fx1, fy1, fx2, fy2 = face_bbox
                    face_crop = person_crop[fy1:fy2, fx1:fx2]
                    
                    # Check if the cropped face image is valid
                    if face_crop.size == 0:
                        print("Error: Cropped face image is empty!")
                        with open('result.txt', 'w') as f:
                            f.write('1')
                        state = 'initial'  # Reset state for re-detection
                        continue
                    
                    cv2.imwrite("face_crop.jpg", face_crop)
                    
                    # Age prediction
                    age = predict_age(face_crop, age_net)
                    
                    # Save age category
                    if 0 <= age <= 8:
                        with open('result.txt', 'w') as f:
                            f.write('2')
                    elif 8 < age <= 60:
                        with open('result.txt', 'w') as f:
                            f.write('1')
                    else:
                        with open('result.txt', 'w') as f:
                            f.write('0')
                    
                    state = 'tracking'
                else:
                    # Face detection failed
                    with open('result.txt', 'w') as f:
                        f.write('1')
                    state = 'initial'  # Reset state for re-detection
        
        elif state == 'tracking':
            # Track only the selected person
            tracks = tracker.update_tracker(results)
            
            track_found = False
            for track in tracks:
                if track.track_id == selected_id:
                    track_found = True
                    current_bbox = track.to_ltrb()
                    
                    # Check if movement exceeds threshold
                    if not calculate_movement(selected_bbox, current_bbox):
                        continue
                    
                    # Reset if significant movement detected
                    state = 'initial'
                    selected_id = None
                    selected_bbox = None
                    break
            
            # If the selected track is not found in the current frame, reset to initial state
            if not track_found:
                print("Selected track not found, resetting state.")
                state = 'initial'
                selected_id = None
                selected_bbox = None
        
        # Visualization
        for track in tracks:
            if selected_id is not None and track.track_id == selected_id:
                x1, y1, x2, y2 = [int(i) for i in track.to_ltrb()]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"Selected ID: {selected_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36, 255, 12), 2)
        
        cv2.imshow('Object Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

