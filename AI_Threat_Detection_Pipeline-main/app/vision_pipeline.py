import cv2
import numpy as np
import pickle
from ultralytics import YOLO

# ================= CONFIG =================
DET_MODEL_PATH = "C:\\Users\\chari\\OneDrive\\Projects\\ForestEye\\Models\\yolov8n.pt"
POSE_MODEL_PATH = "C:\\Users\\chari\\OneDrive\\Projects\\ForestEye\\Models\\yolov8n-pose.pt"
CLASSIFIER_PATH = "C:\\Users\\chari\\OneDrive\\Projects\\ForestEye\\Models\\threat.pkl"
THRESHOLD = 0.6
# =========================================

# ================= LOAD MODELS =================
det_model = YOLO(DET_MODEL_PATH)
pose_model = YOLO(POSE_MODEL_PATH)

with open(CLASSIFIER_PATH, "rb") as f:
    classifier = pickle.load(f)

# ================= HELPERS =================
def compute_angle(a, b, c):
    ba = a - b
    bc = c - b
    denom = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denom < 1e-6:
        return 0.0
    cosine = np.dot(ba, bc) / denom
    cosine = np.clip(cosine, -1.0, 1.0)
    return np.arccos(cosine)


def normalize_skeleton(joints):
    hip_center = (joints[6] + joints[9]) / 2
    joints = joints - hip_center

    shoulder_width = np.linalg.norm(joints[0] - joints[3])
    if shoulder_width < 1e-6:
        return None

    return (joints / shoulder_width).flatten()


def process_frame(frame):

    result = "No Person"
    probability = 0.0

    det = det_model(frame, verbose=False)

    if det[0].boxes is None or len(det[0].boxes) == 0:
        return result, probability

    person_found = any(int(cls) == 0 for cls in det[0].boxes.cls)

    if not person_found:
        return result, probability

    pose = pose_model(frame, verbose=False)

    if pose[0].keypoints is None or pose[0].keypoints.xy.shape[0] == 0:
        return result, probability

    kp = pose[0].keypoints.xy[0].cpu().numpy()

    selected = np.array([
        kp[6], kp[8], kp[10],
        kp[5], kp[7], kp[9],
        kp[12], kp[14], kp[16],
        kp[11], kp[13], kp[15]
    ])

    normalized = normalize_skeleton(selected)

    if normalized is None:
        return result, probability

    RS, RE, RW = selected[0], selected[1], selected[2]
    LS, LE, LW = selected[3], selected[4], selected[5]

    right_angle = compute_angle(RS, RE, RW)
    left_angle = compute_angle(LS, LE, LW)

    features = np.hstack((normalized, [right_angle, left_angle]))
    features = features.reshape(1, -1)

    probability = classifier.predict_proba(features)[0][1]

    if probability > THRESHOLD:
        result = "Threat"
    else:
        result = "Safe"

    return result, probability