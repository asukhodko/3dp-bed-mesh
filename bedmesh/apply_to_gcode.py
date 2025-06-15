from typing import List
from scipy.interpolate import RectBivariateSpline
from typing import Dict, Union
import math


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
