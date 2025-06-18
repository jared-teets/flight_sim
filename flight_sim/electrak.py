import canopen
import logging
import canalystii
import time
from canopen import Node
import os

# Configure logging for the electrak module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("electrak")

# File handler for logging to a file
file_handler = logging.FileHandler("electrak.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Path to the EDS file for the Electrak HD actuator
current_dir = os.getcwd()
EDS_FILE = os.path.join(current_dir, 'config/Electrak_HD-20200113.eds')
CAN_INTERFACE = 'canalystii'  # Change if your interface is different (e.g., 'usb0', 'pcan0', etc.)
CHANNEL = '0'
BITRATE = 500000 #500 baud
SCAN_TIMEOUT = 0.05  # seconds

MAX_CURRENT_LIMIT_A = 20.0  # 20 Amps
MIN_TARGET_POSITION_MM = 0.0
MAX_TARGET_POSITION_MM = 360.0


def move_actuator(
    node: canopen.Node,
    target_position_mm: float,
    current_limit_a: float = 12.5,
    target_speed_pct: float = 80.0,
    movement_profile: int = 0,
    enable_motion: bool = True,
) -> None:
    """
    Send a control command to the actuator using RPDO1.

    All values are converted to the correct resolution as per documentation.
    Enforces max current and position limits.

    :param node: canopen.Node instance for the actuator.
    :param target_position_mm: Target position in mm (float).
    :param current_limit_a: Current limit in Amps (float).
    :param target_speed_pct: Target speed as percent (float).
    :param movement_profile: Movement profile (int, see documentation).
    :param enable_motion: Whether to enable motion (bool).
    """
    try:
        # Clamp values to allowed ranges
        target_position_mm = max(
            MIN_TARGET_POSITION_MM, min(MAX_TARGET_POSITION_MM, target_position_mm)
        )
        current_limit_a = min(current_limit_a, MAX_CURRENT_LIMIT_A)

        # Convert to 0.1 units as per documentation
        target_position = int(target_position_mm * 10)  # mm to 0.1mm
        current_limit = int(current_limit_a * 10)  # A to 0.1A
        target_speed = int(target_speed_pct * 10)  # % to 0.1%
        control_bits = 0x01 if enable_motion else 0x00

        # Set RPDO1 mapped objects using EDS names
        node.rpdo[1]["Target Position"].raw = target_position
        node.rpdo[1]["Current Limit"].raw = current_limit
        node.rpdo[1]["Target Speed"].raw = target_speed
        node.rpdo[1]["Movement Profile"].raw = movement_profile
        node.rpdo[1]["Control Bits"].raw = control_bits
        node.rpdo[1].transmit()
        logger.info(
            "Node %d: Move command sent: pos=%.1fmm, curr=%.1fA, speed=%.1f%%, profile=%d, enable=%d",
            node.id,
            target_position_mm,
            current_limit_a,
            target_speed_pct,
            movement_profile,
            enable_motion,
        )
    except Exception as e:
        logger.error("Error sending move command to node %d: %s", node.id, e)


def read_actuator_feedback(node: canopen.Node) -> tuple:
    """
    Read feedback from the actuator using TPDO1.

    :param node: canopen.Node instance for the actuator.
    :return: Tuple (position_mm, current_a, speed_pct, motion_flags, error_flags)
    """
    try:
        node.tpdo[1].wait_for_reception(timeout=1.0)
        position = node.tpdo[1]["Measured Position"].raw / 10.0
        current = node.tpdo[1]["Measured Current"].raw / 10.0
        speed = node.tpdo[1]["Measured Speed"].raw / 10.0
        motion_flags = node.tpdo[1]["Motion Flags"].raw
        error_flags = node.tpdo[1]["Error Flags"].raw
        logger.info(
            "Node %d: Feedback: pos=%.1fmm, curr=%.1fA, speed=%.1f%%, motion=0x%02X, error=0x%02X",
            node,
            position,
            current,
            speed,
            motion_flags,
            error_flags,
        )
        return position, current, speed, motion_flags, error_flags
    except Exception as e:
        logger.error("Error reading feedback from node %d: %s", node, e)
        return None, None, None, None, None


def log_all_feedback(nodes: dict) -> None:
    """
    Log feedback for all nodes.

    :param nodes: Dictionary of node_id to canopen.Node.
    """
    for node in nodes:
        read_actuator_feedback(node)


def periodic_move(nodes: dict, positions: dict, interval: float = 1.0) -> None:
    """
    Periodically send move commands to all actuators.

    :param nodes: Dictionary of node_id to canopen.Node.
    :param positions: Dictionary of node_id to target position (mm).
    :param interval: Time between move commands (seconds).
    """
    logger.info("Starting periodic move commands...")
    while True:
        for node_id, node in nodes.items():
            pos = positions.get(node_id, 0)
            move_actuator(node, pos)
        time.sleep(interval)


def main() -> None:
    """
    Main entry point for actuator control and feedback logging.
    """
    network = canopen.Network()
    network.connect(interface=CAN_INTERFACE, channel=CHANNEL, bitrate=BITRATE)
    network.scanner.search()
    time.sleep(SCAN_TIMEOUT)
    nodes = network.scanner.nodes
    for node_id in nodes:
        print(f"Found nodes {node_id}!")
        node = network.add_node(node_id, EDS_FILE)
        network_node = network.values()
        print(f"Added nodes {network_node}!")
    # Send NMT start to all nodes
    network.nmt.state = 'OPERATIONAL'
    time.sleep(0.1) #wake up
    print("Network operational")
    
    log_all_feedback(nodes)
    
    network.disconnect()

    # Example: Move all actuators to 100mm, then 200mm, then 0mm in a loop
"""
        try:
            while True:
                for pos in [100, 200, 0]:
                    for node_id in nodes:
                        positions[node_id] = pos
                    periodic_move(nodes, positions, interval=2.0)
        except KeyboardInterrupt:
            logger.info("Exiting on user request.")
"""


if __name__ == "__main__":
    main()
