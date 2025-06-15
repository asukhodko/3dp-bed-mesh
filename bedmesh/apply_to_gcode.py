import math
from typing import List, Dict, Union

from scipy.interpolate import RectBivariateSpline

from bedmesh.parse import SurfaceMesh


def parse_gcode_line(line: str) -> Dict[str, Union[str, float]]:
    line = line.strip()
    if not line or line.startswith(";"):
        return {}

    parts = line.split()
    result: Dict[str, Union[str, float]] = {"cmd": parts[0]}
    for part in parts[1:]:
        if part.startswith(";"):
            break
        key = part[0]
        val = part[1:]
        try:
            result[key] = float(val)
        except ValueError:
            result[key] = val
    return result


def format_gcode_line(cmd: str, params: Dict[str, Union[str, float]]) -> str:
    parts = [cmd]
    for key in sorted(params.keys()):
        if key == "cmd":
            continue
        if isinstance(params[key], float):
            parts.append(f"{key}{params[key]:.5f}")
        else:
            parts.append(f"{key}{params[key]}")
    return " ".join(parts)


def interpolate_surface_z(interpolator: RectBivariateSpline, x: float, y: float) -> float:
    return float(interpolator(y, x)[0][0])


def split_move(start: Dict[str, float], end: Dict[str, float], max_dist: float) -> List[Dict[str, float]]:
    x0, y0, z0, e0 = start.get("X", 0), start.get("Y", 0), start.get("Z", 0), start.get("E", 0)
    x1, y1, z1, e1 = end.get("X", x0), end.get("Y", y0), end.get("Z", z0), end.get("E", e0)

    dx, dy = x1 - x0, y1 - y0
    dist = math.hypot(dx, dy)
    if dist <= max_dist or dist == 0:
        return [end]

    steps = math.ceil(dist / max_dist)
    segments = []
    for i in range(1, steps + 1):
        t = i / steps
        segment = {
            "X": x0 + t * dx,
            "Y": y0 + t * dy,
            "Z": z0 + t * (z1 - z0),
            "E": e0 + t * (e1 - e0)
        }
        segments.append(segment)
    return segments


def collapse_segments(segments: List[Dict[str, float]], split_delta_z: float) -> List[Dict[str, float]]:
    if not segments:
        return []

    result = [segments[0]]
    for seg in segments[1:]:
        prev = result[-1]
        if abs(seg["Z"] - prev["Z"]) > split_delta_z:
            result.append(seg)
        else:
            result[-1] = seg
    return result


def apply_bed_mesh_to_gcode(
        gcode_lines: List[str],
        surface: SurfaceMesh,
        move_check_distance: float = 1.0,
        split_delta_z: float = 0.01
) -> List[str]:
    interpolator = RectBivariateSpline(surface.y, surface.x, surface.z)
    output_lines = []
    last_pos: Dict[str, Union[float, None]] = {"X": 0.0, "Y": 0.0, "Z": 0.0, "E": 0.0, "F": None}

    for line in gcode_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(";") or stripped.startswith("M") or stripped.startswith(
                "T") or "EXCLUDE_OBJECT" in stripped:
            output_lines.append(line)
            continue

        cmd = parse_gcode_line(stripped)
        if not cmd or cmd["cmd"] not in {"G0", "G1"}:
            output_lines.append(line)
            continue

        start = last_pos.copy()
        end = last_pos.copy()
        end.update({k: v for k, v in cmd.items() if k in "XYZE"})

        segments = split_move(start, end, move_check_distance)

        prev = start
        for seg in segments:
            x = seg.get("X", prev["X"])
            y = seg.get("Y", prev["Y"])
            delta_z = interpolate_surface_z(interpolator, x, y)
            base_z = seg.get("Z", prev["Z"])
            seg["Z"] = base_z + delta_z
            prev = seg

        segments = collapse_segments(segments, split_delta_z)

        for seg in segments:
            merged = {**{"cmd": cmd["cmd"]}, **seg}
            if "F" in cmd:
                merged["F"] = cmd["F"]
            output_lines.append(format_gcode_line(merged["cmd"], merged))

        last_pos.update(end)

    return output_lines
