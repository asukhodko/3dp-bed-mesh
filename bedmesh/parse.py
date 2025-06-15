import re
from dataclasses import dataclass

import numpy as np


@dataclass
class SurfaceMesh:
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    z_top: float

@dataclass
class _MeshMeta:
    x_count: int
    y_count: int
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    mesh_x_pps: int = 2
    mesh_y_pps: int = 2
    algo: str = "bicubic"
    tension: float = 0.2

@dataclass
class _BedMeshData:
    z_matrix: np.ndarray
    meta: _MeshMeta

def parse_bed_mesh(text: str) -> SurfaceMesh:
    """
    Парсит текст формата bed_mesh и возвращает SurfaceMesh.
    Поддерживает и ":" и "=".

    Пример ввода (работает и без '#*#'):
#*# [bed_mesh raw, 120C]
#*# version = 1
#*# points =
#*# 	0.093000, 0.276000, 0.416000, 0.528000, 0.571000, 0.549000, 0.464000, 0.331000, 0.149000
#*# 	0.041000, 0.219000, 0.356000, 0.456000, 0.486000, 0.441000, 0.326000, 0.176000, -0.004000
#*# 	0.036000, 0.206000, 0.321000, 0.416000, 0.439000, 0.394000, 0.259000, 0.131000, -0.054000
#*# 	0.001000, 0.206000, 0.309000, 0.409000, 0.431000, 0.369000, 0.256000, 0.126000, -0.074000
#*# 	-0.029000, 0.189000, 0.321000, 0.421000, 0.424000, 0.386000, 0.292000, 0.154000, -0.027000
#*# 	-0.024000, 0.201000, 0.334000, 0.441000, 0.469000, 0.441000, 0.339000, 0.211000, 0.022000
#*# 	0.034000, 0.214000, 0.376000, 0.574000, 0.543000, 0.521000, 0.421000, 0.304000, 0.133000
#*# 	0.098000, 0.299000, 0.451000, 0.621000, 0.651000, 0.644000, 0.553000, 0.431000, 0.261000
#*# 	0.187000, 0.381000, 0.578000, 0.786000, 0.883000, 0.841000, 0.734000, 0.624000, 0.463000
#*# x_count = 9
#*# y_count = 9
#*# mesh_x_pps = 2
#*# mesh_y_pps = 2
#*# algo = bicubic
#*# tension = 0.2
#*# min_x = 5.0
#*# max_x = 345.0
#*# min_y = 5.0
#*# max_y = 345.0
#*#
    """
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    result = {"z_matrix": [], "meta": {}}

    for line in lines:
        if line.startswith("#*#"):
            line = line[3:].lstrip()
        if line.startswith("points") or line.startswith("points:") or line.startswith("points ="):
            current_section = "points"
            continue
        elif re.match(r"^\[.*\]$", line) or line.startswith("version"):
            continue
        elif re.match(r"^[a-z_]+\s*[:=]", line):
            key, val = re.split(r"[:=]", line, maxsplit=1)
            key = key.strip()
            val = val.strip()
            try:
                parsed_val = int(val) if "." not in val else float(val)
            except ValueError:
                parsed_val = val
            result["meta"][key] = parsed_val
            continue
        if "current_section" in locals() and current_section == "points":
            values = list(map(float, line.split(",")))
            result["z_matrix"].append(values)

    z_matrix = np.array(result["z_matrix"])
    m = result["meta"]
    meta = _MeshMeta(
        x_count=int(m["x_count"]),
        y_count=int(m["y_count"]),
        min_x=float(m["min_x"]),
        max_x=float(m["max_x"]),
        min_y=float(m["min_y"]),
        max_y=float(m["max_y"]),
        mesh_x_pps=int(m.get("mesh_x_pps", 2)),
        mesh_y_pps=int(m.get("mesh_y_pps", 2)),
        algo=str(m.get("algo", "bicubic")),
        tension=float(m.get("tension", 0.2)),
    )

    x = np.linspace(meta.min_x, meta.max_x, meta.x_count)
    y = np.linspace(meta.min_y, meta.max_y, meta.y_count)
    z_top = float(np.max(z_matrix))

    return SurfaceMesh(x=x, y=y, z=z_matrix, z_top=z_top)
