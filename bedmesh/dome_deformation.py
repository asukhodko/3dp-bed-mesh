import numpy as np

from bedmesh.parse import SurfaceMesh


def dome_deformation(x: float, y: float, Lx: float = 350.0, Ly: float = 350.0, delta: float = 0.3) -> float:
    fx = 1 - ((2 * x / Lx) - 1) ** 2
    fy = 1 - ((2 * y / Ly) - 1) ** 2
    return delta * fx ** 2 * fy ** 2


def apply_dome_compensation(
        mesh: SurfaceMesh,
        delta: float,
        compensation: float
) -> SurfaceMesh:
    """
    Применяет компенсацию куполообразной деформации к SurfaceMesh.

    :param mesh: исходная сетка
    :param delta: высота подъёма в центре (мм)
    :param compensation: коэффициент компенсации [0..1], где 1 — полная компенсация
    :return: новая сетка с модифицированной матрицей z
    """
    Lx = float(np.max(mesh.x)) - float(np.min(mesh.x))
    Ly = float(np.max(mesh.y)) - float(np.min(mesh.y))
    x0 = float(np.min(mesh.x))
    y0 = float(np.min(mesh.y))

    z_new = mesh.z.copy()

    for iy, y in enumerate(mesh.y):
        for ix, x in enumerate(mesh.x):
            fx = x - x0
            fy = y - y0
            correction = dome_deformation(fx, fy, Lx, Ly, delta)
            z_new[iy, ix] += compensation * correction

    z_top = float(np.max(z_new))
    return SurfaceMesh(x=mesh.x.copy(), y=mesh.y.copy(), z=z_new, z_top=z_top)
