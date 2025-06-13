import logging
import os
from datetime import datetime

import Utilities as util
import xpc


class Get_data:
    """
    Retrieves and processes flight data from X-Plane using XPlaneConnect.
    Computes normalized accelerations and orientation angles for use in motion cueing and platform control.
    Logs all input data to a unique file in the data directory.
    """

    def __init__(self):
        """
        Initialize the Get_data object, set up datarefs, logging, and prepare state variables.
        """
        # List of X-Plane datarefs to query (see X-Plane Data Output settings)
        self.drefs = [
            # within X-Plane, go to settings -> Data Output -> Dataref Read/Write
            "sim/flightmodel/position/groundspeed",
            "sim/flightmodel/forces/fnrml_prop",
            "sim/flightmodel/forces/fside_prop",
            "sim/flightmodel/forces/faxil_prop",
            "sim/flightmodel/forces/fnrml_aero",
            "sim/flightmodel/forces/fside_aero",
            "sim/flightmodel/forces/faxil_aero",
            "sim/flightmodel/forces/fnrml_gear",
            "sim/flightmodel/forces/fside_gear",
            "sim/flightmodel/forces/faxil_gear",
            "sim/flightmodel/weight/m_total",
            "sim/flightmodel/position/theta",
            "sim/flightmodel/position/psi",
            "sim/flightmodel/position/phi",
            "sim/time/paused",
        ]
        # XPlaneConnect client for communication with X-Plane
        self.client = xpc.XPlaneConnect()
        # Acceleration components (normal, side, axial)
        self.a_nrml = None
        self.a_side = None
        self.a_axil = None
        # Acceleration and orientation arrays for downstream processing
        self.faa = [None, None, None]  # [side, axial, normal]
        self.oaa = [None, None, None]  # [phi, psi, theta]
        # Pause state (0 = running, 1 = paused)
        self.paused = 0
        # Last position and previous psi for delta calculation
        self.posi = None
        self.psiprev = self.client.getPOSI()[5]

        # Setup logging to a unique file in the data directory
        data_dir = os.path.join(os.path.dirname(__file__), "../data")
        os.makedirs(data_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"get_data_{timestamp}.log"
        log_path = os.path.join(data_dir, log_filename)
        self.logger = logging.getLogger(f"GetDataLogger_{timestamp}")
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(log_path)
        formatter = logging.Formatter("%(asctime)s %(message)s")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.propagate = False  # Prevent double logging

        # Write header for CSV-style log
        header = (
            "groundspeed,fnrml_prop,fside_prop,faxil_prop,fnrml_aero,fside_aero,"
            "faxil_aero,fnrml_gear,fside_gear,faxil_gear,m_total,theta,psi,phi,paused"
        )
        self.logger.info(header)

    def run(self) -> None:
        """
        Fetch the latest dataref values from X-Plane, log them, and process them.
        """
        values = self.client.getDREFs(self.drefs)
        # Flatten and log the raw input values
        flat_values = [str(v[0]) for v in values]
        self.logger.info(",".join(flat_values))
        self.get_values(values)

    def initialize_values(self) -> None:
        """
        Initialize position and psi values from X-Plane.
        """
        self.posi = self.client.getPOSI()
        self.initpsi = self.posi[5]

    def get_values(self, values: list) -> None:
        """
        Extract and process acceleration and orientation values from X-Plane datarefs.

        :param values: List of lists, each containing the value(s) for a dataref.
        """
        # Extract raw values from datarefs
        groundspeed = values[0][0]
        fnrml_prop = values[1][0]
        fside_prop = values[2][0]
        faxil_prop = values[3][0]
        fnrml_aero = values[4][0]
        fside_aero = values[5][0]
        faxil_aero = values[6][0]
        fnrml_gear = values[7][0]
        fside_gear = values[8][0]
        faxil_gear = values[9][0]
        m_total = values[10][0]
        theta = values[11][0]
        # Calculate change in psi (yaw) since last update
        psi = self.psiprev - values[12][0]
        self.psiprev = values[12][0]
        phi = values[13][0]
        self.paused = values[14][0]

        # Compute normalization ratio based on groundspeed
        ratio = util.MPD_fltlim(groundspeed * 0.2, 0.0, 1.0)
        # Compute normalized accelerations (with limiting and normalization)
        self.a_nrml = util.MPD_fallout(
            fnrml_prop + fnrml_aero + fnrml_gear, -0.1, 0.1
        ) / util.MPD_fltmax2(m_total, 1.0)
        self.a_side = (
            (fside_prop + fside_aero + fside_gear)
            / util.MPD_fltmax2(m_total, 1.0)
            * ratio
        )
        self.a_axil = (
            (faxil_prop + faxil_aero + faxil_gear)
            / util.MPD_fltmax2(m_total, 1.0)
            * ratio
        )

        # Assign processed values to arrays for downstream modules
        # faa: [side, axial, normal], oaa: [phi, psi, theta]
        self.faa[0] = -self.a_side
        self.faa[1] = self.a_axil
        self.faa[2] = self.a_nrml
        self.oaa[0] = phi
        self.oaa[1] = psi
        self.oaa[2] = theta

    def print_vals(self) -> None:
        """
        Print the current normalized acceleration values for debugging.
        """
        print("Normal Acceleration: ", self.a_nrml)
        print("Side Acceleration: ", self.a_side)
        print("Axial Acceleration: ", self.a_axil)


# Optionally, to run the class directly:
if __name__ == "__main__":
    data_getter = Get_data()
    data_getter.run()
