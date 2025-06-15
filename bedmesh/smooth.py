import numpy as np
from bedmesh.parse import SurfaceMesh

def smooth_surface_laplacian(mesh: SurfaceMesh, iterations: int = 3) -> SurfaceMesh:
    """
    Выполняет лапласово сглаживание поверхности: каждая точка z[i,j] заменяется
    на среднее арифметическое своих 4-х соседей (без учёта краёв).

    Параметры:
        mesh: SurfaceMesh — исходная поверхность
        iterations: int — число итераций сглаживания

    Возвращает:
        Новый SurfaceMesh со сглаженной матрицей z
    """
    z = mesh.z.copy()
    for _ in range(iterations):
        z_new = z.copy()
        # внутренняя часть
        z_new[1:-1, 1:-1] = 0.25 * (
            z[:-2, 1:-1] + z[2:, 1:-1] +
            z[1:-1, :-2] + z[1:-1, 2:]
        )
        z = z_new

    z_top = float(np.max(z))
    return SurfaceMesh(x=mesh.x.copy(), y=mesh.y.copy(), z=z, z_top=z_top)

def smooth_surface_laplacian_partial(mesh: SurfaceMesh, iterations: int = 3, lam: float = 0.4) -> SurfaceMesh:
    """
    Выполняет лапласово сглаживание с контролем силы (lambda ∈ [0,1]):
    z[i,j] := (1 - lambda) * z[i,j] + lambda * среднее 4-х соседей

    Параметры:
        mesh: SurfaceMesh — исходная поверхность
        iterations: int — число итераций сглаживания
        lam: float — сила сглаживания (lambda)

    Возвращает:
        Новый SurfaceMesh со сглаженной матрицей z
    """
    z = mesh.z.copy()
    for _ in range(iterations):
        neighbors_mean = 0.25 * (
            z[:-2, 1:-1] + z[2:, 1:-1] +
            z[1:-1, :-2] + z[1:-1, 2:]
        )
        z_new = z.copy()
        z_new[1:-1, 1:-1] = (1 - lam) * z[1:-1, 1:-1] + lam * neighbors_mean
        z = z_new

    z_top = float(np.max(z))
    return SurfaceMesh(x=mesh.x.copy(), y=mesh.y.copy(), z=z, z_top=z_top)
