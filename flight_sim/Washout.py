import math


class Washout:
    """
    Implements a washout filter for motion cueing in a motion platform.
    Processes acceleration and orientation data to generate actuator commands.
    """

    def __init__(self):
        """
        Initialize washout filter parameters, filter states, and accumulators.
        """
        # Filter and scaling parameters for each axis
        self.params = {
            "Faa_scale_lp": [0.8, 0.8, 0.8],
            "Faa_limit_lp": [10.0, 10.0, 10.0],
            "Oaa_scale_hp": [0.8, 0.8, 0.8],
            "Oaa_limit_hp": [100.0, 100.0, 100.0],
            "Faa_scale_hp": [0.8, 0.8, 0.8],
            "Faa_limit_hp": [5.0, 5.0, 5.0],
            "hpfilt_faa": [
                {"a1": 0.0, "a2": 0.0, "a3": 0.0, "b1": 0.0, "b2": 0.0},
                {"a1": 0.0, "a2": 0.0, "a3": 0.0, "b1": 0.0, "b2": 0.0},
                {"a1": 0.0, "a2": 0.0, "a3": 0.0, "b1": 0.0, "b2": 0.0},
            ],
            "hpfilt_faa_c": [
                {"a1": 0.0, "a2": 0.0, "a3": 0.0, "b1": 0.0, "b2": 0.0},
                {"a1": 0.0, "a2": 0.0, "a3": 0.0, "b1": 0.0, "b2": 0.0},
                {"a1": 0.0, "a2": 0.0, "a3": 0.0, "b1": 0.0, "b2": 0.0},
            ],
        }
        # Filter states for cascaded filters (two per axis)
        self.fs = [{"in_prev": [0.0, 0.0], "out_prev": [0.0, 0.0]} for _ in range(6)]

        # Accumulators for integration
        self.faa_sum = [0.0, 0.0, 0.0]
        self.faa_sum2 = [0.0, 0.0, 0.0]
        self.sample = 100

        # // Faa -> scale/limit -> (g) -> HP filter -> euler -> HP filter 2 -> integrate x2 -> Si

    # def compute2(self, faa, oaa, pos):
    #     faa_scaled = self.scale_and_limit(faa, 'F_HP')
    #     print("faa scaled:", faa_scaled)
    #     faa_subg = self.sub_g(faa_scaled, pos)
    #     print("faa subg:", faa_subg)
    #     faa_hp = self.hp_filter_faa(faa_subg)
    #     print("faa hp:", faa_hp)
    #     faa_rot = self.faa_rot(faa_hp, pos)
    #     print("faa rot:", faa_rot)
    #     faa_hp2 = self.hp_filter_faa(faa_rot)
    #     print("faa hp2:", faa_hp2)
    #     faa_integrate = self.integrate2x(faa_hp2, self.sample)
    #     print("faa integrate:", faa_integrate)
    #     return faa_integrate

    def compute2(self, faa, oaa, pos):
        self.faa_sum = [0.0, 0.0, 0.0]
        self.faa_sum2 = [0.0, 0.0, 0.0]
        for i in range(self.sample):
            faa_scaled = self.scale_and_limit(faa, "F_HP")
            # print("faa scaled:", faa_scaled)
            faa_subg = self.sub_g(faa_scaled, pos)
            # print("faa subg:", faa_subg)
            # faa_hp = self.hp_filter_faa(faa_subg)
            # print("faa hp:", faa_hp)
            faa_rot = self.faa_rot(faa_subg, pos)
            # print("faa rot:", faa_rot)
            # faa_hp2 = self.hp_filter_faa(faa_rot)
            # print("faa hp2:", faa_hp2)
            faa_integrate = self.integrate2x(faa_rot)
            # print("faa integrate:", faa_integrate)
        return self.faa_sum2

    def scale_and_limit(self, input_values: list, sl: str) -> list:
        """
        Apply scaling and limiting to input values.

        :param input_values: List of input values.
        :param sl: String key to select scale/limit parameters.
        :return: List of scaled and limited values.
        """
        if sl == "F_LP":
            scale = self.params["Faa_scale_lp"]
            limit = self.params["Faa_limit_lp"]
        elif sl == "F_O":
            scale = self.params["Oaa_scale_hp"]
            limit = self.params["Oaa_limit_hp"]
        elif sl == "F_HP":
            scale = self.params["Faa_scale_hp"]
            limit = self.params["Faa_limit_hp"]
        else:
            raise ValueError(f"Unknown scale/limit key: {sl}")

        # Initialize the output list
        output = [0, 0, 0]
        for i in range(3):
            output[i] = max(-limit[i], min(input_values[i], limit[i]))
            output[i] *= scale[i]
        return output

    def sub_g(self, input_values: list, pos) -> list:
        """
        Subtract gravity vector from acceleration based on platform orientation.

        :param input_values: List of accelerations.
        :param pos: Position object with orientation.
        :return: List of gravity-compensated accelerations.
        """
        output = [0, 0, 0]
        g = 9.8  # m/s^2
        output[0] = input_values[0] - g * math.sin(pos.theta)
        output[1] = input_values[1] + g * math.cos(pos.theta) * math.sin(pos.phi)
        output[2] = input_values[2] + g * math.cos(pos.theta) * math.cos(pos.phi)
        return output

    def filter(self, cf: dict, in_val: float, fs: dict) -> float:
        """
        Apply a biquad filter to a single value.

        :param cf: Filter coefficients (dict with a1, a2, a3, b1, b2).
        :param in_val: Input value.
        :param fs: Filter state (dict with in_prev, out_prev).
        :return: Filtered value.
        """
        ret = (
            cf["a1"] * in_val
            + cf["a2"] * fs["in_prev"][0]
            + cf["a3"] * fs["in_prev"][1]
            - cf["b1"] * fs["out_prev"][0]
            - cf["b2"] * fs["out_prev"][1]
        )
        # Update filter state
        fs["in_prev"][1] = fs["in_prev"][0]
        fs["in_prev"][0] = in_val
        fs["out_prev"][1] = fs["out_prev"][0]
        fs["out_prev"][0] = ret
        return ret

    def lp_filter_faa(self, in_vals: list) -> list:
        """
        Apply low-pass filter to acceleration values.

        :param in_vals: List of input values.
        :return: List of filtered values.
        """
        out = [0.0, 0.0, 0.0]
        for i in range(3):
            out[i] = self.filter(self.params["lpfilt_faa"][i], in_vals[i], self.fs[i])
        return out

    def hp_filter_faa(self, in_vals: list) -> list:
        """
        Apply cascaded high-pass filters to acceleration values.

        :param in_vals: List of input values.
        :return: List of filtered values.
        """
        Faa_hp = [0.0, 0.0, 0.0]
        out = [0.0, 0.0, 0.0]
        # First biquad cascade
        for i in range(3):
            Faa_hp[i] = self.filter(
                self.params["hpfilt_faa"][i], in_vals[i], self.fs[i * 2]
            )
        # Second cascade
        for i in range(3):
            out[i] = self.filter(
                self.params["hpfilt_faa_c"][i], Faa_hp[i], self.fs[i * 2 + 1]
            )
        return out

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

    def faa_rot(self, input_values: list, pos) -> list:
        """
        Rotate acceleration vector according to platform orientation.

        :param input_values: List of accelerations.
        :param pos: Position object with orientation.
        :return: Rotated acceleration vector.
        """
        out = [0, 0, 0]
        RB = self.rot_matrix(pos.psi, pos.theta, pos.phi)
        for i in range(3):
            out[i] = (
                RB[i] * input_values[0]
                + RB[i + 3] * input_values[1]
                + RB[i + 6] * input_values[2]
            )
        return out

    def integrate2x(self, input_values: list) -> None:
        """
        Double integration of input values (for position from acceleration).

        :param input_values: List of input values.
        """
        for i in range(3):
            self.faa_sum[i] += input_values[i] * (1.0 / self.sample)
            self.faa_sum2[i] += self.faa_sum[i] * (1.0 / self.sample)
