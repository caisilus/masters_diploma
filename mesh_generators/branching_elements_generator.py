import gmsh
import math

class BranchingElementsGenerator:
    def __init__(self, r_root=0.5, h_root=4.0, r_branch=0.4, h_branch=3.0, num_branches=4, angle=math.radians(30)):
        self.r_root = r_root
        self.h_root = h_root
        self.r_branch = r_branch
        self.h_branch = h_branch
        self.num_branches = num_branches
        self.angle = angle
        self.z_angle_per_branch = 2 * math.pi / self.num_branches
        self.cube_dimention = 1.0 # constant for now

    def generate_volume(self, num_elements_x, num_elements_y, num_elements_z):
        branched_elements = self.generate_branched_trees(num_elements_x, num_elements_y, num_elements_z)
        _, fused_trees = self.fuse_elements(branched_elements)

        bounding_box = gmsh.model.occ.add_box(0, 0, 0, self.cube_dimention, self.cube_dimention, self.cube_dimention)

        gmsh.model.occ.synchronize()

        branch_inside_cube, _ = gmsh.model.occ.intersect([(3, fused_trees)], [(3, bounding_box)], removeTool=False)
        gmsh.model.occ.synchronize()

        cube_fragments, _ = gmsh.model.occ.fragment([(3, bounding_box)], branch_inside_cube)
        gmsh.model.occ.synchronize()

        return cube_fragments

    def generate_branched_trees(self, num_elements_x, num_elements_y, num_elements_z):
        element_positions = self.calculate_positions(num_elements_x, num_elements_y, num_elements_z)

        all_elements = set()
        for pos in element_positions:
            element = self.generate_element_at(*pos)
            _, element_id = element
            all_elements.add(element_id)

        return list(all_elements)

    def calculate_positions(self, num_elements_x, num_elements_y, num_elements_z):
        dx, dy, dz = self.branch_dimentions_by_angle(self.z_angle_per_branch)
        element_width = math.sqrt(dx * dx + dy * dy) * 1.98
        element_height = self.h_root + dz * 0.7
        start = (element_width / 2, element_width / 2, 0)
        positions = [start]
        for iz in range(0, num_elements_z):
            x, y, z = start
            x += dx * iz
            y -= dy * iz
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

        return fused[0]

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
