import gmsh
from mesh_generators.polyhedron_porous_generator import PolyhedronPorousGenerator

gmsh.initialize()
gmsh.model.add("random_octahedron")

generator = PolyhedronPorousGenerator()
generator.generate_volume()

gmsh.write("random_octahedron.msh")
gmsh.fltk.run()
gmsh.finalize()
