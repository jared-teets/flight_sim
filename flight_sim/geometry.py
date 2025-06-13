import math


class Geometry:
    """
    Models the geometric and kinematic properties of a parallel robot platform (e.g., Stewart platform).
    Provides methods to initialize platform geometry and compute actuator lengths for a given pose.
    """

    def __init__(
        self,
        radius_base: float,
        radius_platform: float,
        mid_length: float,
        min_length: float,
        range_val: float,
        sep_angle: float,
        sep_angle_platform: float,
    ) -> None:
        """
        Initialize the Geometry object with platform and actuator parameters.

        :param radius_base: Radius of the base attachment circle (meters).
        :param radius_platform: Radius of the platform attachment circle (meters).
        :param mid_length: Mid-stroke actuator length (meters).
        :param min_length: Minimum actuator length (meters).
        :param range_val: Actuator movement range (meters).
        :param sep_angle: Separation angle between base attachment points (radians).
        :param sep_angle_platform: Separation angle between platform attachment points (radians).
        """
        self.radius_base = radius_base
        self.radius_platform = radius_platform
        self.mid_length = mid_length
        self.min_length = min_length
        self.range_val = range_val
        self.sep_angle = sep_angle
        self.sep_angle_platform = sep_angle_platform

        # 3D coordinates of the six base and platform attachment points
        self.base = [[0, 0, 0] for _ in range(6)]
        self.platform = [[0, 0, 0] for _ in range(6)]
        # Auxiliary arrays for kinematic calculations
        self.p = [[0, 0, 0] for _ in range(6)]
        self.b = [[0, 0, 0] for _ in range(6)]

        # Initialize geometry (computes attachment point positions and heights)
        self.init_geometry()

    def find_height(
        self,
        radius_base: float,
        radius_platform: float,
        length: float,
        angle: float,
    ) -> float:
        """
        Calculate the vertical distance (height) between the base and platform
        for a given actuator length and configuration.

        :param radius_base: Radius of the base circle.
        :param radius_platform: Radius of the platform circle.
        :param length: Actuator length.
        :param angle: Angle between attachment points (radians).
        :return: Height (meters).
        """
        # Uses Pythagorean theorem for triangle formed by actuator and radii
        return math.sqrt(
            length**2 - (radius_base - radius_platform * math.cos(angle)) ** 2
        )

    def init_geometry(self) -> None:
        """
        Compute the 3D coordinates of the six base and platform attachment points.
        Distributes points evenly in a circle, with separation angles applied.
        Also computes minimum and mid-stroke platform heights.
        """
        for i in range(6):
            angle = 2 * math.pi * (i // 2) / 3.0
            angle += math.pi
            angle_p = angle
            if i % 2:
                angle += self.sep_angle / 2.0
            else:
                angle -= self.sep_angle / 2.0

            if i % 2:
                angle_p += self.sep_angle_platform / 2.0
            else:
                angle_p -= self.sep_angle_platform / 2.0

            # Base attachment point (x, y, z=0)
            self.base[i][0] = self.radius_base * math.sin(angle)
            self.base[i][1] = self.radius_base * math.cos(angle)
            # Platform attachment point (x, y, z=0)
            self.platform[i][0] = self.radius_platform * math.sin(angle_p - math.pi / 3)
            self.platform[i][1] = self.radius_platform * math.cos(angle_p - math.pi / 3)

        # Assign platform and base points for kinematic calculations
        for i in range(6):
            j = i
            k = (j + 5) % 6
            for dim in range(3):  # For x, y, z
                self.p[i][dim] = self.platform[j][dim]
                self.b[i][dim] = self.base[k][dim]

        # Calculate platform heights for mid and min actuator lengths
        self.mid_height = self.find_height(
            self.radius_base,
            self.radius_platform,
            self.mid_length,
            math.pi / 3.0 - self.sep_angle / 2 - self.sep_angle_platform / 2,
        )
        self.min_height = self.find_height(
            self.radius_base,
            self.radius_platform,
            self.min_length,
            math.pi / 3.0 - self.sep_angle / 2 - self.sep_angle_platform / 2,
        )

        self.act_min = self.min_length
        self.act_range = self.range_val

    def rot_matrix(self, psi: float, theta: float, phi: float) -> list:
        """
        Compute a 3x3 rotation matrix (flattened) from Euler angles.

        :param psi: Yaw angle (radians).
        :param theta: Pitch angle (radians).
        :param phi: Roll angle (radians).
        :return: Flattened 3x3 rotation matrix as a list of 9 floats.
        """
        RB = [0] * 9
        RB[0] = math.cos(psi) * math.cos(theta)
        RB[1] = math.sin(psi) * math.cos(theta)
        RB[2] = -math.sin(theta)

        RB[3] = -math.sin(psi) * math.cos(phi) + math.cos(psi) * math.sin(
            theta
        ) * math.sin(phi)
        RB[4] = math.cos(psi) * math.cos(phi) + math.sin(psi) * math.sin(
            theta
        ) * math.sin(phi)
        RB[5] = math.cos(theta) * math.sin(phi)

        RB[6] = math.sin(psi) * math.sin(phi) + math.cos(psi) * math.sin(
            theta
        ) * math.cos(phi)
        RB[7] = -math.cos(psi) * math.sin(phi) + math.sin(psi) * math.sin(
            theta
        ) * math.cos(phi)
        RB[8] = math.cos(theta) * math.cos(phi)
        return RB

    def inverse_kinematics(self, pos) -> list:
        """
        Calculate the required actuator lengths for a given platform pose.

        :param pos: Position object with attributes:
            - psi: Yaw angle (radians)
            - theta: Pitch angle (radians)
            - phi: Roll angle (radians)
            - T: Translation vector [x, y, z] (meters)
        :return: List of six actuator lengths (meters).
        """
        RB = self.rot_matrix(pos.psi, pos.theta, pos.phi)
        leg_lengths = []

        for i in range(6):
            # Compute vector from base to platform attachment point for each leg
            L = [
                pos.T[j]
                + sum(self.p[i][k] * RB[j + k * 3] for k in range(3))
                - self.b[i][j]
                for j in range(3)
            ]
            # Euclidean norm gives actuator length
            length = math.sqrt(sum(x**2 for x in L))
            leg_lengths.append(length)

        return leg_lengths
