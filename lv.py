import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# Define the system of differential equations
def system(conditions, t, a, b, c, d, e, f, g):
    x, y, z = conditions
    dxdt = a * x - b * x * y
    dydt = -(c * y) + (d * x * y) - (e * y * z)
    dzdt = -f * z + g * y * z
    return [dxdt, dydt, dzdt]

# Parameters
a = 0.04 # grass growth rate
b = 0.01 # consumption of grass by sheep
c = 0.5 # sheep death rate
d = 0.02 # sheep birth from grass
e = 0.05 # sheep consumption rate by wolves
f = 0.08 # wolf death rate
g = 0.02 # wolf birth rate from sheep 

# Initial conditions
x0 = 200
y0 = 100
z0 = 50
initial_conditions = [x0, y0, z0]

t0 = 500
t = np.linspace(0, t0, t0*500)

solution = odeint(system, initial_conditions, t, args=(a, b, c, d, e, f, g))

plt.plot(t, solution[:, 0], label='x(t)')
plt.plot(t, solution[:, 1], label='y(t)')
plt.plot(t, solution[:, 2], label='z(t)')
plt.legend(loc='best')
plt.xlabel('t')
plt.ylabel('values')
plt.title('Solution of the differential equations')
plt.grid(True)
plt.show()
