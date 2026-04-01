from flask import Flask, render_template_string
import paho.mqtt.client as mqtt
import json
import threading

app = Flask(__name__)

# ================= CONFIG =================
MQTT_BROKER = "localhost"
TOPIC = "safety/detections/#"

# We no longer need CAMERA_URLS here because images come via MQTT
latest_data = {}

# ================= MQTT =================
def on_message(client, userdata, msg):
    global latest_data
    try:
        data = json.loads(msg.payload.decode())
        cam_id = data["device_id"]
        # Process the PPE stats before storing
        data["stats"] = process_ppe(data)
        latest_data[cam_id] = data
    except Exception as e:
        print(f"Error processing message: {e}")

def mqtt_thread():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883, 60)
    client.subscribe(TOPIC)
    client.loop_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()

# ================= PPE PROCESSING =================
def process_ppe(data):
    stats = {"Person": 0, "Hardhat": 0, "Safety Vest": 0, "Boots": 0}
    for d in data["detections"]:
        cls = d["class"]
        if cls in stats:
            stats[cls] += 1

    p = stats["Person"]
    return {
        "people": p,
        "hardhat": stats["Hardhat"],
        "vest": stats["Safety Vest"],
        "boots": stats["Boots"],
        "no_hardhat": max(p - stats["Hardhat"], 0),
        "no_vest": max(p - stats["Safety Vest"], 0),
        "no_boots": max(p - stats["Boots"], 0),
    }

# ================= WEB PAGE =================
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>PPE Real-Time Dashboard</title>
    <meta http-equiv="refresh" content="1"> 
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #1a1a1a; color: white; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
        .card { background: #2d2d2d; border-radius: 12px; padding: 15px; border: 1px solid #444; }
        .img-container { position: relative; width: 100%; border-radius: 8px; overflow: hidden; }
        img { width: 100%; display: block; }
        .stats-overlay { display: flex; justify-content: space-around; margin-top: 15px; }
        .stat-box { text-align: center; font-size: 0.9em; }
        .ok { color: #00ff00; }
        .bad { color: #ff4444; font-weight: bold; }
        h2 { margin-top: 0; color: #aaa; font-size: 1.2em; }
    </style>
</head>
<body>
    <h1 style="text-align:center;">🏗️ Site Safety Monitor</h1>
    <div class="grid">
    {% for cam_id, info in data_map.items() %}
        <div class="card">
            <h2>Channel: {{ cam_id }}</h2>
            <div class="img-container">
                <img src="data:image/jpeg;base64,{{ info.image }}" alt="Live Feed">
            </div>
            
            <div class="stats-overlay">
                <div class="stat-box">
                    <div>Workers</div>
                    <div style="font-size: 1.5em;">{{ info.stats.people }}</div>
                </div>
                <div class="stat-box">
                    <div>Hardhats</div>
                    <div class="{{ 'bad' if info.stats.no_hardhat > 0 else 'ok' }}">
                        {{ info.stats.hardhat }}/{{ info.stats.people }}
                    </div>
                </div>
                <div class="stat-box">
                    <div>Vests</div>
                    <div class="{{ 'bad' if info.stats.no_vest > 0 else 'ok' }}">
                        {{ info.stats.vest }}/{{ info.stats.people }}
                    </div>
                </div>
                <div class="stat-box">
                    <div>Boots</div>
                    <div class="{{ 'bad' if info.stats.no_boots > 0 else 'ok' }}">
                        {{ info.stats.boots }}/{{ info.stats.people }}
                    </div>
                </div>
            </div>
        </div>
    {% endfor %}
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    # Sort by camera ID so the UI doesn't jump around
    sorted_data = dict(sorted(latest_data.items()))
    return render_template_string(HTML, data_map=sorted_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)