import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.unit
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
                                              name="Wall Curved Polyline Project")

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


## Wall_1

entity_wall1 = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                   ifc_class='IfcWall', 
                                                   name='Wall_1', 
                                                   predefined_type='NOTDEFINED')

builder1 = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)

points = [V(100, 0), V(70.7, 70.7), V(0, 100), V(0, 98), V(69.296, 69.296), V(98, 0)]
arc_points = [1, 4] # point with index 1 is the middle of the outer arc, 4 is the middle of inner arc
position = V(0,0)
curved_polyline = builder1.polyline(points, closed=True, position_offset=position, arc_points=arc_points)


extruded = builder1.extrude(profile_or_curve=curved_polyline, 
                            magnitude= 140.0, 
                            position = V(0, 0, 0)) 

repr_3d_1 = builder1.get_representation(context=body, items=[extruded])

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=entity_wall1, 
                                                representation=repr_3d_1)

# placement values are centimetres
placement_wall1 = make_placement_matrix(V(0.0, 0.0, 0.0))

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=entity_wall1, 
                                                matrix=placement_wall1, 
                                                is_si=False)



# Write out to a file
ifcfile.write("./output/wall_curve1.ifc")
