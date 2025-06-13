import math

class Geometry:
    def __init__(self, radius_base, radius_platform, mid_length, min_length, range_val, sep_angle, sep_angle_platform):
        self.radius_base = radius_base
        self.radius_platform = radius_platform
        self.mid_length = mid_length
        self.min_length = min_length
        self.range_val = range_val
        self.sep_angle = sep_angle
        self.sep_angle_platform = sep_angle_platform

        # Initialize the arrays to store the geometry data
        self.base = [[0, 0, 0] for _ in range(6)]
        self.platform = [[0, 0, 0] for _ in range(6)]
        self.p = [[0, 0, 0] for _ in range(6)]
        self.b = [[0, 0, 0] for _ in range(6)]

        # Initialize geometry
        self.init_geometry()

    def find_height(self, radius_base, radius_platform, length, angle):
        # Implement or translate the find_height function based on your requirements
        # This is just a placeholder
        return math.sqrt(length**2 - (radius_base - radius_platform * math.cos(angle))**2)

    def init_geometry(self):
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

            self.base[i][0] = self.radius_base * math.sin(angle)
            self.base[i][1] = self.radius_base * math.cos(angle)
            self.platform[i][0] = self.radius_platform * math.sin(angle_p - math.pi / 3)
            self.platform[i][1] = self.radius_platform * math.cos(angle_p - math.pi / 3)

        for i in range(6):
            j = i
            k = (j + 5) % 6
            for dim in range(3):  # For x, y, z dimensions
                self.p[i][dim] = self.platform[j][dim]
                self.b[i][dim] = self.base[k][dim]

        # Calculate height based on mid-length of actuator
        rho = math.pi / 3.0 - 2.0 * (self.sep_angle / 2.0)
        self.mid_height = self.find_height(self.radius_base, self.radius_platform, self.mid_length, math.pi/3.0 - self.sep_angle/2 - self.sep_angle_platform/2)
        self.min_height = self.find_height(self.radius_base, self.radius_platform, self.min_length, math.pi/3.0 - self.sep_angle/2 - self.sep_angle_platform/2)

        self.act_min = self.min_length
        self.act_range = self.range_val


    def rot_matrix(self, psi, theta, phi):
        RB = [0] * 9
        RB[0] = math.cos(psi) * math.cos(theta)
        RB[1] = math.sin(psi) * math.cos(theta)
        RB[2] = -math.sin(theta)
        
        RB[3] = -math.sin(psi) * math.cos(phi) + math.cos(psi) * math.sin(theta) * math.sin(phi)
        RB[4] = math.cos(psi) * math.cos(phi) + math.sin(psi) * math.sin(theta) * math.sin(phi)
        RB[5] = math.cos(theta) * math.sin(phi)

        RB[6] = math.sin(psi) * math.sin(phi) + math.cos(psi) * math.sin(theta) * math.cos(phi)
        RB[7] = -math.cos(psi) * math.sin(phi) + math.sin(psi) * math.sin(theta) * math.cos(phi)
        RB[8] = math.cos(theta) * math.cos(phi)
        return RB
    

    def inverse_kinematics(self, pos):
        RB = self.rot_matrix(pos.psi, pos.theta, pos.phi)
        leg_lengths = []  # This will store the lengths of all legs

        for i in range(6):
            # Calculate the L vector for each leg
            L = [pos.T[j] + sum(self.p[i][k] * RB[j + k*3] for k in range(3)) - self.b[i][j] for j in range(3)]
            
            # Calculate the length of the leg from the L vector
            length = math.sqrt(sum(x ** 2 for x in L))
            leg_lengths.append(length)  # Store the leg length

        return leg_lengths  # Return the list of leg lengths

