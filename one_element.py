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
        branched_elements = self.generate_branched_trees(num_elements_x, num_elements_y, num_elements_z)
        _, fused_trees = self.fuse_elements(branched_elements)

        bounding_box = self.generate_bounding_box_for(fused_trees, margin=1.0)
        difference_result, _ = gmsh.model.occ.cut([(3, bounding_box)], [(3, fused_trees)], removeTool=False)

        gmsh.model.occ.synchronize()

        return difference_result

    def generate_branched_trees(self, num_elements_x, num_elements_y, num_elements_z):
        element_positions = self.calculate_positions(num_elements_x, num_elements_y, num_elements_z)

        all_elements = set()
        for pos in element_positions:
            element_list = self.generate_element_at(*pos)
            for (_, element_id) in element_list:
                all_elements.add(element_id)

        return list(all_elements)

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

    def fuse_elements(self, element_ids):
        elements_for_fuse = [(3, e) for e in element_ids]

        if len(elements_for_fuse) == 1:
            return elements_for_fuse

        unified_object = elements_for_fuse[0]
        for obj in elements_for_fuse[1:]:
            fused, _ = gmsh.model.occ.fuse([unified_object], [obj])
            gmsh.model.occ.synchronize()  # синхронизация после каждой операции
            unified_object = fused[0]

        return unified_object

    def generate_bounding_box_for(self, element, margin=1.0):
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(3, element)

        box_x = xmin - margin
        box_y = ymin - margin
        box_z = zmin - margin
        box_dx = (xmax - xmin) + 2 * margin
        box_dy = (ymax - ymin) + 2 * margin
        box_dz = (zmax - zmin) + 2 * margin

        box = gmsh.model.occ.addBox(box_x, box_y, box_z, box_dx, box_dy, box_dz)
        gmsh.model.occ.synchronize()

        return box


element_generator = ElementGenerator(r_root, h_root, r_branch, h_branch, num_branches, angle)

all_elements = element_generator.generate_volume(2, 2, 2)
print(all_elements)

gmsh.model.mesh.setSize(gmsh.model.getEntities(0), 1)

# Генерация сетки
gmsh.model.mesh.generate(3)

# Сохранение в файл
gmsh.write("branch_element.msh")

# Включение GUI для визуализации (если необходимо)
if '-nopopup' not in sys.argv:
    gmsh.fltk.run()

gmsh.finalize()
