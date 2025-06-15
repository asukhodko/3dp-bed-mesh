import unittest
import numpy as np
from bedmesh.parse import SurfaceMesh
from scipy.interpolate import RectBivariateSpline
from bedmesh.apply_to_gcode import parse_gcode_line, format_gcode_line, interpolate_surface_z, split_move


class TestBedMeshUtils(unittest.TestCase):
    def test_parse_and_format(self):
        line = "G1 X100.0 Y200.0 Z0.3 E1.25 F1800"
        parsed = parse_gcode_line(line)
        self.assertEqual(parsed["cmd"], "G1")
        self.assertEqual(parsed["X"], 100.0)
        self.assertEqual(parsed["Y"], 200.0)
        self.assertEqual(parsed["Z"], 0.3)
        self.assertEqual(parsed["E"], 1.25)
        self.assertEqual(parsed["F"], 1800.0)
        formatted = format_gcode_line(parsed["cmd"], parsed)
        self.assertIn("X100.00000", formatted)
        self.assertIn("Y200.00000", formatted)

    def test_interpolation(self):
        x = np.linspace(0, 10, 5)
        y = np.linspace(0, 10, 5)
        z = np.add.outer(np.linspace(0, 2, 5), np.linspace(0, 2, 5))  # Z = x + y
        mesh = SurfaceMesh(x, y, z, z_top=np.max(z))
        interpolator = RectBivariateSpline(mesh.y, mesh.x, mesh.z)
        z_val = interpolate_surface_z(interpolator, 5, 5)
        self.assertTrue( 1.9 < z_val < 2.1)

    def test_split_move(self):
        start = {"X": 0.0, "Y": 0.0, "Z": 0.2, "E": 0.0}
        end = {"X": 10.0, "Y": 0.0, "Z": 0.2, "E": 1.0}
        segments = split_move(start, end, max_dist=2.0)
        self.assertEqual(len(segments), 5)
        self.assertTrue(abs(segments[-1]["X"] - 10.0) < 1e-6)
        self.assertTrue(abs(segments[-1]["E"] - 1.0) < 1e-6)
