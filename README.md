# OpenGuard: Edge AI for Automated PPE Compliance

## Overview
OpenGuard is a distributed multi-node edge AI system designed to monitor Personal Protective Equipment (PPE) compliance in real-time across construction sites.

Unlike traditional cloud-based systems, OpenGuard performs on-device inference using edge hardware, ensuring:
- Low latency
- Reduced bandwidth usage
- Improved privacy
- Scalable deployment across multiple zones

The system integrates computer vision, IoT communication, and real-time dashboards to provide immediate safety feedback to workers and supervisors.

---

## Problem Statement

Construction sites are among the most hazardous working environments globally.  
In Singapore, ~52% of fatal incidents are caused by falls, often due to inconsistent PPE compliance.

### Limitations of Existing Solutions
- Manual supervision → labour-intensive and reactive  
- Cloud-based systems → high latency, bandwidth cost, privacy concerns  
- Academic prototypes → limited to single-node setups  

### Solution
OpenGuard addresses these gaps with a fully edge-based, multi-zone, real-time monitoring system.

---

## Project Objectives

1. Train and deploy a YOLOv8n PPE detection model  
2. Optimise model using NCNN for edge deployment  
3. Build a multi-node edge architecture  
4. Enable real-time MQTT communication  
5. Provide instant alerts via M5Stick  
6. Develop a centralised monitoring dashboard  

---

## System Architecture
[Camera (per zone)]
↓
[Raspberry Pi Zero 2 W] (Edge Nodes)
↓
[Raspberry Pi 5] (Central Coordinator + MQTT Broker)
↓
┌───────────────┬───────────────┐
[M5Stick Alert] [Dashboard UI]


---

## Components

### Edge Nodes (Raspberry Pi Zero 2 W)
- Capture video using Logitech C270 webcams  
- Stream frames to central node  
- Operate independently (fault tolerant)  

### Central Node (Raspberry Pi 5)
- Runs YOLO inference  
- Hosts MQTT broker  
- Aggregates multi-zone data  
- Serves dashboard  

### M5StickC Plus
- Subscribes to MQTT alerts  
- Displays real-time safety status:
  - RED → Missing PPE  
  - YELLOW → No people detected  
  - GREEN → Safe  

### Dashboard
- Displays live camera feeds  
- Shows PPE statistics  
- Provides zone-level alerts  

---

## AI Model

- Model: YOLOv8n  
- Classes:
  - Person  
  - HardHat / No HardHat  
  - Safety Vest / No Safety Vest  
  - Boots / No Boots  

### Optimisation
- Converted to NCNN format  
- Designed for edge devices  

---

## Safety Logic
IF any PPE is missing → RED
ELSE IF all PPE present → GREEN
ELSE → YELLOW


---

## Communication (MQTT)

### Topics
| Topic | Purpose |
|------|--------|
| ppe/alerts/cam_x | Sends safety status to M5Stick |
| safety/detections/# | Sends detection data to dashboard |

### Why MQTT?
- Lightweight  
- Real-time  
- Scalable  
- Decouples system components  

---

## Experiments & Results

Using PASO framework:

| Stage | First Model (~7s) | Retrained Model (~4s) |
|------|------------------|-----------------------|
| Profiling | High latency | Reduced latency |
| Analysis | Complex, slow | Optimised for edge |
| Scheduling | Frame drops | Smooth updates |
| Optimisation | Inconsistent | Stable & responsive |

### Key Findings
- Initial model too slow for real-time  
- Optimised model:
  - Reduced latency (~40%)  
  - Improved consistency  
  - Better integration with MQTT  

---

## Features

- Multi-zone PPE monitoring  
- Fully edge-based system  
- Real-time alerts  
- Dashboard visualisation  
- Scalable architecture  
- Fault-tolerant design  

---

## Tech Stack

### Hardware
- Raspberry Pi Zero 2 W  
- Raspberry Pi 5  
- M5StickC Plus  
- Logitech C270 Cameras  

### Software
- Python (OpenCV, NumPy)  
- Ultralytics YOLOv8  
- NCNN  
- MQTT (paho-mqtt)  
- Flask  
- Tkinter  
- Arduino C++  

---

---

## Limitations

- Detection accuracy depends on training data  
- No per-person PPE tracking  
- Limited FPS on edge hardware  
- Sensitive to lighting conditions  

---

## Future Improvements

- Per-person PPE tracking  
- Fall detection integration  
- Temporal smoothing  
- Mobile app integration  
- Hardware acceleration (NPU / GPU)  
- Historical analytics  

---

## Demo Highlights

- Real-time PPE detection  
- Instant LED alerts  
- Multi-camera dashboard  
- Fully edge-based system  

---

## Team

- PEK JUN TECK KEITH  
- JONATHAN ZENG YU ZHAO  
- CHARMAINE CHOO MIN RE  
- NG XING WEI DELVIN  
- MATTHEW CHUA XIANG JUN  

Faculty: Professor Muhamed Fauzi Bin Abbas  

---

## Reference

Ministry of Manpower Singapore (2023)  
Workplace Safety and Health Report 2023  
https://www.mom.gov.sg/workplace-safety-and-health  

---

## Conclusion

OpenGuard demonstrates how Edge AI + IoT can be combined to build a scalable, low-cost, real-time safety monitoring system for industrial environments.

It bridges the gap between academic prototypes and real-world deployment, enabling practical and efficient PPE compliance monitoring.
