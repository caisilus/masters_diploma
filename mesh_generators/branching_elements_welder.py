import gmsh, math

class BranchingElementsWelder:
    def weld(self, b1, b2, cutting_plane_at=None):
        welded_element = self.weld_branches(b1, b2)
        if cutting_plane_at:
            welded_element = self.cut_by_plane(welded_element, cutting_plane_at)

        return welded_element

    def weld_branches(self, b1, b2):
        kept = [(3, b1), (3, b2)]

        fused, _ = gmsh.model.occ.fuse(kept, kept, removeObject=True, removeTool=True)

        gmsh.model.occ.synchronize()

        return fused[0]

    def cut_by_plane(self, welded_element, cutting_plane_at):
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.occ.getBoundingBox(*welded_element)

        cutting_plane = gmsh.model.occ.addBox(
            xmin - 1, ymin - 1,
            cutting_plane_at,
            (xmax - xmin) + 2,
            (ymax - ymin) + 2,
            (zmax - cutting_plane_at) + 1
        )
        gmsh.model.occ.synchronize()

        out, _ = gmsh.model.occ.cut(
            [welded_element],
            [(3, cutting_plane)]
        )

        gmsh.model.occ.synchronize()

        return out[0]
