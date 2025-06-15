import argparse
from pathlib import Path
from bedmesh.parse import parse_bed_mesh
from bedmesh.smooth import smooth_surface_laplacian_partial
from bedmesh.interpolate import interpolate_surface_with_extension
from bedmesh.apply_to_gcode import apply_bed_mesh_to_gcode

def main():
    parser = argparse.ArgumentParser(description="Apply bed mesh compensation to G-code file.")
    parser.add_argument("--mesh", required=True, help="Path to bed mesh text file.")
    parser.add_argument("--gcode", required=True, help="Path to input G-code file.")
    parser.add_argument("--out", required=True, help="Path to output G-code file.")
    parser.add_argument("--move-check-distance", type=float, default=5.0, help="Max XY distance between compensation points.")
    parser.add_argument("--split-delta-z", type=float, default=0.01, help="Max Z difference to keep segments combined.")
    parser.add_argument("--smooth-iterations", type=int, default=1, help="How many smoothing passes to apply.")
    parser.add_argument("--smooth-lambda", type=float, default=0.6, help="Smoothing factor (lambda).")
    parser.add_argument("--resolution", type=int, default=100, help="Interpolation resolution.")

    args = parser.parse_args()

    with open(args.mesh, "r") as f:
        mesh_text = f.read()

    surface = parse_bed_mesh(mesh_text)
    surface = smooth_surface_laplacian_partial(surface, iterations=args.smooth_iterations, lam=args.smooth_lambda)
    surface = interpolate_surface_with_extension(surface, resolution=args.resolution, edge_offset=0)

    gcode_lines = Path(args.gcode).read_text(encoding="utf-8").splitlines()
    compensated_lines = apply_bed_mesh_to_gcode(
        gcode_lines,
        surface,
        move_check_distance=args.move_check_distance,
        split_delta_z=args.split_delta_z,
    )

    Path(args.out).write_text("\n".join(compensated_lines) + "\n", encoding="utf-8")
    print(f"G-code saved to {args.out}")

if __name__ == "__main__":
    main()
