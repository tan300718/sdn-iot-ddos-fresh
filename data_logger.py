import pandas as pd
from scapy.all import sniff
from scapy.layers.inet import IP
from collections import defaultdict
import time
import os

# -------------------------------
# CONFIGURATION
# -------------------------------
INTERFACE = "h1-eth0"  # change to your Mininet host interface
OUTPUT_FILE = "real_ddos_data.csv"
LABEL = 1  # 0 = normal, 1 = attack
CAPTURE_TIMEOUT = 5  # seconds
MIN_PKTS = 1 # reduce for testing

# -------------------------------
# TRACKING
# -------------------------------
ip_stats = defaultdict(lambda: {"pkts": 0, "bytes": 0})
start_time = time.time()

# -------------------------------
# INITIALIZE CSV FILE
# -------------------------------
if not os.path.exists(OUTPUT_FILE):
    df = pd.DataFrame(columns=[
        "pkts_per_sec",
        "bytes_per_sec",
        "avg_pkt_size",
        "src_ip_count",
        "label"
    ])
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[INFO] Created new CSV file: {OUTPUT_FILE}")

# -------------------------------
# FEATURE CALCULATION
# -------------------------------
def calculate_features(ip_stats):
    global start_time
    duration = max(time.time() - start_time, 1)  # prevent divide by zero
    total_pkts = sum(v["pkts"] for v in ip_stats.values())
    total_bytes = sum(v["bytes"] for v in ip_stats.values())
    pkts_per_sec = total_pkts / duration
    bytes_per_sec = total_bytes / duration
    avg_pkt_size = total_bytes / total_pkts if total_pkts > 0 else 0
    src_ip_count = len(ip_stats)
    return [pkts_per_sec, bytes_per_sec, avg_pkt_size, src_ip_count]

# -------------------------------
# PACKET PROCESSING
# -------------------------------
def process_packet(pkt):
    if IP in pkt:
        src_ip = pkt[IP].src
        ip_stats[src_ip]["pkts"] += 1
        ip_stats[src_ip]["bytes"] += len(pkt)
        print(f"[PACKET] {src_ip} len={len(pkt)}")  # debug print

# -------------------------------
# SAVE FEATURES TO CSV
# -------------------------------
def save_to_csv(features):
    row = features + [LABEL]
    df = pd.DataFrame([row], columns=[
        "pkts_per_sec",
        "bytes_per_sec",
        "avg_pkt_size",
        "src_ip_count",
        "label"
    ])
    df.to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
    print(f"[INFO] Saved features to CSV: {row}")

# -------------------------------
# MONITORING LOOP
# -------------------------------
def start_logging():
    global start_time
    print(f"[INFO] Logging on {INTERFACE} | Label={LABEL} | Press Ctrl+C to stop")

    try:
        while True:
            sniff(iface=INTERFACE, timeout=CAPTURE_TIMEOUT, prn=process_packet)
            total_pkts = sum(v["pkts"] for v in ip_stats.values())

            if total_pkts < MIN_PKTS:
                print(f"[INFO] Only {total_pkts} pkts captured, skipping...")
                ip_stats.clear()
                start_time = time.time()
                continue

            features = calculate_features(ip_stats)
            print(f"[FEATURES] {features}")
            save_to_csv(features)
            print(f"[DEBUG] total_pkts={total_pkts}")
            # Reset for next cycle
            ip_stats.clear()
            start_time = time.time()

    except KeyboardInterrupt:
        print("\n[INFO] Logging stopped.")

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    start_logging()
