import serial
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np


# make sure the 'COM#' is set according the Windows Device Manager
ser = serial.Serial('COM9', 9600, timeout=1)
time.sleep(2)

data = []

def print_serial():
    while True:
        line = ser.readline().decode()
        print(line)

def plot_static():
    for i in range(50):
        line = ser.readline()   # read a byte string
        if line:
            string = line.decode()  # convert the byte string to a unicode string
            num = int(string) # convert the unicode string to an int
            print(num)
            data.append(num) # add int to data list
    ser.close()

    # build the plot
    plt.plot(data)
    plt.xlabel('Time')
    plt.ylabel('Potentiometer Reading')
    plt.title('Potentiometer Reading vs. Time')
    plt.show()

xs = []
ys = []
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

def animate(i, xs, ys):
    line = ser.readline().decode()
    vals = line.split(',')

    xs.append(vals[0])
    ys.append(vals[1])

    ax.plot(xs, ys, label="Experimental Probability")
    ax.plot(xs, xs, label="Theoretical Probability")


ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1)
plt.show()