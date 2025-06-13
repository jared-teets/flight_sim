class Position:
    """
    Represents the pose (orientation and translation) of the motion platform.

    Attributes:
        psi (float): Yaw angle (radians).
        theta (float): Pitch angle (radians).
        phi (float): Roll angle (radians).
        T (list[float]): Translation vector [x, y, z] (meters).
    """

    def __init__(self, mid_height: float) -> None:
        """
        Initialize the Position object with default orientation and translation.

        :param mid_height: The initial z-position (height) of the platform (meters).
        """
        self.psi = 0.0    # Yaw angle (radians)
        self.theta = 0.0  # Pitch angle (radians)
        self.phi = 0.0    # Roll angle (radians)
        self.T = [0.0, 0.0, mid_height]  # Translation vector [x, y, z]

    def give_positions(self, oaa: list, T: list) -> None:
        """
        Update the orientation and translation of the platform.

        :param oaa: List of orientation angles [phi (roll), psi (yaw), theta (pitch)] in radians.
        :param T: Translation vector [x, y, z] in meters.
        """
        self.psi = oaa[1]
        self.phi = oaa[0]
        self.theta = oaa[2]
        self.T = T

    def display_positions(self) -> None:
        """
        Print the current orientation and translation of the platform.
        """
        print("psi (yaw): ", self.psi)
        print("phi (roll): ", self.phi)
        print("theta (pitch): ", self.theta)
        print("T (translation):", self.T)


