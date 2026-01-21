import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.unit
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.util.shape_builder
import ifcopenshell.api.spatial
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
                                              name="ConnectPath Project")

model3d = ifcopenshell.api.context.add_context(file=ifcfile, context_type="Model")

# note - for subsequent uses of `geometry.edit_object_placement` we have to call 
# with `is_si=False`
length = ifcopenshell.api.unit.add_si_unit(file=ifcfile, unit_type="LENGTHUNIT", prefix="MILLI")
ifcopenshell.api.unit.assign_unit(file=ifcfile, units=[length])


body = ifcopenshell.api.context.add_context(file=ifcfile,
                                            context_type="Model", 
                                            context_identifier="Body", 
                                            target_view="MODEL_VIEW", 
                                            parent=model3d)


## Proxy_1

wall1 = ifcopenshell.api.root.create_entity(file=ifcfile,  
                                                   ifc_class='IfcWall', 
                                                   name='Wall_1', 
                                                   predefined_type='NOTDEFINED')

wall2 = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                            ifc_class='IfcWall', 
                                            name='Wall_2',
                                            predefined_type='NOTDEFINED')

builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)

block1 = builder.block(position= V(0,0,0), 
                       x_length= 1000,
                       y_length= 100,
                       z_length= 100)

block2 = builder.block(position= V(1000,0,0), 
                       x_length= 1000,
                       y_length= 100,
                       z_length= 100)

rep1 = builder.get_representation(context=body, items=[block1])
rep2 = builder.get_representation(context=body, items=[block2])


ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=wall1, 
                                                representation=rep1)

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=wall2, 
                                                representation=rep2)


path1 = ifcopenshell.api.geometry.connect_path(file=ifcfile, 
                                               relating_element=wall1,
                                               related_element=wall2,
                                               relating_connection="ATEND",
                                               related_connection="ATSTART")

# We can assign the walls into a space which gets shown in the hierarchy view
# In FreeCAD and Blender/Bonsai we can then toggle visibility of the space 
# which toglles both walls - or toggle the individual walls separately.
# What we can't do is edit_object_placement of the space

space1 = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                             ifc_class="IfcSpace", 
                                             name="Space_1")
ifcopenshell.api.aggregate.assign_object(file=ifcfile, products=[space1], relating_object=project)
ifcopenshell.api.aggregate.assign_object(file=ifcfile, products=[wall1, wall2], relating_object=space1)
ifcopenshell.api.spatial.assign_container(file=ifcfile, 
                                                products=[wall1, wall2],
                                                relating_structure=space1)


# Write out to a file
ifcfile.write("./output/geometry_connect_path1.ifc")
