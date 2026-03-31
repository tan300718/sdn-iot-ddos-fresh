from scapy.all import sniff
from scapy.layers.inet import IP
from collections import defaultdict
import time
import joblib
import numpy as np
import os
import json

# -------------------------------
# CONFIGURATION
# -------------------------------
INTERFACE = "h1-eth0"   # safer than h1-eth0
CAPTURE_TIMEOUT = 5  # seconds

# -------------------------------
# LOAD MODEL
# -------------------------------
try:
    model = joblib.load("ddos_model.pkl")
    print("[INFO] Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit()

# -------------------------------
# TRACKING VARIABLES
# -------------------------------
ip_stats = defaultdict(lambda: {"pkts": 0, "bytes": 0})
start_time = time.time()

# -------------------------------
# PACKET PROCESSING
# -------------------------------
def process_packet(pkt):
    if IP in pkt:
        src_ip = pkt[IP].src
        ip_stats[src_ip]["pkts"] += 1
        ip_stats[src_ip]["bytes"] += len(pkt)

# -------------------------------
# FEATURE CALCULATION
# -------------------------------
def calculate_features():
    global start_time

    duration = max(time.time() - start_time, 1)

    total_pkts = sum(v["pkts"] for v in ip_stats.values())
    total_bytes = sum(v["bytes"] for v in ip_stats.values())

    if total_pkts == 0:
        return None, None

    pkts_per_sec = total_pkts / duration
    bytes_per_sec = total_bytes / duration
    avg_pkt_size = total_bytes / total_pkts
    src_ip_count = len(ip_stats)

    return [pkts_per_sec, bytes_per_sec, avg_pkt_size, src_ip_count], ip_stats

def update_dashboard(features, prediction):
    data = {
        "pkts_per_sec": features[0],
        "bytes_per_sec": features[1],
        "avg_pkt_size": features[2],
        "src_ip_count": features[3],
        "prediction": int(prediction),
        "status": "ATTACK" if prediction == 1 else "NORMAL"
    }

    with open("dashboard_data.json", "w") as f:
        json.dump(data, f)

# -------------------------------
# DETECTION FUNCTION
# -------------------------------
def detect_attack(features, ip_stats):
    X = np.array([features])

    print(f"\n[INFO] Features: {features}")

    try:
        prediction = model.predict(X)[0]
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return

    print(f"[DEBUG] Prediction: {prediction}")

    if prediction == 1:
        # Find attacker (most packets)
        attacker_ip = max(ip_stats, key=lambda x: ip_stats[x]["pkts"])

        print(f"🚨 DDOS DETECTED from {attacker_ip}")

        # Block attacker
        os.system(f"iptables -A INPUT -s {attacker_ip} -j DROP")
        print(f"⛔ Blocked IP: {attacker_ip}")
    
    else:
        print("✅ Normal traffic")
    update_dashboard(features, prediction)

# -------------------------------
# MAIN LOOP
# -------------------------------
def start_detection():
    global start_time

    print(f"[INFO] Monitoring on interface: {INTERFACE}")
    print("[INFO] Press Ctrl+C to stop\n")

    try:
        while True:
            sniff(iface=INTERFACE, timeout=CAPTURE_TIMEOUT, prn=process_packet)

            features, stats = calculate_features()

            if features is None:
                print("[INFO] No packets captured...")
                start_time = time.time()
                continue

            detect_attack(features, stats)

            # Reset stats
            ip_stats.clear()
            start_time = time.time()

    except KeyboardInterrupt:
        print("\n[INFO] Detection stopped.")

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    start_detection()
