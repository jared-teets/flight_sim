import xpc
# import Washout as washout
import Utilities as util

class Get_data:
    def __init__(self):
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
            "sim/time/paused"
        ]
        self.client = xpc.XPlaneConnect() # this is the __init__.py file within the xpc dir 
        self.a_nrml = None
        self.a_side = None
        self.a_axil = None
        self.faa = [None, None, None] #y,x,z
        self.oaa = [None, None, None] #phi, psi, theta
        self.paused = 0
        self.posi = None
        self.psiprev = self.client.getPOSI()[5]


    def run(self):
                values = self.client.getDREFs(self.drefs)
                self.get_values(values)
                # self.print_vals()

    def initialize_values(self): 
        self.posi = self.client.getPOSI()
        self.initpsi = self.posi[5]


    def get_values(self, values):
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
        psi = self.psiprev -  values[12][0]
        self.psiprev = values[12][0]
        phi = values[13][0]
        # theta = self.posi[3]
        # psi =  self.initpsi - self.posi[5]   
        # phi = self.posi[4]
        self.paused = values[14][0]

        ratio = util.MPD_fltlim(groundspeed * 0.2, 0.0, 1.0)
        self.a_nrml = util.MPD_fallout(fnrml_prop + fnrml_aero + fnrml_gear, -0.1, 0.1) / util.MPD_fltmax2(m_total, 1.0)
        self.a_side = (fside_prop + fside_aero + fside_gear) / util.MPD_fltmax2(m_total, 1.0) * ratio
        self.a_axil = (faxil_prop + faxil_aero + faxil_gear) / util.MPD_fltmax2(m_total, 1.0) * ratio
    #     theta = udp_state->theta; // pitch
	# psi=udp_state->psi; // yaw
	# phi=udp_state->phi; // roll
	# y=udp_state->a_side; // sideways
	# z=udp_state->a_nrml; // upward
	# x=udp_state->a_axil; // backward
        self.faa[0] =  -self.a_side
        self.faa[1] = self.a_axil
        self.faa[2] = self.a_nrml
        self.oaa[0] = phi
        self.oaa[1] = psi
        self.oaa[2] = theta
        


    def print_vals(self):
        print("Normal Acceleration: ", self.a_nrml)
        print("Side Acceleration: ", self.a_side)
        print("Axial Acceleration: ", self.a_axil)

# Optionally, to run the class, you could use:
if __name__ == '__main__':
    data_getter = Get_data()
    data_getter.run()



    
    

# import xpc
# import Washout as washout
# import Utilities as util
# drefs = ["sim/flightmodel/position/groundspeed",
# 	        "sim/flightmodel/forces/fnrml_prop",
# 	        "sim/flightmodel/forces/fside_prop",
# 	        "sim/flightmodel/forces/faxil_prop",
# 	        "sim/flightmodel/forces/fnrml_aero",
# 	        "sim/flightmodel/forces/fside_aero",
# 	        "sim/flightmodel/forces/faxil_aero",
# 	        "sim/flightmodel/forces/fnrml_gear",
# 	        "sim/flightmodel/forces/fside_gear",
# 	        "sim/flightmodel/forces/faxil_gear",
# 	        "sim/flightmodel/weight/m_total",
# 	        "sim/flightmodel/position/theta",
# 	        "sim/flightmodel/position/psi",
# 	        "sim/flightmodel/position/phi",
# 	        "sim/time/paused"]

# def main(): 
#     with xpc.XPlaneConnect() as client: 
#         while True: 
#             posi = client.getPOSI()
#             values = client.getDREFS(drefs)
#             length_vals = Dowashout(values)

# # Faa -> scale/limit -> (g) -> HP filter -> euler -> HP filter 2 -> integrate x2 -> Si
# # float ratio = MPD_fltlim(groundspeed*0.2,0.0,1.0);
# # float a_nrml= MPD_fallout(fnrml_prop+fnrml_aero+fnrml_gear,-0.1,0.1)/MPD_fltmax2(m_total,1.0);
# # float a_side= (fside_prop+fside_aero+fside_gear)/MPD_fltmax2(m_total,1.0)*ratio;
# # float a_axil= (faxil_prop+faxil_aero+faxil_gear)/MPD_fltmax2(m_total,1.0)*ratio;
# def Dowashout(values): 
#     fnrml_prop = values[1][0]
#     fnrml_aero = values[4][0]
#     fnrml_gear = values[7][0]
#     fside_prop = values[2][0]
#     fside_aero = values[5][0]
#     fside_gear = values[8][0]
#     faxil_prop = values[3][0]
#     faxil_aero = values[6][0]
#     faxil_gear = values[9][0]
#     m_total = values[10][0]
#     groundspeed = values[0][0]
#     ratio = util.MDP_fltlim(groundspeed*0.2,0.0,1.0)
#     a_nrml = util.MPD_fallout(fnrml_prop+fnrml_aero+fnrml_gear, -0.1, 0.1)/util.MPD_fltmax2(m_total,1.0)
#     a_side= (fside_prop+fside_aero+fside_gear)/MPD_fltmax2(m_total,1.0)*ratio
#     a_axil= (faxil_prop+faxil_aero+faxil_gear)/MPD_fltmax2(m_total,1.0)*ratio

# def printvals(values):
#     #print all the values



    


