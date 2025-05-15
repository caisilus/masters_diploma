import gmsh
import math

class BranchingElementGenerator:
    def __init__(self, width, height, h_root=4.0, r_root=0.5, r_branch=0.4, num_branches=4):
        self.width = width
        self.height = height
        self.r_root = r_root
        self.h_root = h_root
        self.r_branch = r_branch
        self.num_branches = num_branches
        self.z_angle_per_branch = 2 * math.pi / self.num_branches
        self.calculate_angle_and_h_branch()

    def calculate_angle_and_h_branch(self):
        dx = self.width / 2
        dy = self.height = self.h_root
        hypotenuse = math.sqrt(dx * dx + dy * dy)
        self.cos_angle = dx / hypotenuse
        self.sin_angle = dy / hypotenuse
        self.h_branch = hypotenuse * 1.5

    def generate_at(self, x, y, z):
        root_cylinder = gmsh.model.occ.addCylinder(x, y, z, 0, 0, self.h_root, self.r_root)

        branches = []
        for i in range(self.num_branches):
            theta = i * self.z_angle_per_branch
            dx, dy, dz = self.branch_dimentions_by_angle(theta)
            branch_start = (x, y, z + self.h_root)
            branch = gmsh.model.occ.addCylinder(*branch_start, dx, dy, dz, self.r_branch)
            branches.append(branch)

        fused, _ = gmsh.model.occ.fuse([(3, root_cylinder)],  [(3, e) for e in branches])
        gmsh.model.occ.synchronize()

        return fused[0]

    def dimentions(self):
        return self.width, self.height

    def branch_dimentions_by_angle(self, theta):
        branch_dx = self.h_branch * math.cos(theta) * self.cos_angle
        branch_dy = self.h_branch * math.sin(theta) * self.cos_angle
        branch_dz = self.h_branch * self.sin_angle
        return branch_dx, branch_dy, branch_dz
