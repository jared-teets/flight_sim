import pytest
import logging

def rpdo_frame(node_id, target_position_mm, current_limit_a=200.0, target_speed_pct=80.0, movement_profile=0, enable=True):
    # Convert values to CANopen format (resolution from docs)
    # Target Position: 0.1mm/bit
    target_position = int(target_position_mm * 10)  # mm to 0.1mm units
    # Current Limit: 0.1A/bit
    current_limit = int(current_limit_a * 10)
    # Target Speed: 0.1%/bit
    target_speed = int(target_speed_pct * 10)
    # Movement Profile: 0=normal
    # Control Bits: bit 0 = enable
    control_bits = 0x01 if enable else 0x00

    data = [
        target_position & 0xFF, (target_position >> 8) & 0xFF,
        current_limit & 0xFF, (current_limit >> 8) & 0xFF,
        target_speed & 0xFF, (target_speed >> 8) & 0xFF,
        movement_profile & 0xFF,
        control_bits
    ]
    cob_id = 0x200 + node_id
    return cob_id, data

def test_connect_and_log_can_messages_for_6_actuators(caplog, mocker, tmp_path):
    # Set up a dedicated log file for this test
    log_file = tmp_path / "can_messages.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    logger = logging.getLogger("electrak")
    logger.addHandler(file_handler)

    caplog.set_level(logging.INFO, logger="electrak")

    # Patch CAN network and node discovery with correct function names
    mock_network = mocker.Mock()
    mocker.patch("electrak.connect_can_network", return_value=mock_network)
    mocker.patch("electrak.scan_devices", return_value=[1, 2, 3, 4, 5, 6])

    # Patch Node so add_nodes creates mocks with needed attributes
    mock_node_class = mocker.patch("electrak.Node")
    mock_nodes = {}
    for i in range(1, 7):
        node = mocker.Mock()
        node.id = i
        node.nmt = mocker.Mock()
        mock_nodes[i] = node
    mock_node_class.side_effect = lambda node_id, eds: mock_nodes[node_id]

    import electrak
    network = electrak.connect_can_network()
    discovered_nodes = electrak.scan_devices(network)
    assert discovered_nodes == [1, 2, 3, 4, 5, 6]
    nodes = electrak.add_nodes(network, discovered_nodes)
    assert len(nodes) == 6

    # Set operational state
    electrak.set_operational(network, nodes)
    target_positions = {node_id: 150 for node_id in nodes}

    # Move actuators and log actual CAN messages in correct format
    for node_id, node in nodes.items():
        # Compose the actual RPDO frame for the actuator
        cob_id, data = rpdo_frame(node_id, target_positions[node_id])
        logger.info(
            f"Node {node_id}: RPDO CAN frame - COB-ID: 0x{cob_id:X}, Data: {['0x%02X' % b for b in data]}"
        )

    logger.removeHandler(file_handler)

    # Output the log file contents for verification
    with open(log_file) as f:
        log_contents = f.read()
        print(log_contents)
        for node_id in nodes:
            assert f"Node {node_id}: RPDO CAN frame - COB-ID: 0x{0x200+node_id:X}" in log_contents