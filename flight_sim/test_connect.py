import canopen
import time
import os
import canopen.network
import logging

current_dir = os.getcwd()
EDS_FILE = os.path.join(current_dir, 'config/Electrak_HD-20200113.eds')
CAN_INTERFACE = 'canalystii'  # Change if your interface is different (e.g., 'usb0', 'pcan0', etc.)
CHANNEL = '0'
BITRATE = 500000 #500 baud
SCAN_TIMEOUT = 0.05  # seconds

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("electrak")
#network = canopen.Network()
#network.connect(interface='canalystii', channel='0', bitrate=500000)
"""node = network.add_node(6, '/home/pb/flight_sim/config/Electrak_HD-20200113.eds')
local_node = canopen.LocalNode(1, '/home/pb/flight_sim/config/Electrak_HD-20200113.eds')
for node_id in network:
    print(network[node_id])
"""
#EDS_FILE = '/home/pb/flight_sim/config/Electrak_HD-20200113.eds'
network = canopen.Network()
network.connect(interface=CAN_INTERFACE, channel=CHANNEL, bitrate=BITRATE)
network.connect(bustype="canalystii", channel="0", bitrate=500000)
logger.info("Connected to CAN network on interface %s", CAN_INTERFACE)

network.scanner.search()
time.sleep(SCAN_TIMEOUT)
nodes = network.scanner.nodes
for node_id in nodes:
    print(f"Found nodes {node_id}!")
    node = network.add_node(node_id, EDS_FILE)
    network_node = network.values()
    print(f"Added nodes {network_node}!")

network.disconnect()