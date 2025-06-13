import sys

import xpc

import time


def monitor():
    with xpc.XPlaneConnect() as client:
        while True:
            start_time = time.time()
            posi = client.getPOSI();
            drefs = ["sim/flightmodel/position/local_ax", "sim/flightmodel/position/local_ay", "sim/flightmodel/position/local_az"]
            values = client.getDREFs(drefs)
            print("Time:", start_time)

            
            print(f"Pitch: {posi[3]}, roll: {posi[4]}, yaw: {posi[5]}, surge: {values[0][0]}, sway: {values[1][0]}, heave: {values[2][0]}")



            # print(f"Pitch: {posi[3]}, roll: {posi[4]}, yaw: {posi[5]})

              


if __name__ == "__main__":
    monitor()