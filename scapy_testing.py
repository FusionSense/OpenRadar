from scapy.all import * 
import numpy as np

IFACE_NAME = "Realtek USB GbE Family Controller #2"

capture = sniff(iface = IFACE_NAME, count = 100)
packet = capture[5]
raw = packet.lastlayer()
data = hexdump(raw)
packet_data = np.frombuffer(data[10:], dtype=np.uint16)
print(packet_data)