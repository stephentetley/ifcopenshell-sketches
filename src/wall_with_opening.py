import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.shape_builder
from ifcopenshell.util.shape_builder import V
import numpy


def make_placement_matrix(x, y, z): 
    matrix = numpy.eye(4)
    matrix[:,3][0:3] = (x, y, z)
    return matrix

def make_placement_angle_matrix(deg, x, y, z): 
    matrix = numpy.eye(4)
    matrix = ifcopenshell.util.placement.rotation(deg, "Z") @ matrix
    matrix[:,3][0:3] = (x, y, z)
    return matrix

def make_placement_angle_matrix_x(deg, x, y, z): 
    matrix = numpy.eye(4)
    matrix = ifcopenshell.util.placement.rotation(deg, "X") @ matrix
    matrix[:,3][0:3] = (x, y, z)
    return matrix


# Create a blank model
ifcfile = ifcopenshell.api.project.create_file(version="IFC4X3")
project = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                              ifc_class="IfcProject", 
                                              name="Wall With Opening Project")

model3d = ifcopenshell.api.context.add_context(file=ifcfile, context_type="Model")

# note - for subsequent uses of `geometry.edit_object_placement` we have to call 
# with `is_si=False`
si_length = ifcopenshell.api.unit.add_si_unit(file=ifcfile, unit_type="LENGTHUNIT", prefix="MILLI")
ifcopenshell.api.unit.assign_unit(file=ifcfile, units=[si_length])


body = ifcopenshell.api.context.add_context(file=ifcfile,
                                            context_type="Model", 
                                            context_identifier="Body", 
                                            target_view="MODEL_VIEW", 
                                            parent=model3d)


## Wall_1

wall1 = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                            ifc_class='IfcWall',
                                            name='Wall_1',
                                            predefined_type='NOTDEFINED')

wrep = ifcopenshell.api.geometry.add_wall_representation(file=ifcfile,
                                                         context=body,
                                                         length=2.4,
                                                         height=1.6,
                                                         thickness=0.1,
                                                         clippings=[]
                                                         )

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=wall1, 
                                                representation=wrep)

# placement in mm
placement_wall1 = make_placement_matrix(0.0, 0.0, 0.0)

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=wall1, 
                                                matrix=placement_wall1, 
                                                is_si=False)

door_opening = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                   ifc_class="IfcOpeningElement")

builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)

door_shape = builder.rectangle(size=V(1800, 1300))

door_opening_solid = builder.extrude(profile_or_curve=door_shape,
                                     magnitude=100.0)

opening_repr = builder.get_representation(context=body, items=[door_opening_solid])
ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=door_opening, 
                                                representation=opening_repr)


opening_placement = make_placement_angle_matrix_x(90, 300.0, 100.0, 0.0)

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=door_opening, 
                                                matrix=opening_placement, 
                                                is_si=False)

ifcopenshell.api.feature.add_feature(file=ifcfile, element=wall1, feature=door_opening)

# Write out to a file
ifcfile.write("./output/wall_with_opening1.ifc")
