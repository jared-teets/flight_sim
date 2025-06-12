import can
import canopen
import logging
import time
from canopen import Network, Node

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("electrak")

# File handler for logging to a file
file_handler = logging.FileHandler("electrak.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

EDS_FILE = "Electrak_HD-20200113.eds"
CAN_INTERFACE = "can0"  # Change if your interface is different (e.g., 'usb0', 'pcan0', etc.)
SCAN_TIMEOUT = 5  # seconds

def connect_can_network():
    network = canopen.Network()
    network.connect(bustype='socketcan', channel=CAN_INTERFACE, bitrate=250000)
    logger.info("Connected to CAN network on interface %s", CAN_INTERFACE)
    return network

def scan_devices(network):
    logger.info("Scanning for CANopen devices...")
    found_nodes = network.scanner.search(timeout=SCAN_TIMEOUT)
    logger.info("Found nodes: %s", found_nodes)
    return found_nodes

def add_nodes(network, node_ids):
    nodes = {}
    for node_id in node_ids:
        node = Node(node_id, EDS_FILE)
        network.add_node(node)
        nodes[node_id] = node
        logger.info("Added node %d with EDS %s", node_id, EDS_FILE)
    return nodes

def set_operational(network, nodes):
    logger.info("Setting all nodes to operational state...")
    for node in nodes.values():
        node.nmt.state = 'OPERATIONAL'
        logger.info("Node %d set to OPERATIONAL", node.id)

def read_actuator_feedback(node):
    # Example: Read position and current feedback (update indexes/subindexes as per EDS)
    try:
        position = node.sdo['Position feedback'].raw
        current = node.sdo['Current feedback'].raw
        logger.info("Node %d: Position=%s mm, Current=%s mA", node.id, position, current)
        return position, current
    except Exception as e:
        logger.error("Error reading feedback from node %d: %s", node.id, e)
        return None, None

def log_all_feedback(nodes):
    for node in nodes.values():
        read_actuator_feedback(node)

def move_actuator(node, target_position):
    # Example: Write target position (update index/subindex as per EDS)
    try:
        node.sdo['Target position'].raw = target_position
        logger.info("Node %d: Move command sent to position %s mm", node.id, target_position)
    except Exception as e:
        logger.error("Error sending move command to node %d: %s", node.id, e)

def periodic_move(nodes, positions, interval=1.0):
    logger.info("Starting periodic move commands...")
    while True:
        for node_id, node in nodes.items():
            pos = positions.get(node_id, 0)
            move_actuator(node, pos)
        time.sleep(interval)

def main():
    network = connect_can_network()
    try:
        found_nodes = scan_devices(network)
        if not found_nodes:
            logger.warning("No nodes found on the network.")
            return

        nodes = add_nodes(network, found_nodes)
        set_operational(network, nodes)

        # Example: Log feedback once
        log_all_feedback(nodes)

        # Example: Move all actuators to 100mm, then 200mm, then 0mm in a loop
        positions = {node_id: 100 for node_id in nodes}
        try:
            while True:
                for pos in [100, 200, 0]:
                    for node_id in nodes:
                        positions[node_id] = pos
                    periodic_move(nodes, positions, interval=2.0)
        except KeyboardInterrupt:
            logger.info("Exiting on user request.")

    finally:
        network.disconnect()
        logger.info("Disconnected from CAN network.")

if __name__ == "__main__":
    main()