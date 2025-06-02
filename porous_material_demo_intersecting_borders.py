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

        intersections, _ = gmsh.model.occ.intersect(sphere_objects, [(3, bounding_box)], removeTool=False)
        gmsh.model.occ.synchronize()

        cube_fragments, _ = gmsh.model.occ.cut([(3, bounding_box)], intersections)
        gmsh.model.occ.synchronize()

        return cube_fragments

    def generate_sphere_objects(self, spheres_count=10, r=0.2):
        self.existing_spheres = []
        objs = []
        for _ in range(spheres_count):
            new_objs = self.generate_random_periodic_sphere(r)
            objs.extend(new_objs)

        return objs

    def generate_random_periodic_sphere(self, r):
        while True:
            x = random.uniform(0, 1)
            y = random.uniform(0, 1)
            z = random.uniform(0, 1)
            imaginary_periodic_spheres = self.get_imaginary_periodic_spheres(x, y, z, r)

            if not self.check_intersections(imaginary_periodic_spheres, self.existing_spheres):
                objects = []
                for sphere in imaginary_periodic_spheres:
                    x, y, z = sphere["center"]
                    objects.append(self.add_sphere(x, y, z, sphere["radius"]))
                return objects

    def get_imaginary_periodic_spheres(self, x, y, z, r):
        spheres = []

        shifts = list(product([0, -1, 1], repeat=3))
        for dx, dy, dz in shifts:
            new_x = x + dx
            new_y = y + dy
            new_z = z + dz

            if (0 - r <= new_x <= 1 + r and
                0 - r <= new_y <= 1 + r and
                0 - r <= new_z <= 1 + r):

                spheres.append({"center": (new_x, new_y, new_z), "radius": r})

        return spheres


    def add_sphere(self, x, y, z, r):
        sphere_tag = gmsh.model.occ.addSphere(x, y, z, r)
        self.existing_spheres.append({"center": (x, y, z), "radius": r})
        return (3, sphere_tag)

    def check_intersections(self, spheres_list1, spheres_list2):
        for s1 in spheres_list1:
            for s2 in spheres_list2:
                intersect = self.spheres_intersect(s1["center"], s1["radius"], s2["center"], s2["radius"])
                if intersect:
                    return True

        return False

    def spheres_intersect(self, c1, r1, c2, r2):
        dx = c1[0] - c2[0]
        dy = c1[1] - c2[1]
        dz = c1[2] - c2[2]
        distance_squared = dx * dx + dy * dy + dz * dz
        radius_sum = r1 + r2
        return distance_squared <= (radius_sum * radius_sum + self.allowance)


gmsh.initialize()
gmsh.model.add("porous_material")

mesh_size = 0.05
min_size = 0.9 * mesh_size
max_size = 1.1 * mesh_size
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", min_size)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", max_size)

generator = PorousMaterialVolumeGenerator()
volume = generator.generate_volume(10, 0.1)

gmsh.model.mesh.generate(3)
filename = "porous.msh"
gmsh.write(filename)

gmsh.fltk.run()

gmsh.finalize()

