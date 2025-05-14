import gmsh
import math
from mesh_generators.branching_element_generator import BranchingElementGenerator
from mesh_generators.branching_elements_welder import BranchingElementsWelder

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
        self.single_element_generator = BranchingElementGenerator(
            r_root=r_root, h_root=h_root, r_branch=r_branch, h_branch=h_branch, num_branches=num_branches, angle=angle\
        )
        self.elements_welder = BranchingElementsWelder()

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
        # return 0

    def generate_branched_trees(self, num_elements_x, num_elements_y, num_elements_z):
        element_positions = self.calculate_positions(num_elements_x, num_elements_y, num_elements_z)

        all_elements = set()
        for pos in element_positions:
            element = self.generate_element_at(*pos)
            _, element_id = element
            all_elements.add(element_id)

        return list(all_elements)

    def calculate_positions(self, num_elements_x, num_elements_y, num_elements_z):
        element_width, element_height = self.single_element_generator.dimentions()
        start = (element_width / 2 - 0, element_width / 2 - 0, 0)
        positions = []
        for iz in range(0, num_elements_z):
            x, y, z = start
            # x += element_width / 2 * iz
            y -= element_width / 2 * iz
            for ix in range(0, num_elements_x):
                for iy in range(0, num_elements_y):
                    new_point = (x + element_width * ix, y + element_width * iy, z + element_height * iz)
                    positions.append(new_point)
        return positions

    def generate_element_at(self, x, y, z):
        return self.single_element_generator.generate_at(x, y, z)

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
