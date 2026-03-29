import joblib
from scapy.all import sniff, IP
from collections import defaultdict
import time
import pandas as pd
import numpy as np

# Load PRODUCTION model
model = joblib.load('ddos_model_production.pkl')
print("🚀 95.2% XGBoost LIVE DDoS DETECTOR STARTED")
print("📊 Waiting for Mininet traffic... (Ctrl+C to stop)")

flows = defaultdict(lambda: {'pkts': 0, 'bytes': 0, 'dur': 0, 'src': None})
start_time = time.time()

def packet_handler(pkt):
    global start_time
    if IP in pkt:
        key = (pkt[IP].src, pkt[IP].dst)
        flows[key]['pkts'] += 1
        flows[key]['bytes'] += len(pkt)
        flows[key]['dur'] = time.time() - start_time
        flows[key]['src'] = pkt[IP].src
        
        # Analyze every 50 packets
        if sum(f['pkts'] for f in flows.values()) % 50 == 0:
            analyze_flows()

def analyze_flows():
    features = []
    for flow, stats in flows.items():
        features.append([
            stats['pkts'] / max(stats['dur'], 1),      # pkts_per_sec
            stats['bytes'] / max(stats['dur'], 1),     # bytes_per_sec  
            stats['bytes'] / max(stats['pkts'], 1),    # avg_pkt_size
            1.0,                                       # src_ip_count (simplified)
            stats['dur'],                              # duration
            stats['pkts'] / 100.0                      # pps_ratio
        ])
    
    if features:
        df = pd.DataFrame(features)
        prob = model.predict_proba(df.tail(1))[0][1]  # DDoS probability
        
        src_ip = flows[list(flows.keys())[0]]['src'] if flows else "unknown"
        if prob > 0.7:
            print(f"🚨 DDoS ALERT! BLOCK {src_ip} (prob: {prob:.1%})")
        elif prob > 0.3:
            print(f"⚠️  Suspicious: {src_ip} (prob: {prob:.1%})")
        else:
            print(f"✅ Normal: {src_ip} (prob: {prob:.1%})")

# Start sniffing
print("\n🎯 LIVE MONITORING ACTIVE - Start Mininet now!")
sniff(prn=packet_handler, store=0, count=2000)
