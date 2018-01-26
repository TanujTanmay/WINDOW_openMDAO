import numpy as np
# from src.api import read_windrose

ref_height_wind_speed = 119.0 # [m]
alpha = 0.10  # Approximate mean value of fits to data in ECN report and paper of Tambke (EWEC 2004). Wind Shear Exponent.
hat = 2.05  # [m] Horns Rev website: Tides are approximately 1.2 m; Paper ICCE: appr. 1.5 m - A little more than half of this is taken for 'extrapolation'
lat = - 1.6  # [m] Horns Rev website: Tides are approximately 1.2 m; Paper ICCE: appr. 1.5 m - A little more than half of this is taken for 'extrapolation'
storm_surge_pos = 2.5  # [m] Paper ICCE
storm_surge_neg = - 0.5  # [m] Guess
Hs_50_year = 5.0  # [m] Horns Rev website: Highest value in graph of Hm0 is 4.3. Somewhat higher value taken for 'extrapolation' (note: graph is for 1 hour values) - Support structure design tool description derives Hs_1_year = 0.64 * Hs_50_year
Hs_1_year = 3.3  # [m] Horns Rev website: waves of more than 6 m height reached every year. Divided by 1.86 to estimate significant wave height
current_depth_averaged_50_year = 0.8  # [m/s] Horns Rev website: Currents may reach 0.8 m/s during storms (doesn't mention return period and whether this is depth averaged)
angle_wave_current_50_year = 20.0  # [degrees] (Arbitrary default)
water_density = 1025.0  # [kg/m^3]
d50_soil = 0.0002  # [m]  Values given as 'range' in baggrund8 IEA report and confirmed by figure 2.2. in fish IEA report
d90_soil = 0.0005  # [m]  Values given as 'range' in baggrund8 IEA report and confirmed by figure 2.2. in fish IEA report
friction_angle = 35.0  # [degrees] Depth averaged friction angle from 'friction angle-report'
submerged_unit_weight = 10000.0  # [N/m^3] From 'friction angle-report', lighter layer ignored, because it is at great depth.

# --------  Windrose  ----------------
# wind_directions, weibull_scales, weibull_shapes, direction_probabilities = read_windrose('Input/weibull_windrose_12unique.dat')
n_windrose_sectors = 12
wind_directions = [i * 30.0 for i in range(n_windrose_sectors)]
weibull_scales = [8.65, 8.86, 8.15, 9.98, 11.35, 10.96, 11.28, 11.50, 11.08, 10.94, 11.27, 10.55]
weibull_shapes = [2.11, 2.05, 2.35, 2.55, 2.81, 2.74, 2.63, 2.40, 2.23, 2.28, 2.29, 2.28]
direction_probabilities = [5.1, 4.3, 4.3, 6.6, 8.9, 6.5, 8.7, 11.5, 12.0, 11.1, 11.4, 9.6]
TI_ambient = 0.11

n_quadrilaterals = 2 # Number of quadrilaterals into which the wind farm area is divided.
areas = np.array([[[484178.55, 5732482.8], [500129.9, 5737534.4], [497318.1, 5731880.24], [491858.00, 5725044.75]], [[491858.00, 5725044.75], [497318.1, 5731880.24], [503163.37, 5729155.3], [501266.5, 5715990.05]]])  # Areas need to be defined in clockwise order starting on the "bottom left" corner, and grouped per quadrilateral considered.

def separation_equation_y(x):  # values y greater than f(x) use mapping 1, else mapping 0, in the case of two quadrilaterals.
    if len(areas) > 1:
        m = (areas[1][0][1] - areas[1][1][1]) / (areas[1][0][0] - areas[1][1][0])
        yy = areas[1][0][1]
        xx = areas[1][0][0]
        b = yy - m * xx
        return m * x + b
    else:
        return - 10000000.0  # Any value so that the entire farm is above this coordinate in the y-axis.