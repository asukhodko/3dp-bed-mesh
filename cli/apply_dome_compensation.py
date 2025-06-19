from bedmesh.parse import parse_bed_mesh
from bedmesh.smooth import smooth_surface_laplacian_partial
from bedmesh.dome_deformation import apply_dome_compensation


def format_mesh_points(mesh):
    lines = []
    for row in mesh.z:
        line = ", ".join(f"{val:.6f}" for val in row)
        lines.append(f"  {line}")
    return "points:\n" + "\n".join(lines)


def generate_corrected_points_from_text(text: str, delta: float = 0.3, compensation: float = 0.5) -> str:
    mesh = parse_bed_mesh(text)
    mesh = smooth_surface_laplacian_partial(mesh, iterations=1, lam=0.6)
    mesh = apply_dome_compensation(mesh, delta=delta, compensation=compensation)
    return format_mesh_points(mesh)


if __name__ == "__main__":
    text = """
[bed_mesh PETG shim, 120C]
version: 1
points: 
  -0.156000, 0.025000, 0.054000, 0.022000, -0.003000, 0.032000, 0.112000, 0.141000, -0.061000
  0.032000, 0.090000, -0.013000, 0.005000, 0.055000, 0.030000, 0.104000, 0.064000, -0.108000
  0.060000, 0.117000, -0.011000, 0.029000, -0.036000, 0.041000, 0.110000, 0.099000, -0.091000
  0.054000, 0.047000, -0.030000, -0.008000, -0.031000, -0.031000, 0.094000, 0.125000, -0.021000
  0.052000, 0.072000, 0.002000, 0.009000, -0.014000, -0.023000, 0.077000, 0.134000, 0.026000
  0.114000, 0.029000, -0.028000, 0.002000, 0.006000, -0.001000, 0.015000, 0.115000, 0.112000
  0.115000, 0.012000, 0.007000, 0.104000, 0.047000, 0.059000, 0.094000, 0.084000, 0.112000
  0.104000, 0.042000, -0.013000, 0.024000, 0.001000, 0.001000, -0.023000, 0.101000, 0.139000
  0.112000, -0.016000, -0.093000, -0.048000, -0.020000, -0.009000, -0.031000, 0.044000, -0.056000
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

    corrected_output = generate_corrected_points_from_text(text, delta=0.3, compensation=1.0)
    print(corrected_output)
