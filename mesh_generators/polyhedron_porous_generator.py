
import math
import gmsh
import random
import numpy as np
from mesh_generators.volume_generator import VolumeGenerator, ParamType

class PolyhedronPorousGenerator(VolumeGenerator):
    def __init__(self, element_scale=0.5):
        self.element_scale = element_scale

    @classmethod
    def build(cls, params: ParamType):
        ...

    def generate_volume(self):
        base_vertices = np.array([
            [1, 0, 0], [-1, 0, 0], [0, 1, 0],
            [0, -1, 0], [0, 0, 1], [0, 0, -1]
        ]) * self.element_scale

        faces = [
            [0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4],
            [0, 5, 2], [2, 5, 1], [1, 5, 3], [3, 5, 0]
        ]

        offset_range = 1.0
        offset = np.random.rand(3) * offset_range
        vertices = base_vertices + offset

        point_tags = []
        for i, v in enumerate(vertices):
            tag = gmsh.model.occ.addPoint(v[0], v[1], v[2])
            point_tags.append(tag)

        gmsh.model.occ.synchronize()

        surf_tags = []
        for idx, f in enumerate(faces):
            p = [point_tags[i] for i in f]
            l1 = gmsh.model.occ.addLine(p[0], p[1])
            l2 = gmsh.model.occ.addLine(p[1], p[2])
            l3 = gmsh.model.occ.addLine(p[2], p[0])
            loop = gmsh.model.occ.addCurveLoop([l1, l2, l3])
            s = gmsh.model.occ.addPlaneSurface([loop])
            surf_tags.append(s)

        sl = gmsh.model.occ.addSurfaceLoop(surf_tags)
        vol = gmsh.model.occ.addVolume([sl])

        gmsh.model.occ.synchronize()

        self.face_centers = []
        for f in faces:
            pts = vertices[f]   # массив 3×3
            center = pts.mean(axis=0)
            self.face_centers.append(center)
