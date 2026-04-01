import cv2
import numpy as np
import urllib.request
import tkinter as tk
from PIL import Image, ImageTk
from ultralytics import YOLO
import time
import threading
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import base64

gui_frame = None

# ================= CONFIG =================
CAMERAS = [
    {"id": "cam_01", "url": "http://169.254.64.11:8080/snapshot", "topic": "safety/detections/cam_01"},
    {"id": "cam_02", "url": "http://169.254.64.12:8080/snapshot", "topic": "safety/detections/cam_02"},
    {"id": "cam_03", "url": "http://169.254.64.13:8080/snapshot", "topic": "safety/detections/cam_03"},
    {"id": "cam_04", "url": "http://169.254.64.14:8080/snapshot", "topic": "safety/detections/cam_04"},
]

FPS_INTERVAL  = 300          # slightly relaxed for Pi 5
MODEL_PATH = "/home/student/ppe/edge_ppe_model3/best_ncnn_model4"

CLASS_COLORS = {
    "Hardhat":        (0, 200, 0),
    "NO-Hardhat":     (0, 0, 220),
    "Safety Vest":    (0, 200, 0),
    "NO-Safety Vest": (0, 0, 220),
    "Boots":          (0, 200, 0),
    "NO-Boots":       (0, 0, 220),
    "Person":         (200, 200, 0),
}

# ================= LOAD MODEL =================
from ultralytics import YOLO

MODEL_PATH = "/home/student/ppe/edge_ppe_model3/best_ncnn_model"

print(f"[INFO] Loading model: {MODEL_PATH}")
model = YOLO(MODEL_PATH, task="detect")
print("[INFO] Model loaded successfully")

# ================= MQTT SETUP =================
MQTT_BROKER = "localhost"
MQTT_PORT   = 1883

mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)



# ================= FETCH FRAME =================
def fetch_frame(url):
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = bytearray(resp.read())
            arr  = np.asarray(data, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            return frame
    except Exception as e:
        print(f"[WARN] Frame fetch failed: {e}")
        return None

# ================= INFERENCE =================
def run_inference(frame):
    results    = model(frame, conf=0.25, iou=0.5, verbose=False)[0]
    annotated  = frame.copy()
    detections = []

    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf   = float(box.conf[0])
        label  = model.names.get(cls_id, f"cls{cls_id}")
        color  = CLASS_COLORS.get(label, (255, 255, 0))
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated, f"{label} {conf:.2f}",
                    (x1, max(y1 - 8, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        detections.append({"class": label, "conf": round(conf, 3)})

    return annotated, detections


# ================= CAMERA THREAD =================
def camera_thread(cam):
    global gui_frame
    while True:
        # 1. Get the raw image from the camera
        frame = fetch_frame(cam["url"])

        if frame is None:
            print(f"[WARN] {cam['id']} offline")
            time.sleep(5) 
            continue

        # 2. Run AI Inference (get boxes and labels)
        annotated, detections = run_inference(frame)

        # 3. --- NEW: M5STICK LOGIC (One per camera) ---
        # Determine status for this specific camera
        # Count detections
        num_person   = sum(1 for d in detections if d["class"] == "Person")
        num_hardhat  = sum(1 for d in detections if d["class"] == "Hardhat")
        num_vest     = sum(1 for d in detections if d["class"] == "Safety Vest")
        num_boots    = sum(1 for d in detections if d["class"] == "Boots")

        # Default
        status_msg = "YELLOW"

        if num_person > 0:
            # 🔥 ANY missing PPE → RED
            if num_hardhat < num_person or num_vest < num_person or num_boots < num_person:
                status_msg = "RED"
            else:
                status_msg = "GREEN"

        # Publish simple text to the specific alert topic for this camera
        # M5Stick 1 subscribes to ppe/alerts/cam_01, etc.
        mqtt_client.publish(f"ppe/alerts/{cam['id']}", status_msg)


        # 4. --- DASHBOARD LOGIC (With Image) ---
        success, buffer = cv2.imencode('.jpg', annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        
        if success:
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')

            message = {
                "device_id": cam["id"],
                "timestamp": datetime.now().isoformat(),
                "num_detections": len(detections),
                "detections": detections,
                "image": jpg_as_text 
            }
            # Dashboard stays subscribed to safety/detections/#
            mqtt_client.publish(cam["topic"], json.dumps(message))

        # 5. Update local GUI if this is cam_01
        if cam["id"] == "cam_01":
            gui_frame = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

        time.sleep(0.01)



# ================= GUI =================
class PPEViewer:
    def __init__(self, root):
        self.root  = root
        self.root.title("PPE Monitor — Pi 5")
        self.root.configure(bg="#1a1a1a")

        # Title
        tk.Label(root, text="PPE Live Monitor",
                 fg="white", bg="#1a1a1a",
                 font=("Courier", 14, "bold")).pack(pady=(10, 0))

        # Video
        self.video_label = tk.Label(root, bg="#1a1a1a")
        self.video_label.pack(padx=10, pady=10)

        # Status
        self.status_var = tk.StringVar(value="Connecting...")
        tk.Label(root, textvariable=self.status_var,
                 fg="lime", bg="#111111",
                 font=("Courier", 10)).pack(fill="x", padx=10, pady=(0, 10))

        # Start update loop
        self.update_gui()

    # <-- New method replaces old update()
    def update_gui(self):
        global gui_frame
        if gui_frame is not None:
            img = Image.fromarray(gui_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
            self.status_var.set(f"Showing cam_01")
        self.root.after(FPS_INTERVAL, self.update_gui)





# ================= MAIN =================
if __name__ == "__main__":
    print("[INFO] Starting GUI...")
    for cam in CAMERAS:
    	t = threading.Thread(target=camera_thread, args=(cam,), daemon=True)
    	t.start()

    root = tk.Tk()
    root.geometry("800x600")
    PPEViewer(root)
    root.mainloop()
