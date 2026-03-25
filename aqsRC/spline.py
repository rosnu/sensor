import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import SmoothBivariateSpline

from sensor_data import sensors, aqs5, aqs6

data = np.array(aqs6['cal'])


x = data[:, 2]
y = data[:, 3]
z = data[:, 1]
z = data[:, 0]

# # Messpunkte
# np.random.seed(0)
# x = np.random.rand(100)
# y = np.random.rand(100)
# z = np.sin(3*x) * np.cos(3*y)

# Spline
spline = SmoothBivariateSpline(x, y, z, kx=2, ky=2)

# Auswerte-Gitter
xi = np.linspace(500, 2500, 100)
yi = np.linspace(500, 2500, 100)
Xi, Yi = np.meshgrid(xi, yi)
# Auswerte-Gitter

# xi = np.linspace(0, 500, 2500)
# yi = np.linspace(0, 500, 2500)
# Xi, Yi = np.meshgrid(xi, yi)

Zi = spline(xi, yi)
Zi = Zi.T   # <<< WICHTIG

# Plot
fig = plt.figure()
ax = fig.add_subplot(projection="3d")

ax.plot_surface(Xi, Yi, Zi, cmap="viridis", alpha=0.9)
ax.scatter(x, y, z, color="r", s=10)

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")

ax.set_zlim(0, 10)

plt.show()
