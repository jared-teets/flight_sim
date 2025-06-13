import canopen
import logging
import time
from canopen import Node

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

MAX_CURRENT_LIMIT_A = 20.0  # 20 Amps
MIN_TARGET_POSITION_MM = 0.0
MAX_TARGET_POSITION_MM = 360.0

def connect_can_network():
    network = canopen.Network()
    network.connect(bustype='socketcan', channel=CAN_INTERFACE, bitrate=500000)
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
        time.sleep(0.1)

def move_actuator(node, target_position_mm, current_limit_a=12.5, target_speed_pct=80.0, movement_profile=0, enable_motion=True):
    """
    Send a control command to the actuator using RPDO1.
    All values are converted to the correct resolution as per documentation.
    Enforces max current and position limits.
    """
    try:
        # Clamp values to allowed ranges
        target_position_mm = max(MIN_TARGET_POSITION_MM, min(MAX_TARGET_POSITION_MM, target_position_mm))
        current_limit_a = min(current_limit_a, MAX_CURRENT_LIMIT_A)

        # Convert to 0.1 units as per documentation
        target_position = int(target_position_mm * 10)  # mm to 0.1mm
        current_limit = int(current_limit_a * 10)       # A to 0.1A
        target_speed = int(target_speed_pct * 10)       # % to 0.1%
        control_bits = 0x01 if enable_motion else 0x00

        # Use canopen OD names from EDS
        node.rpdo[1]['Target Position'].raw = target_position
        node.rpdo[1]['Current Limit'].raw = current_limit
        node.rpdo[1]['Target Speed'].raw = target_speed
        node.rpdo[1]['Movement Profile'].raw = movement_profile
        node.rpdo[1]['Control Bits'].raw = control_bits
        node.rpdo[1].transmit()
        logger.info(
            "Node %d: Move command sent: pos=%.1fmm, curr=%.1fA, speed=%.1f%%, profile=%d, enable=%d",
            node.id, target_position_mm, current_limit_a, target_speed_pct, movement_profile, enable_motion
        )
    except Exception as e:
        logger.error("Error sending move command to node %d: %s", node.id, e)

def read_actuator_feedback(node):
    """
    Read feedback from the actuator using TPDO1.
    Returns (position_mm, current_a, speed_pct, motion_flags, error_flags)
    """
    try:
        node.tpdo[1].wait_for_reception(timeout=1.0)
        position = node.tpdo[1]['Measured Position'].raw / 10.0
        current = node.tpdo[1]['Measured Current'].raw / 10.0
        speed = node.tpdo[1]['Measured Speed'].raw / 10.0
        motion_flags = node.tpdo[1]['Motion Flags'].raw
        error_flags = node.tpdo[1]['Error Flags'].raw
        logger.info(
            "Node %d: Feedback: pos=%.1fmm, curr=%.1fA, speed=%.1f%%, motion=0x%02X, error=0x%02X",
            node.id, position, current, speed, motion_flags, error_flags
        )
        return position, current, speed, motion_flags, error_flags
    except Exception as e:
        logger.error("Error reading feedback from node %d: %s", node.id, e)
        return None, None, None, None, None

def log_all_feedback(nodes):
    for node in nodes.values():
        read_actuator_feedback(node)

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