from Get_data import Get_data
from geometry import Geometry
from Position import Position
from Washout import Washout
import time
import matplotlib.pyplot as plt

class MainClass:
    def __init__(self):
        self.data_getter = Get_data()
        self.platform_geometry = Geometry(radius_base=0.791, radius_platform=0.7835, mid_length=0.74343 #min_length+(range_val/2),
        min_length=0.59706, range_val=0.292, sep_angle=2.094, sep_angle_platform=1.753)
        self.position = Position(self.platform_geometry.mid_length)
        self.washout = Washout()
        self.arrays = []
      

    def start(self):
        self.platform_geometry.init_geometry()
        start_time = time.time()
        flag = 0
        # self.data_getter.initialize_values()
        while True:
            self.data_getter.run() # This calls the getDREFs method from init.py
            if self.data_getter.paused == 0:
                T = self.washout.compute2(self.data_getter.faa, self.data_getter.oaa, self.position)
                #print("T:", T)
                # print(type(T[0]))
                self.position.give_positions(self.data_getter.oaa, T)
                lengths = self.platform_geometry.inverse_kinematics(self.position)
                self.arrays.append(lengths) # appears that lengths will be converted to can bus
                print("Lengths:", lengths)
                
            end_time = time.time()
            print("Time:", end_time)
            # if (end_time - start_time) > 10 and flag == 0:
            #    self.plot_graph()
            #    flag = 1
           
            # self.position.display_positions()
            # print("Lengths:", lengths)
            # self.data_getter.print_vals()
            time.sleep(1)  # Wait for 1 second before the next call
    
    def plot_graph(self):
        print("-------------------Plotting--------------")
        x_min = min(min(array) for array in self.arrays)
        x_max = max(max(array) for array in self.arrays)
        y_min = min(min(array) for array in self.arrays)
        y_max = max(max(array) for array in self.arrays)
        transposed_arrays = list(zip(*self.arrays))


"""
# Plotting
        plt.figure(figsize=(20, 10))  # Adjust the figure size if needed
        # for i, array in enumerate(transposed_arrays):
        #     plt.plot(array, label=f'Array {i+1}')

        for i, values in enumerate(transposed_arrays):
            plt.plot([i] * len(values), values, 'o', label=f'Index {i+1}')

# Plot lines
        for i in range(len(transposed_arrays) - 1):
            plt.plot([i, i + 1], [transposed_arrays[i][-1], transposed_arrays[i+1][0]], 'k--')

# Set axis limits
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)

        plt.xlabel('Index')
        plt.ylabel('Value')
        plt.title('Line Graphs of Arrays')
        plt.legend()
        plt.grid(True)
        plt.savefig('graph.png')
        plt.show()
"""


if __name__ == '__main__':
    main_instance = MainClass()
    main_instance.start()

#     Base mount point dia: 1.582 m
# Upper mounting point dia: 1.567 m 
# Base separation angle: 2.094 rad
# Platform separation angle: 1.753 rad
# Actuator range: 0.35 m (0.292 m active) Why is active length less than range? safety margin?
# Actuator mid: 0.14637 m
# Min length actuator: 0.54 m ( 0.59706 m active)
