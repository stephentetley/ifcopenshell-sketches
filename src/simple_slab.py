import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.shape_builder 
from ifcopenshell.util.shape_builder import V, VectorType
import numpy
from typing import Literal

def make_placement_matrix(position: VectorType = (0.0, 0.0, 0.0),
                          *,
                          rotations: list[tuple[float, Literal['X', 'Y', 'Z']]] = []) -> numpy.ndarray: 
    matrix = numpy.eye(4)
    for (deg, rot) in rotations:
        matrix = ifcopenshell.util.placement.rotation(deg, rot) @ matrix
    (x, y, z) = position
    matrix[:,3][0:3] = (x, y, z)
    return matrix

# Create a blank model
ifcfile = ifcopenshell.api.project.create_file(version="IFC4X3")
project = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                              ifc_class="IfcProject", 
                                              name="Simple Slab Project")

model3d = ifcopenshell.api.context.add_context(file=ifcfile, context_type="Model")

# note - for subsequent uses of `geometry.edit_object_placement` we have to call 
# with `is_si=False`
length = ifcopenshell.api.unit.add_si_unit(file=ifcfile, 
                                           unit_type="LENGTHUNIT", 
                                           prefix="MILLI")
ifcopenshell.api.unit.assign_unit(file=ifcfile, units=[length])


body = ifcopenshell.api.context.add_context(file=ifcfile,
                                            context_type="Model", 
                                            context_identifier="Body", 
                                            target_view="MODEL_VIEW", 
                                            parent=model3d)


## slab_1

slab1 = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                   ifc_class='IfcSlab', 
                                                   name='Slab_1', 
                                                   predefined_type='NOTDEFINED')


builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)

# slab polygon points in metres...
slab_points = [(0.0, 0.0), (2.000, 0), (2.250, 1.000), (-0.250, 1.000)]
srep = ifcopenshell.api.geometry.add_slab_representation(file=ifcfile,
                                                         context=body, 
                                                         depth=0.5,
                                                         direction_sense='POSITIVE',
                                                         polyline=slab_points
                                                         )

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=slab1, 
                                                representation=srep)

placement_matrix = make_placement_matrix(V(0.0, 0.0, 0))

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=slab1, 
                                                matrix=placement_matrix, 
                                                is_si=False)


# Write out to a file
ifcfile.write("./output/simple_slab1.ifc")
