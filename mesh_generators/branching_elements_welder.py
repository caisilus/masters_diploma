import gmsh, math

class BranchingElementsWelder:
    def weld(self, b1, b2):
        intersect_out, _ = gmsh.model.occ.intersect([(3, b1)], [(3, b2)], removeObject=False, removeTool=False)
        inter_tag = intersect_out[0][1]
        inter_com = gmsh.model.occ.getCenterOfMass(3, inter_tag)

        frags, _ = gmsh.model.occ.fragment([(3, b1)], [(3, b2)])
        frags = [tag for dim, tag in frags if dim == 3]

        kept = []
        to_remove = intersect_out
        for tag in frags:
            com = gmsh.model.occ.getCenterOfMass(3, tag)
            if com[2] <= inter_com[2] + 1e-4:
                kept.append((3, tag))
            else:
                to_remove.append((3, tag))

        gmsh.model.occ.remove(to_remove, recursive=True)

        fused, _ = gmsh.model.occ.fuse(kept, kept, removeObject=True, removeTool=True)

        gmsh.model.occ.synchronize()

        # return fused
        return 0
