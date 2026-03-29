#!/usr/bin/env python3

import numpy as np
import time
import os
from scapy.all import sniff, IP
import warnings

warnings.filterwarnings('ignore')

print("🚀 LIVE DDoS Detection + Mitigation System")
print("⏳ Capturing traffic in real-time... (Press Ctrl+C to stop)\n")

# -----------------------------
# Global counters and storage
# -----------------------------
packet_count = 0
byte_count = 0
src_ips = set()
start_time = time.time()

# -----------------------------
# Packet processing function
# -----------------------------
def process(packet):
    global packet_count, byte_count, src_ips, start_time

    # Only process IP packets
    if packet.haslayer(IP):
        packet_count += 1
        byte_count += len(packet)
        src_ips.add(packet[IP].src)

    duration = time.time() - start_time

    # Evaluate every 5 seconds
    if duration >= 5:
        if packet_count == 0:
            start_time = time.time()
            return

        # -----------------------------
        # Feature extraction
        # -----------------------------
        pkts_per_sec = packet_count / duration
        bytes_per_sec = byte_count / duration
        avg_pkt_size = byte_count / packet_count
        src_ip_count = len(src_ips)
        pps_ratio = pkts_per_sec / (bytes_per_sec + 1)

        # -----------------------------
        # RULE-BASED DETECTION (Stable)
        # -----------------------------
        if pkts_per_sec > 10:
            prob = 0.9   # attack
        elif pkts_per_sec > 5:
            prob = 0.5   # suspicious
        else:
            prob = 0.1   # normal

        # -----------------------------
        # Output and mitigation
        # -----------------------------
        print("\n📊 Traffic Summary (last 5s):")
        print(f"Packets/sec: {pkts_per_sec:.2f}, Bytes/sec: {bytes_per_sec:.2f}, Src IPs: {src_ip_count}")

        if prob > 0.7:
            print(f"🚨 DDOS DETECTED! Probability: {prob:.2%}")
            for ip in src_ips:
                if ip not in ["127.0.0.1", "10.0.0.1"]:
                    print(f"⛔ Blocking IP: {ip}")
                    os.system(f"iptables -A INPUT -s {ip} -j DROP")

        elif prob > 0.3:
            print(f"⚠️ Suspicious traffic detected. Probability: {prob:.2%}")

        else:
            print(f"✅ Normal traffic. Probability: {prob:.2%}")

        # -----------------------------
        # Reset counters
        # -----------------------------
        packet_count = 0
        byte_count = 0
        src_ips.clear()
        start_time = time.time()

# -----------------------------
# Start sniffing packets
# -----------------------------
try:
    sniff(iface="h1-eth0", prn=process, store=0)
except KeyboardInterrupt:
    print("\n🛑 Stopping detector...")
    print("⚠️ Flush iptables after test: sudo iptables -F")
