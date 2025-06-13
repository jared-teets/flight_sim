import math
class Washout:
    def __init__(self):
        # Initialize the scale and limit parameters as attributes
        self.params = {
            'Faa_scale_lp': [0.8, 0.8, 0.8],
            'Faa_limit_lp': [10.0, 10.0, 10.0],
            'Oaa_scale_hp': [0.8, 0.8, 0.8],
            'Oaa_limit_hp': [100.0, 100.0, 100.0],
            'Faa_scale_hp': [0.8, 0.8, 0.8],
            'Faa_limit_hp': [5.0, 5.0, 5.0],
            'hpfilt_faa': [
                {'a1': 0.0, 'a2': 0.0, 'a3': 0.0, 'b1': 0.0, 'b2': 0.0},
                {'a1': 0.0, 'a2': 0.0, 'a3': 0.0, 'b1': 0.0, 'b2': 0.0},
                {'a1': 0.0, 'a2': 0.0, 'a3': 0.0, 'b1': 0.0, 'b2': 0.0}
            ],
            'hpfilt_faa_c': [
                {'a1': 0.0, 'a2': 0.0, 'a3': 0.0, 'b1': 0.0, 'b2': 0.0},
                {'a1': 0.0, 'a2': 0.0, 'a3': 0.0, 'b1': 0.0, 'b2': 0.0},
                {'a1': 0.0, 'a2': 0.0, 'a3': 0.0, 'b1': 0.0, 'b2': 0.0}
            ]
        }
        # Initialize filter states for two cascades for each axis
        self.fs = [
            {'in_prev': [0.0, 0.0], 'out_prev': [0.0, 0.0]} for _ in range(6)
        ]

        self.faa_sum = [0.0, 0.0, 0.0]
        self.faa_sum2 = [0.0, 0.0, 0.0]
        self.sample = 100

        #// Faa -> scale/limit -> (g) -> HP filter -> euler -> HP filter 2 -> integrate x2 -> Si
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
            faa_scaled = self.scale_and_limit(faa, 'F_HP')
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

        

        
    def scale_and_limit(self, input_values, sl):
        # Determine scale and limit based on sl parameter
        if sl == 'F_LP':
            scale = self.params['Faa_scale_lp']
            limit = self.params['Faa_limit_lp']
        elif sl == 'F_O':
            scale = self.params['Oaa_scale_hp']
            limit = self.params['Oaa_limit_hp']
        elif sl == 'F_HP':
            scale = self.params['Faa_scale_hp']
            limit = self.params['Faa_limit_hp']

        # Initialize the output list
        output = [0, 0, 0]

        # Apply limit
        for i in range(3):
            output[i] = input_values[i]
            if input_values[i] > limit[i]:
                output[i] = limit[i]
            elif input_values[i] < -limit[i]:
                output[i] = -limit[i]

        # Apply scale
        for i in range(3):
            output[i] *= scale[i]

        return output
    
    def sub_g(self, input_values, pos):
        output = [0, 0, 0]
        g = 9.8  # Acceleration due to gravity in m/s^2
        output[0] = input_values[0] - g * math.sin(pos.theta)
        output[1] = input_values[1] + g * math.cos(pos.theta) * math.sin(pos.phi)
        output[2] = input_values[2] + g * math.cos(pos.theta) * math.cos(pos.phi)
        return output
    
    def filter(self, cf, in_val, fs):
        ret = (cf['a1'] * in_val + cf['a2'] * fs['in_prev'][0] + cf['a3'] * fs['in_prev'][1] -
               cf['b1'] * fs['out_prev'][0] - cf['b2'] * fs['out_prev'][1])
        # Update filter state
        fs['in_prev'][1] = fs['in_prev'][0]
        fs['in_prev'][0] = in_val
        fs['out_prev'][1] = fs['out_prev'][0]
        fs['out_prev'][0] = ret
        return ret

    def lp_filter_faa(self, in_vals):
        out = [0.0, 0.0, 0.0]
        for i in range(3):
            out[i] = self.filter(self.params['lpfilt_faa'][i], in_vals[i], self.fs[i])
        return out

    def hp_filter_faa(self, in_vals):
        Faa_hp = [0.0, 0.0, 0.0]
        out = [0.0, 0.0, 0.0]
        # First biquad cascade
        for i in range(3):
            Faa_hp[i] = self.filter(self.params['hpfilt_faa'][i], in_vals[i], self.fs[i*2])
        # Second cascade
        for i in range(3):
            out[i] = self.filter(self.params['hpfilt_faa_c'][i], Faa_hp[i], self.fs[i*2+1])
        return out
    
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

    def faa_rot(self, input_values, pos):
        out = [0, 0, 0]
        RB = self.rot_matrix(pos.psi, pos.theta, pos.phi)
        for i in range(3):
            out[i] = RB[i] * input_values[0] + RB[i+3] * input_values[1] + RB[i+6] * input_values[2]
        return out
    
    def integrate2x(self, input_values):
        for i in range(3):
            self.faa_sum[i] += input_values[i] * (1.0 / self.sample)
            self.faa_sum2[i] += self.faa_sum[i] * (1.0 / self.sample)
            

