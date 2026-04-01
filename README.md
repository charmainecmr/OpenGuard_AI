# OpenGuard: Edge AI for Automated PPE Compliance

## Overview

OpenGuard is a distributed multi-node edge AI system that monitors Personal Protective Equipment (PPE) compliance in real-time across construction sites.

Unlike traditional cloud-based systems, OpenGuard performs on-device inference using edge hardware, ensuring:

- Low latency
- Reduced bandwidth usage
- Improved privacy
- Scalable deployment across multiple zones

The system integrates computer vision, IoT communication, and a real-time dashboard to provide immediate safety feedback to workers and supervisors.

---

## Problem Statement

Construction sites are among the most hazardous working environments globally. In Singapore, ~52% of fatal incidents are caused by falls, often due to inconsistent PPE compliance.

**Limitations of existing solutions:**

| Approach | Problem |
|----------|---------|
| Manual supervision | Labour-intensive and reactive |
| Cloud-based systems | High latency, bandwidth cost, privacy concerns |
| Academic prototypes | Limited to single-node setups |

OpenGuard addresses these gaps with a fully edge-based, multi-zone, real-time monitoring system.

---

## System Architecture

```
[Camera (per zone)]
        ↓
[Raspberry Pi Zero 2 W]  ← Edge Nodes (uStreamer → MJPEG stream)
        ↓
[Raspberry Pi 5]         ← Central Coordinator + MQTT Broker
        ↓
   ┌────┴────┐
[M5Stick] [Dashboard]
```

### Edge Nodes (Raspberry Pi Zero 2 W)

- Capture video from Logitech C270 webcams
- Stream MJPEG video to the central node via **uStreamer** (low-latency, hardware-accelerated streaming)
- Operate independently (fault tolerant)

### Central Node (Raspberry Pi 5)

- Consumes MJPEG streams from each edge node
- Runs YOLO inference using the NCNN model
- Hosts the MQTT broker (Mosquitto)
- Aggregates multi-zone detection data
- Serves the monitoring dashboard

### M5StickC Plus

- Subscribes to MQTT alerts
- Displays real-time safety status:
  - RED → Missing PPE
  - YELLOW → No people detected
  - GREEN → All PPE present

### Dashboard

- Displays live camera feeds (via uStreamer)
- Shows per-zone PPE detection statistics
- Provides real-time alerts

---

## AI Model

### Model: `best_ncnn_model`

The model is a **YOLOv8n** trained on a merged PPE dataset and exported to **NCNN** format for efficient edge inference.

| Property | Value |
|----------|-------|
| Format | NCNN (`.param` + `.bin`) |
| Input size | 640 × 640 |
| Stride | 32 |
| Batch size | 1 |
| Task | Object Detection |
| Trained with | Ultralytics v8.4.30 |
| Training date | 2026-03-27 |

**Detection Classes:**

| ID | Class |
|----|-------|
| 0 | Hardhat |
| 1 | NO-Hardhat |
| 2 | Safety Vest |
| 3 | NO-Safety Vest |
| 4 | Boots |
| 5 | NO-Boots |
| 6 | Person |

The NCNN format removes the Python/PyTorch runtime dependency, making inference viable on resource-constrained devices like the Raspberry Pi 5.

---

## Safety Logic

```
IF person detected AND any PPE class is missing → RED alert
ELSE IF no person detected                      → YELLOW (standby)
ELSE                                            → GREEN (compliant)
```

---

## Communication (MQTT)

| Topic | Purpose |
|-------|---------|
| `ppe/alerts/cam_x` | Safety status sent to M5StickC |
| `safety/detections/#` | Detection data sent to dashboard |

**Why MQTT?** Lightweight, real-time, scalable, and decouples system components.

---

## Video Streaming (uStreamer)

Each Raspberry Pi Zero 2 W runs **uStreamer** to capture and stream camera frames as an MJPEG HTTP stream. uStreamer is chosen over alternatives (e.g. `mjpg-streamer`) for its:

- Better performance on ARM hardware
- Lower CPU overhead
- Stable HTTP/MJPEG output compatible with OpenCV and browser clients

The central node reads each stream directly using OpenCV (`cv2.VideoCapture`) for inference.

---

## Experiments & Results

Optimisation followed the **PASO framework** (Profile → Analyse → Schedule → Optimise):

| Stage | Initial Model (~7s/frame) | Retrained NCNN Model (~4s/frame) |
|-------|--------------------------|----------------------------------|
| Profiling | High latency | Reduced latency |
| Analysis | Complex, slow | Optimised for edge |
| Scheduling | Frame drops | Smooth updates |
| Optimisation | Inconsistent | Stable & responsive |

**Key findings:**

- Initial model was too slow for real-time deployment
- Retrained and NCNN-converted model reduced latency by ~40%
- Improved consistency and stable MQTT integration

---

## Tech Stack

### Hardware

- Raspberry Pi Zero 2 W (edge nodes)
- Raspberry Pi 5 (central coordinator)
- M5StickC Plus (alert display)
- Logitech C270 Webcams

### Software

| Component | Technology |
|-----------|-----------|
| Inference | Ultralytics YOLOv8 + NCNN |
| Video streaming | uStreamer (MJPEG) |
| Messaging | MQTT (Mosquitto + paho-mqtt) |
| Dashboard | Flask + OpenCV |
| Alert display | Arduino C++ (M5StickC) |
| Language | Python (OpenCV, NumPy) |

---

## Limitations

- Detection accuracy depends on training data quality
- No per-person PPE tracking across frames
- Limited FPS on edge hardware
- Sensitive to lighting conditions

---

## Future Improvements

- Per-person PPE tracking (ReID / tracking algorithms)
- Fall detection integration
- Temporal smoothing to reduce false alerts
- Mobile app integration
- Hardware acceleration (NPU / GPU)
- Historical analytics and reporting

---

## Team

- PEK JUN TECK KEITH
- JONATHAN ZENG YU ZHAO
- CHARMAINE CHOO MIN RE
- NG XING WEI DELVIN
- MATTHEW CHUA XIANG JUN

Faculty Supervisor: Professor Muhamed Fauzi Bin Abbas

---

## Reference

Ministry of Manpower Singapore (2023). *Workplace Safety and Health Report 2023*.
https://www.mom.gov.sg/workplace-safety-and-health

---

## Conclusion

OpenGuard demonstrates how Edge AI and IoT can be combined to build a scalable, low-cost, real-time safety monitoring system for industrial environments. By combining uStreamer for efficient video transport, a retrained NCNN-optimised YOLOv8n model, and MQTT-based communication, the system achieves practical PPE compliance monitoring without relying on cloud infrastructure.
