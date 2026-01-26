import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.placement
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
                                              name="Kiosk Project")

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

kiosk_width_metres = 1.8
kiosk_side_height_metres = 1.6
kiosk_gable_height = 1.85
kiosk_depth_metres = 0.8
wall_thickness_metres = 0.01

## front_wall



front_wall = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                ifc_class='IfcWall', 
                                                name='Front_Wall', 
                                                predefined_type='NOTDEFINED')


fw_rep = ifcopenshell.api.geometry.add_wall_representation(file=ifcfile,
                                                          context=body, 
                                                          length=kiosk_width_metres, 
                                                          height=kiosk_side_height_metres, 
                                                          thickness=wall_thickness_metres)

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=front_wall, 
                                                representation=fw_rep)

# placement values are millimetres
fw_placement = make_placement_matrix(V(0, 0, 0))

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=front_wall, 
                                                matrix=fw_placement, 
                                                is_si=False)

# back_wall


back_wall = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                ifc_class='IfcWall', 
                                                name='Back_Wall', 
                                                predefined_type='NOTDEFINED')


bw_rep = ifcopenshell.api.geometry.add_wall_representation(file=ifcfile,
                                                          context=body, 
                                                          length=kiosk_width_metres, 
                                                          height=kiosk_side_height_metres, 
                                                          thickness=wall_thickness_metres)

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=back_wall, 
                                                representation=bw_rep)

# placement values are millimetres
y_displacement_mm = (kiosk_depth_metres-wall_thickness_metres) * 1000.0

bw_placement = make_placement_matrix(V(0, y_displacement_mm, 0))

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=back_wall, 
                                                matrix=bw_placement, 
                                                is_si=False)

# right_side_wall

right_side_wall = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                    ifc_class='IfcWall', 
                                                    name='Right_Side_Wall', 
                                                    predefined_type='NOTDEFINED')

side_length = kiosk_depth_metres - (2.0 * wall_thickness_metres)
rsw_rep = ifcopenshell.api.geometry.add_wall_representation(file=ifcfile,
                                                          context=body, 
                                                          length=side_length, 
                                                          height=kiosk_side_height_metres, 
                                                          thickness=wall_thickness_metres)


ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=right_side_wall, 
                                                representation=rsw_rep)

x_displacement_mm = kiosk_width_metres * 1000.0
y_displacement_mm = wall_thickness_metres * 1000.0
rsw_placement = make_placement_matrix(position=V(x_displacement_mm, y_displacement_mm, 0),
                                      rotations = [(90, 'Z')])

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=right_side_wall, 
                                                matrix=rsw_placement, 
                                                is_si=False)

# left_side_wall

left_side_wall = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                    ifc_class='IfcWall', 
                                                    name='Left_Side_Wall', 
                                                    predefined_type='NOTDEFINED')


lsw_rep = ifcopenshell.api.geometry.add_wall_representation(file=ifcfile,
                                                          context=body, 
                                                          length=side_length, 
                                                          height=kiosk_side_height_metres, 
                                                          thickness=wall_thickness_metres)

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=left_side_wall, 
                                                representation=lsw_rep)

x_displacement = wall_thickness_metres * 1000.0
y_displacement_mm = wall_thickness_metres * 1000.0
lsw_placement = make_placement_matrix(position=V(x_displacement, y_displacement_mm, 0),
                                      rotations = [(90, 'Z')])

ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=left_side_wall, 
                                                matrix=lsw_placement, 
                                                is_si=False)

# Opening

door_opening = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                   ifc_class="IfcOpeningElement")

door_width_metres = 1.50
door_height_metres = 1.45 
builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)

door_shape_mm = builder.rectangle(size=V(door_width_metres * 1000.0, door_height_metres * 1000.0))

# draw the shape in the XZ plane and extrude on the y-axis, move the y-origin
# to acount for thickness (magnitude)
door_opening_solid = builder.extrude(profile_or_curve=door_shape_mm,
                                     magnitude=wall_thickness_metres * 1000,
                                     position=(0, 10, 0),
                                     position_x_axis=(1.0, 0.0, 0.0),
                                     position_y_axis=(0.0, 0.0, 1.0),
                                     position_z_axis=(0.0, 1.0, 0.0))

opening_repr = builder.get_representation(context=body, items=[door_opening_solid])
ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=door_opening, 
                                                representation=opening_repr)


opening_placement = make_placement_matrix(V(150.0, 0.0, 0.0))

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=door_opening, 
                                                matrix=opening_placement, 
                                                is_si=False)

ifcopenshell.api.feature.add_feature(file=ifcfile, element=front_wall, feature=door_opening)


# Write out to a file
ifcfile.write("./output/kiosk.ifc")
