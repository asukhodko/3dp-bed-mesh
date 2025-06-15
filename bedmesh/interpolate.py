import numpy as np
from scipy.interpolate import RectBivariateSpline

from bedmesh.parse import SurfaceMesh


def _make_interpolator_grid(mesh: SurfaceMesh) -> RectBivariateSpline:
    """
    Строит интерполятор RectBivariateSpline на основе SurfaceMesh.
    """
    return RectBivariateSpline(mesh.y, mesh.x, mesh.z, kx=3, ky=3)


def interpolate_surface(
        mesh: SurfaceMesh,
        resolution: int = 50
) -> SurfaceMesh:
    """
    Интерполяция внутри области bed_mesh (min..max).
    Использует безопасный метод .__call__().
    """
    interp = _make_interpolator_grid(mesh)

    x_min, x_max = float(np.min(mesh.x)), float(np.max(mesh.x))
    y_min, y_max = float(np.min(mesh.y)), float(np.max(mesh.y))

    x_new = np.linspace(x_min, x_max, resolution)
    y_new = np.linspace(y_min, y_max, resolution)

    z_interp = interp(y_new, x_new)
    z_top = float(np.max(z_interp))

    return SurfaceMesh(x=x_new, y=y_new, z=z_interp, z_top=z_top)


def interpolate_surface_with_extension(
        mesh: SurfaceMesh,
        resolution: int = 50,
        edge_offset: float = 0.0
) -> SurfaceMesh:
    """
    Интерполяция с экстраполяцией.
    Отступ edge_offset применяется от границ (0.0 .. full_extent) по X и Y.
    """
    interp = _make_interpolator_grid(mesh)

    extent_x = float(np.min(mesh.x)) + float(np.max(mesh.x))
    extent_y = float(np.min(mesh.y)) + float(np.max(mesh.y))

    x_min = 0.0 + edge_offset
    x_max = extent_x - edge_offset
    y_min = 0.0 + edge_offset
    y_max = extent_y - edge_offset

    x_new = np.linspace(x_min, x_max, resolution)
    y_new = np.linspace(y_min, y_max, resolution)

    z_interp = np.array([[interp.ev(y, x) for x in x_new] for y in y_new])
    z_top = float(np.max(z_interp))

    return SurfaceMesh(x=x_new, y=y_new, z=z_interp, z_top=z_top)
