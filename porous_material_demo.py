import math
import gmsh
import random
from itertools import product

class PorousMaterialVolumeGenerator:
    def __init__(self):
        self.allowance = 0.05

    def generate_volume(self, spheres_count=10, r=0.2):
        bounding_box = gmsh.model.occ.add_box(0, 0, 0, 1, 1, 1)
        gmsh.model.occ.synchronize()

        sphere_objects = self.generate_sphere_objects(spheres_count, r)
        gmsh.model.occ.synchronize()

        # intersections, _ = gmsh.model.occ.intersect(sphere_objects, [(3, bounding_box)], removeTool=False)
        # gmsh.model.occ.synchronize()

        # cube_fragments, _ = gmsh.model.occ.cut([(3, bounding_box)], intersections)
        # gmsh.model.occ.synchronize()

        # return cube_fragments

    def generate_sphere_objects(self, spheres_count=10, r=0.2):
        self.existing_spheres = []
        objs = []
        for _ in range(spheres_count):
            new_objs = self.generate_random_periodic_sphere(r)
            objs.extend(new_objs)

        return objs

    def generate_random_periodic_sphere(self, r):
        while True:
            x = random.uniform(r + self.allowance, 1 - r - self.allowance)
            y = random.uniform(r + self.allowance, 1 - r - self.allowance)
            z = random.uniform(r + self.allowance, 1 - r - self.allowance)
            center = (x, y, z)
            intersected_spheres = list(filter(lambda s: self.spheres_intersect(s["center"], r, center, r), self.existing_spheres))
            if len(intersected_spheres) == 0:
                centers, objects = self.add_periodic_sphere(x, y, z, r)
                for c in centers:
                    self.existing_spheres.append({"center": c, "radius": r})
                return objects

    def add_periodic_sphere(self, x, y, z, r):
        sphere_tag = gmsh.model.occ.addSphere(x, y, z, r)
        return [(x, y, z)], [(3, sphere_tag)]

    # def add_periodic_sphere(self, x, y, z, r):
    #     centers = []
    #     objects = []

    #     shifts = list(product([0, -1, 1], repeat=3))
    #     for dx, dy, dz in shifts:
    #         new_x = x + dx
    #         new_y = y + dy
    #         new_z = z + dz

    #         if (0 - r <= new_x <= 1 + r and
    #             0 - r <= new_y <= 1 + r and
    #             0 - r <= new_z <= 1 + r):

    #             sphere_tag = gmsh.model.occ.addSphere(new_x, new_y, new_z, r)
    #             centers.append((new_x, new_y, new_y))
    #             objects.append((3, sphere_tag))

    #     return centers, objects

    def spheres_intersect(self, c1, r1, c2, r2):
        dx = c1[0] - c2[0]
        dy = c1[1] - c2[1]
        dz = c1[2] - c2[2]
        distance_squared = dx * dx + dy * dy + dz * dz
        radius_sum = r1 + r2
        return distance_squared <= (radius_sum * radius_sum + self.allowance)


gmsh.initialize()
gmsh.model.add("porous_material")

mesh_size = 0.1
min_size = 0.9 * mesh_size
max_size = 1.1 * mesh_size
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", min_size)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", max_size)

generator = PorousMaterialVolumeGenerator()
volume = generator.generate_volume(15, 0.1)

gmsh.model.mesh.generate(3)
filename = "porous.msh"
gmsh.write(filename)

gmsh.fltk.run()

gmsh.finalize()

