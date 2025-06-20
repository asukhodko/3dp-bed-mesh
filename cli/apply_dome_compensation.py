from bedmesh.dome_deformation import apply_dome_compensation
from bedmesh.parse import parse_bed_mesh
from bedmesh.smooth import smooth_surface_laplacian_partial


def format_mesh_points(mesh):
    lines = []
    for row in mesh.z:
        line = ", ".join(f"{val:.6f}" for val in row)
        lines.append(f"  {line}")
    return "points:\n" + "\n".join(lines)


def print_corrected_points_from_text(text: str):
    delta = 0.3
    compensations = [0.3, 0.5, 0.8]
    mesh = parse_bed_mesh(text)
    mesh = smooth_surface_laplacian_partial(mesh, iterations=1, lam=0.6)
    for compensation in compensations:
        corrected_mesh = apply_dome_compensation(mesh, delta=delta, compensation=compensation)
        print(f"Compensation: {compensation:.1f}")
        print(format_mesh_points(corrected_mesh))
        print(f"Z top: {corrected_mesh.z_top:.6f}\n")


if __name__ == "__main__":
    text = """
[bed_mesh shim-70%-with-plate-9x9]
version: 1
points: 
  -0.068000, -0.080000, -0.080000, -0.045000, -0.032000, -0.035000, -0.042000, 0.010000, 0.015000
  -0.069000, -0.090000, -0.067000, -0.074000, -0.072000, -0.062000, -0.099000, -0.095000, -0.062000
  -0.047000, -0.088000, -0.085000, -0.080000, -0.042000, -0.110000, -0.150000, -0.135000, -0.110000
  -0.072000, -0.089000, -0.060000, -0.025000, 0.010000, -0.057000, -0.125000, -0.152000, -0.117000
  -0.075000, -0.104000, -0.060000, -0.012000, -0.003000, -0.038000, -0.109000, -0.130000, -0.117000
  -0.119000, -0.119000, -0.079000, -0.075000, -0.110000, -0.075000, -0.080000, -0.107000, -0.120000
  -0.082000, -0.105000, -0.084000, -0.050000, -0.057000, -0.082000, -0.075000, -0.084000, -0.065000
  -0.062000, -0.090000, -0.010000, -0.005000, 0.008000, -0.020000, -0.013000, -0.003000, 0.057000
  0.053000, -0.007000, 0.033000, 0.068000, 0.096000, 0.103000, 0.108000, 0.100000, 0.173000
x_count: 9
y_count: 9
mesh_x_pps: 2
mesh_y_pps: 2
algo: bicubic
tension: 0.2
min_x: 5.0
max_x: 345.0
min_y: 5.0
max_y: 345.0
"""

    print_corrected_points_from_text(text)
