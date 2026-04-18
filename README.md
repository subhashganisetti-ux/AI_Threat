# 🚨 AI Threat Detection System (Pose-Based)

A real-time computer vision system that detects suspicious human behavior using pose estimation and a custom-trained machine learning model.

---

## 🧠 Problem

Traditional surveillance systems rely heavily on manual monitoring or basic motion detection, which leads to:

* High false positives
* Delayed response to threats
* Poor scalability in real-world environments

This project addresses the problem by analyzing **human posture and intent**, rather than just movement.

---

## ⚙️ Approach

The system follows a structured multi-stage AI pipeline:

### 1. Person Detection

* Uses **YOLOv8** to detect humans in each frame

### 2. Pose Estimation

* Uses **YOLOv8-Pose** to extract skeletal keypoints

### 3. Feature Engineering

* Skeleton normalization (position-invariant)
* Joint angle computation (captures intent)

### 4. Custom Threat Classifier

* Trained on a **custom dataset (~11,000+ labeled samples)**
* Classifies poses into:

  * Safe
  * Threat

### 5. Multi-frame Decision Logic

* Uses a **3-frame voting mechanism**
* Reduces false positives significantly
* Improves real-world reliability

---

## 📊 Dataset

* Built a **custom pose dataset (~11K+ rows)** from video data
* Extracted skeleton features using YOLO-Pose
* Applied filtering and normalization for robust training
* Balanced and cleaned data to improve model performance

👉 This is not a prebuilt dataset — it was **created and engineered from scratch**

---

## 🎯 Results

* Achieved ~80% accuracy on real-world pose data
* Stable performance across different poses and environments
* Reduced false positives using multi-frame validation
* Successfully detects suspicious postures in real-time

---

## 🖥️ Result

https://github.com/user-attachments/assets/e89d0306-53a0-4362-945c-88403e5fbc6b

---

## 🛠️ Tech Stack

* Python
* OpenCV
* Ultralytics YOLOv8
* Streamlit
* NumPy
* Scikit-learn
* XGBoost

---

## 📁 Project Structure

```
AI_Threat_Detection_Pipeline/
│
├── app/
│   ├── main_app.py
│   ├── vision_pipeline.py
│   ├── alert_service.py
│
├── data/
│   └── sample_dataset.csv
│
├── notebooks/
│   └── training_pipeline.ipynb
│
├── .gitignore
└── README.md
```

---

## ⚠️ Note

Model files are not included due to size limitations.

To run locally, place the following inside a `models/` folder:

* yolov8n.pt
* yolov8n-pose.pt
* threat_model.pkl

---

## 🌲 ForestEye Vision (Real-World Integration)

This project is part of a larger system concept:

### 🔥 ForestEye — Edge AI Poaching Detection System

The full system integrates:

* 📷 Camera nodes (ESP32 / edge devices)
* 🎤 Audio sensors (gunshot detection)
* 🧠 AI threat detection (this project)
* 🔔 Real-time alert system for rangers

### 💡 How this model fits:

* Runs as the **core intelligence module**
* Analyzes human posture to detect suspicious activity
* Can be deployed on:

  * Edge devices (Raspberry Pi)
  * Central monitoring systems

---

## 🚀 Future Improvements

* 🔄 Real-time continuous video inference
* 🌐 Cloud-based deployment with API endpoints
* 🎯 Improved model accuracy with larger dataset
* 📡 Integration with IoT hardware (ESP32, sensors, edge cameras)
* 🔊 Multi-modal fusion (audio + vision threat detection)
* 📍 GPS-based alert system for field tracking

---

## 👩‍💻 Author

**Ganta Charishma**
B.Tech CSE (Cybersecurity + IoT + Blockchain)
AI & Edge Intelligence Enthusiast

---

## 💥 Final Note

This project focuses on **practical AI system design**, combining:

* Computer vision
* Feature engineering
* Custom ML modeling
* Real-time decision systems

👉 Built not just as a model — but as a **deployable intelligent system**
