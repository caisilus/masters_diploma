import gmsh
import math
import sys

gmsh.initialize()
gmsh.model.add("branch_element")

r_root=0.5
h_root=4.0
r_branch=0.4
h_branch=3.0
num_branches=4
angle=math.radians(30)

class ElementGenerator:
    def __init__(self, r_root=0.5, h_root=4.0, r_branch=0.4, h_branch=3.0, num_branches=4, angle=math.radians(30)):
        self.r_root = r_root
        self.h_root = h_root
        self.r_branch = r_branch
        self.h_branch = h_branch
        self.num_branches = num_branches
        self.angle = angle
        self.z_angle_per_branch = 2 * math.pi / self.num_branches

    def generate_volume(self, num_elements_x, num_elements_y, num_elements_z):
        element_positions = self.calculate_positions(num_elements_x, num_elements_y, num_elements_z)

        all_elements = []
        for pos in element_positions:
            element = self.generate_element_at(*pos)
            all_elements.extend(element)

        return all_elements

    def calculate_positions(self, num_elements_x, num_elements_y, num_elements_z):
        start = (0, 0, 0)
        positions = [start]
        for iz in range(0, num_elements_z):
            x, y, z = start
            dx, dy, dz = self.branch_dimentions_by_angle(self.z_angle_per_branch)
            element_width = math.sqrt(dx * dx + dy * dy) * 1.98
            element_height = self.h_root + dz * 0.7
            x += dx * iz
            y += dy * iz
            for ix in range(0, num_elements_x):
                for iy in range(0, num_elements_y):
                    new_point = (x + element_width * ix, y + element_width * iy, z + element_height * iz)
                    if new_point != start:
                        positions.append(new_point)
        return positions

    def generate_element_at(self, x, y, z):
        root_cylinder = gmsh.model.occ.addCylinder(x, y, z, 0, 0, self.h_root, self.r_root)

        branches = []
        for i in range(self.num_branches):
            theta = i * self.z_angle_per_branch
            dx, dy, dz = self.branch_dimentions_by_angle(theta)
            branch_start = (x + dx / 20.0, y + dy / 20.0, z + self.h_root - (dz / 5.0))
            branch = gmsh.model.occ.addCylinder(*branch_start, dx, dy, dz, self.r_branch)
            branches.append(branch)

        fused, _ = gmsh.model.occ.fuse([(3, root_cylinder)],  [(3, e) for e in branches])

        return fused

    def branch_dimentions_by_angle(self, theta):
        dx = self.h_branch * math.cos(theta) * math.cos(self.angle)
        dy = self.h_branch * math.sin(theta) * math.cos(self.angle)
        dz = self.h_branch * math.sin(self.angle)
        return dx, dy, dz


element_generator = ElementGenerator(r_root, h_root, r_branch, h_branch, num_branches, angle)

all_elements = element_generator.generate_volume(2, 2, 2)

# fused, _ = gmsh.model.occ.fragment([(3, e) for e in all_elements], [])

gmsh.model.occ.synchronize()

gmsh.model.mesh.setSize(gmsh.model.getEntities(0), 2)

# Генерация сетки
gmsh.model.mesh.generate(3)

# Сохранение в файл
gmsh.write("branch_element.msh")

# Включение GUI для визуализации (если необходимо)
if '-nopopup' not in sys.argv:
    gmsh.fltk.run()

gmsh.finalize()
