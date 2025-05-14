import gmsh
import math

class BranchingElementGenerator:
    def __init__(self, r_root=0.5, h_root=4.0, r_branch=0.4, h_branch=3.0, num_branches=4, angle=math.radians(30)):
        self.r_root = r_root
        self.h_root = h_root
        self.r_branch = r_branch
        self.h_branch = h_branch
        self.num_branches = num_branches
        self.angle = angle
        self.z_angle_per_branch = 2 * math.pi / self.num_branches

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
        dx, dy, dz = self.branch_dimentions_by_angle(self.z_angle_per_branch)
        shift_x = math.cos(self.z_angle_per_branch) * math.sin(self.angle) * self.r_branch
        shift_y = math.sin(self.z_angle_per_branch) * math.sin(self.angle) * self.r_branch
        # dx -= shift_x
        # dy -= shift_y
        element_width = math.sqrt(dx * dx + dy * dy) * 1.98
        element_height = self.h_root + dz * 0.7
        return element_width, element_height

    def branch_dimentions_by_angle(self, theta):
        branch_dx = self.h_branch * math.cos(theta) * math.cos(self.angle)
        branch_dy = self.h_branch * math.sin(theta) * math.cos(self.angle)
        branch_dz = self.h_branch * math.sin(self.angle)
        return branch_dx, branch_dy, branch_dz
