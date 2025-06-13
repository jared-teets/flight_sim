class Position:
    def __init__(self, mid_height):
        self.psi = 0.0
        self.theta = 0.0
        self.phi = 0.0
        self.T = [0.0, 0.0, mid_height]
    def give_positions(self, oaa, T):
        self.psi = oaa[1]
        self.phi = oaa[0]
        self.theta = oaa[2]
        self.T = T
    def display_positions(self):
        print("psi: ", self.psi)
        print("phi: ", self.phi)
        print("theta: ", self.theta)
        print("T:", self.T)


