import gmsh
import math
from mesh_generators.branching_element_generator import BranchingElementGenerator
from mesh_generators.branching_elements_welder import BranchingElementsWelder

class BranchingElementsGenerator:
    def __init__(self, r_root=0.5, h_root=4.0, r_branch=0.4, h_branch=3.0, num_branches=4,
                 num_x=4, num_y=5, num_z=2):
        self.r_root = r_root
        self.h_root = h_root
        self.r_branch = r_branch
        self.h_branch = h_branch
        self.num_branches = num_branches
        self.num_x = num_x
        self.num_y = num_y
        self.num_z = num_z
        self.z_angle_per_branch = 2 * math.pi / self.num_branches
        self.cube_dimention = 1.0 # constant for now
        element_width, element_height = self.single_element_dimentions()
        self.single_element_generator = BranchingElementGenerator(
            element_width, element_height, h_root=h_root, r_root=r_root, r_branch=r_branch,num_branches=num_branches
        )
        self.elements_welder = BranchingElementsWelder()

    # TODO: rework to give all 3 dimentions
    def single_element_dimentions(self):
        return self.cube_dimention / self.num_x, self.cube_dimention / self.num_z

    def generate_volume(self):
        branched_elements = self.generate_branched_trees()
        # _, fused_trees = self.fuse_elements(branched_elements)
        fused_trees = self.fuse_by_levels(branched_elements)

        bounding_box = gmsh.model.occ.add_box(0, 0, 0, self.cube_dimention, self.cube_dimention, self.cube_dimention)

        gmsh.model.occ.synchronize()

        branch_inside_cube, _ = gmsh.model.occ.intersect([(3, fused_trees)], [(3, bounding_box)], removeTool=False)
        gmsh.model.occ.synchronize()

        cube_fragments, _ = gmsh.model.occ.fragment([(3, bounding_box)], branch_inside_cube)
        gmsh.model.occ.synchronize()

        return cube_fragments
        # return 0

    def generate_branched_trees(self):
        levels_to_positions = self.calculate_positions()

        levels_to_elements = {}
        for level, positions in levels_to_positions.items():
            elements = []
            for pos in positions:
                _, element_id = self.generate_element_at(*pos)
                elements.append(element_id)
            levels_to_elements[level] = elements

        return levels_to_elements

    def calculate_positions(self):
        element_width, element_height = self.single_element_dimentions()
        half_width = element_width / 2
        start = (half_width, half_width, 0)
        levels = {}
        for iz in range(0, self.num_z):
            x, y, z = start
            # x += half_width * iz
            y -= half_width * iz
            positions_at_level = []
            for ix in range(0, self.num_x):
                for iy in range(0, self.num_y):
                    new_point = (x + element_width * ix, y + element_width * iy, z + element_height * iz)
                    positions_at_level.append(new_point)

            levels[iz] = positions_at_level
        return levels

    def generate_element_at(self, x, y, z):
        return self.single_element_generator.generate_at(x, y, z)

    def fuse_by_levels(self, elements_by_levels):
        fused = None
        for level, element_ids in elements_by_levels.items():
            at_level = self.fuse_at_level(element_ids)
            if fused is not None:
                fused, _ = gmsh.model.occ.fuse([(3, fused)], [(3, at_level)])
                _, fused = fused[0]
            else:
                fused = at_level

        return fused


    def fuse_at_level(self, element_ids):
        fused = element_ids[0]
        for element_id in element_ids[1:]:
            _, fused = self.elements_welder.weld(fused, element_id)
        return fused

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
