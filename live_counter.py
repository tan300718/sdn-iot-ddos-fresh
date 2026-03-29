import time
from scapy.all import sniff, IP
from collections import defaultdict

print("🔴 LIVE PACKET COUNTER - Real Mininet Traffic")
print("Start Mininet → see REAL pkts/sec → feed to demo")

flows = defaultdict(int)
start = time.time()

def pkt_handler(pkt):
    global start
    if IP in pkt:
        flows[pkt[IP].src] += 1
        elapsed = time.time() - start
        pps = len(flows) / elapsed if elapsed > 0 else 0
        print(f"\r🔴 LIVE: {len(flows)} pkts | {pps:.1f} pps | Top: {max(flows, key=flows.get)}", end="")

sniff(prn=pkt_handler, store=0, count=0, timeout=30)
