import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.placement
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

# Note - this uses shape_builder though it not particularly illustrative
# as it doesn't do anything `geometry.add_wall_representation` can't do...


# Create a blank model
ifcfile = ifcopenshell.api.project.create_file(version="IFC4X3")
project = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                              ifc_class="IfcProject", 
                                              name="Two Walls Project")

model3d = ifcopenshell.api.context.add_context(file=ifcfile, context_type="Model")

# note - for subsequent uses of `geometry.edit_object_placement` we have to call 
# with `is_si=False`
length = ifcopenshell.api.unit.add_si_unit(file=ifcfile, unit_type="LENGTHUNIT", prefix="CENTI")
ifcopenshell.api.unit.assign_unit(file=ifcfile, units=[length])


body = ifcopenshell.api.context.add_context(file=ifcfile,
                                            context_type="Model", 
                                            context_identifier="Body", 
                                            target_view="MODEL_VIEW", 
                                            parent=model3d)

wall_thickness = 1.0

## Wall_1

entity_wall1 = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                   ifc_class='IfcWall', 
                                                   name='Wall_1', 
                                                   predefined_type='NOTDEFINED')

builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)
block1 = builder.block(position=V(0.0, 0.0, 0.0),
                          x_length = 200.0,
                          y_length = wall_thickness,
                          z_length = 140.0)
block_representation1 = builder.get_representation(context=body, items=[block1])

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=entity_wall1, 
                                                representation=block_representation1)

# placement values are centimetres
placement_wall1 = make_placement_matrix(V(50.0, 50.0, 0))

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=entity_wall1, 
                                                matrix=placement_wall1, 
                                                is_si=False)

## Wall_2 

entity_wall2 = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                   ifc_class='IfcWall', 
                                                   name='Wall_2', 
                                                   predefined_type='NOTDEFINED')

block2 = builder.block(position=V(0.0, 0.0, 0.0),
                          x_length = 60.0 - wall_thickness,
                          y_length = wall_thickness,
                          z_length = 140.0)
block_representation2 = builder.get_representation(context=body, items=[block2])

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=entity_wall2, 
                                                representation=block_representation2)

# placement values are centimetres
placement_wall2 = make_placement_matrix(position=V(50.0 + 200.0, 50.0 + wall_thickness, 0),
                                        rotations=[(90.0, 'Z')])

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=entity_wall2, 
                                                matrix=placement_wall2, 
                                                is_si=False)


# Write out to a file
ifcfile.write("./output/builder_two_walls.ifc")

