import numpy as np
import matplotlib.pyplot as plt
from aqsRC import interpolated

# ---------- Regression ----------
def fit_quadratic_surface(x, y, z):
    A = np.column_stack([
        x**2,
        y**2,
        x*y,
        x,
        y,
        np.ones_like(x)
    ])
    coeffs, _, _, _ = np.linalg.lstsq(A, z, rcond=None)
    return coeffs

def quadratic_surface(x, y, coeffs):
    a, b, c, d, e, f = coeffs
    return a*x**2 + b*y**2 + c*x*y + d*x + e*y + f


# ---------- Beispiel-Daten ----------
np.random.seed(0)

x = np.random.uniform(-5, 5, 300)
y = np.random.uniform(-5, 5, 300)
# x = np.random.uniform(-5, 5, 60)
# y = np.random.uniform(-5, 5, 60)

z = (
    1.5 * x**2
    + 0.7 * y**2
    - 0.8 * x * y
    + 2 * x
    - y
    + 3
    + np.random.normal(0, 3, size=x.shape)
)

##############################################
import interpolated2
from interpolated2 import Interpolator, aqs6
interp = Interpolator(aqs6)

x = interp.data[:, 2]
y = interp.data[:, 3]
z = interp.usf_errs
# z = interp.us1_errs
#############################################

coeffs = fit_quadratic_surface(x, y, z)


# ---------- Fläche berechnen ----------
# X, Y = np.meshgrid(
#     np.linspace(-5, 5, 60),
#     np.linspace(-5, 5, 60)
# )
X, Y = np.meshgrid(
    np.linspace(500, 2500, 50),
    np.linspace(500, 2500, 50)
)
Z = quadratic_surface(X, Y, coeffs)


# ---------- Plot ----------
fig = plt.figure(figsize=(9, 7))
ax = fig.add_subplot(111, projection="3d")
# ax.set_zlim(0, .5)

# Punktewolke
ax.scatter(x, y, z, color="blue", s=10, alpha=0.5, label="Messpunkte")

# Regressionsfläche
ax.plot_surface(
    X, Y, Z,
    color="orange",
    alpha=0.6,
    edgecolor="none"
)

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("Quadratische Regressionsfläche")

plt.legend()
plt.tight_layout()
plt.show()
