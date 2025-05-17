import numpy as np
import trimesh
from parse_bed_mesh import SurfaceMesh

def generate_stl_from_surface(mesh: SurfaceMesh, output_path: str) -> str:
    """
    Строит STL из сетки координат и матрицы высот.
    - mesh: объект SurfaceMesh с полями x, y, z, z_top
    - output_path: путь для сохранения STL
    """
    x_new = mesh.x
    y_new = mesh.y
    z_interp = mesh.z
    z_top = mesh.z_top

    res_x = len(x_new)
    res_y = len(y_new)
    resolution = res_x  # предполагаем квадратную сетку

    # Вершины
    vertices_bottom = [[x, y, z_interp[iy, ix]] for iy, y in enumerate(y_new) for ix, x in enumerate(x_new)]
    vertices_top = [[x, y, z_top] for iy, y in enumerate(y_new) for ix, x in enumerate(x_new)]
    offset_top = len(vertices_bottom)

    # Грани
    faces_bottom, faces_top = [], []
    for iy in range(resolution - 1):
        for ix in range(resolution - 1):
            i0 = iy * resolution + ix
            i1 = i0 + 1
            i2 = i0 + resolution
            i3 = i2 + 1
            faces_bottom += [[i0, i2, i1], [i1, i2, i3]]
            faces_top += [[i0 + offset_top, i1 + offset_top, i2 + offset_top],
                          [i1 + offset_top, i3 + offset_top, i2 + offset_top]]

    # Боковые стенки
    vertices_sides = []
    faces_sides = []

    def add_side(v0, v1, base_index):
        z0 = z_interp[v0[1], v0[0]]
        z1 = z_interp[v1[1], v1[0]]
        p0 = [x_new[v0[0]], y_new[v0[1]], z0]
        p1 = [x_new[v1[0]], y_new[v1[1]], z1]
        p2 = [x_new[v0[0]], y_new[v0[1]], z_top]
        p3 = [x_new[v1[0]], y_new[v1[1]], z_top]
        idx = base_index + len(vertices_sides)
        vertices_sides.extend([p0, p1, p2, p3])
        faces_sides.extend([[idx, idx + 1, idx + 2], [idx + 1, idx + 3, idx + 2]])

    for ix in range(resolution - 1):
        add_side((ix, 0), (ix + 1, 0), offset_top * 2)
        add_side((ix, resolution - 1), (ix + 1, resolution - 1), offset_top * 2)
    for iy in range(resolution - 1):
        add_side((0, iy), (0, iy + 1), offset_top * 2)
        add_side((resolution - 1, iy), (resolution - 1, iy + 1), offset_top * 2)

    vertices = np.array(vertices_bottom + vertices_top + vertices_sides)
    faces = faces_bottom + faces_top + faces_sides
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    mesh.export(output_path)
    return output_path
