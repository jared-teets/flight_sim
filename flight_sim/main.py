# Example integration of geometry.py, position.py, and washout.py

from geometry import Geometry
from Position import Position
from Washout import Washout
from Get_data import Get_data
import electrak
import logging
import time

# Configure logging for this script
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# 1. Initialize system
geometry = Geometry(
    radius_base=0.791,
    radius_platform=0.7835,
    mid_length=0.74343,
    min_length=0.59706,
    range_val=0.292,
    sep_angle=2.094,
    sep_angle_platform=1.753,
)
position = Position(mid_height=geometry.mid_height)
washout = Washout()
data_getter = Get_data()

# Initialize CAN network and actuators
network = electrak.connect_can_network()
try:
    node_ids = electrak.scan_devices(network)
    if not node_ids:
        logger.error("No CANopen nodes found. Exiting.")
        exit(1)
    nodes = electrak.add_nodes(network, node_ids)
    electrak.set_operational(network, nodes)

    # Main loop
    while True:
        # Get current acceleration and orientation (from Get_data.py)
        data_getter.run()
        faa = data_getter.faa  # [side, axial, normal]
        oaa = data_getter.oaa  # [phi, psi, theta]

        # Washout filter: process motion cues
        filtered_motion = washout.compute2(faa, oaa, position)

        # Update platform pose
        position.give_positions(oaa, filtered_motion)

        # Compute actuator lengths
        actuator_lengths = geometry.inverse_kinematics(position)

        # Send actuator lengths to each actuator over CAN and log the messages
        for idx, (node_id, node) in enumerate(nodes.items()):
            # Convert length from meters to mm for actuator command
            target_position_mm = actuator_lengths[idx] * 1000.0
            electrak.move_actuator(node, target_position_mm)
            logger.info(
                f"Sent actuator command to node {node_id}: target_position_mm={target_position_mm:.2f}"
            )

        # Wait for next cycle
        time.sleep(0.05)  # 20 Hz update rate

finally:
    network.disconnect()
    logger.info("Disconnected from CAN network.")
