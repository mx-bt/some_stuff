def battery_life_fix(current_percentage):
    """
    Daten des LiPo 3S Akkus aus dem Roboter
    Kapazität 2400 mAh
    Leistung 25.92 Wh
    Nominale Ladespannung 10.8 V
    Nennspannung 4.2 V 
    Batterielebensdauer (Standby) 100 Minuten
    Batterielebensdauer (bei Verwendung) 35 Minuten 
    """

    # get numerical values from the robot user manual
    scaler = current_percentage / 100
    capacity_with_safety_charge = 2400 * 0.9 * scaler / 1000 # Ah
    rated_voltage = 4.2 # V
    power_consumption_robot_standby = 6.1 # W
    power_consumption_robot_usage = 17.5 # W

    # apply basic formulas for battery life approximation
    approximate_battery_life_standby = (capacity_with_safety_charge * rated_voltage / power_consumption_robot_standby) * 60 # min
    approximate_battery_life_usage = (capacity_with_safety_charge * rated_voltage / power_consumption_robot_usage) * 60 # min

    return approximate_battery_life_standby, approximate_battery_life_usage

# Your time and battery percentage data
#
def battery_life_linear_reg():

    import numpy as np # numerical operations, for the regression
    import matplotlib.pyplot as plt # for plotting
    import pandas as pd # for reading the data

    battery_data = pd.read_csv(r"C:\Users\Max\Documents\MOM\ws2324\mbtm_dz_showcase\battery_data.csv")
    battery_percentage = battery_data["battery_percentage"].tolist() 
    total_time = np.linspace(1, len(battery_percentage), len(battery_percentage))

    # fit a linear regression to the data
    # include only the last 60 seconds
    coefficients = np.polyfit(total_time[-60:], battery_percentage[-60:], 1)
    linear_reg = np.poly1d(coefficients) #  for plotting

    # Include safety charge of 10%
    equation = np.poly1d(coefficients) - 10
    roots = np.roots(equation)
    # print("Intersection points with y=10:", roots)

    # print("Int x axis", roots[0])
    # print("last time", total_time[-1])
     # minutes
    # print("Approx remaining time", remaining_time, " minutes")
    # Generate points for the fitted polynomial
    fit_x = np.linspace(min(total_time), max(total_time), 100)
    fit_y = linear_reg(fit_x)

    # Plot the original data and the fitted polynomial
    # limit y axis
    # plt.ylim(0, 100)
    # # plt.xlim(total_time[-120], total_time[-1]) # doesn't work
    # # Insert a horizontal line at y=10
    # plt.axhline(y=10, color='y', linestyle='-')
    # # label y=10 line as "Safety Charge"
    # plt.text(0, 15, 'Safety Charge', color='y')
    # plt.scatter(total_time, battery_percentage, label='Battery % / Time')
    # plt.plot(fit_x, fit_y, label='Linear Regression Robot', color='red')
    # # set title
    # plt.title('Statistical "ML" Battery Life Approximation')
    # plt.xlabel('Time [sec]')
    # plt.ylabel('Battery Percentage [%]')
    # plt.legend()
    # plt.show()

    remaining_time = int(round((roots[-1]-total_time[-1]) / 60))
    return remaining_time

if __name__ == "__main__":
    print(battery_life_linear_reg())