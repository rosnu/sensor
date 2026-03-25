import matplotlib.pyplot as plt
from scipy.interpolate import LinearNDInterpolator
import numpy as np

# Beispiel-Interpolator
np.random.seed(0)
x = np.random.rand(100)
y = np.random.rand(100)
z = np.sin(2*np.pi*x) * np.cos(2*np.pi*y)

# points = np.column_stack((x, y))
# interp = LinearNDInterpolator(points, z)

from interpolated import Interpolator,  aqs6
interp=Interpolator(aqs6).interpolatorUsf_err


# Aus dem Interpolator abgreifen
tri = interp.tri
pts = interp.points
vals = interp.values

# Plot
fig = plt.figure()
ax = fig.add_subplot(projection="3d")

ax.plot_trisurf(
    pts[:, 0],
    pts[:, 1],
    # vals,
    vals[:, 0],
    triangles=tri.simplices,
    alpha=0.85,
    linewidth=0.2,
)

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")

plt.show()








# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.spatial import Delaunay
# from scipy.interpolate import LinearNDInterpolator
#
# from interpolated import Interpolator,  data_aqs6
# interp2=Interpolator(data_aqs6)
#
# # Beispieldaten
# np.random.seed(0)
# x = np.random.rand(100)
# y = np.random.rand(100)
# z = np.sin(2*np.pi*x) * np.cos(2*np.pi*y)
#
# points = np.column_stack((x, y))
#
# # Interpolator (nur zur Klarheit – nicht zwingend nötig fürs Plotten)
# interp = LinearNDInterpolator(points, z)
#
# # Delaunay-Triangulierung im (x,y)-Raum
# tri = Delaunay(points)
#
# # Plot
# fig = plt.figure()
# ax = fig.add_subplot(projection="3d")
#
# # Triangulierte Fläche
# ax.plot_trisurf(
#     x, y, z,
#     triangles=tri.simplices,
#     alpha=0.85,
#     linewidth=0.2,
#     edgecolor="k"
# )
#
# # Stützpunkte
# ax.scatter(x, y, z, color="r", s=10)
#
# ax.set_xlabel("x")
# ax.set_ylabel("y")
# ax.set_zlabel("z")
#
# plt.show()
