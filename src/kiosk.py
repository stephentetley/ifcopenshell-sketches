import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.placement
from ifcopenshell.util.shape_builder import V, VectorType
import numpy
import math
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

kiosk_width_m = 1.8
kiosk_side_height_m = 1.6
kiosk_gable_height_m = 1.85
kiosk_depth_m = 0.8
wall_thickness_m = 0.01

## front_wall



front_wall = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                ifc_class='IfcWall', 
                                                name='Front_Wall', 
                                                predefined_type='NOTDEFINED')


fw_rep = ifcopenshell.api.geometry.add_wall_representation(file=ifcfile,
                                                          context=body, 
                                                          length=kiosk_width_m, 
                                                          height=kiosk_side_height_m, 
                                                          thickness=wall_thickness_m)

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

# Opening

door_opening = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                   ifc_class="IfcOpeningElement")

door_width_m = 1.50
door_height_m = 1.45 
builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)

door_shape_mm = builder.rectangle(size=V(door_width_m * 1000.0, door_height_m * 1000.0))

# draw the shape in the XZ plane and extrude on the y-axis, move the y-origin
# to acount for thickness (magnitude)
door_opening_solid = builder.extrude(profile_or_curve=door_shape_mm,
                                     magnitude=wall_thickness_m * 1000,
                                     position=(0, 10, 0),
                                     position_x_axis=(1.0, 0.0, 0.0),
                                     position_y_axis=(0.0, 0.0, 1.0),
                                     position_z_axis=(0.0, 1.0, 0.0))

opening_repr = builder.get_representation(context=body, items=[door_opening_solid])
ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=door_opening, 
                                                representation=opening_repr)

x_displacement_mm = (kiosk_width_m - door_width_m) / 2.0 * 1000.0
opening_placement = make_placement_matrix(V(x_displacement_mm, 0.0, 0.0))

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=door_opening, 
                                                matrix=opening_placement, 
                                                is_si=False)

ifcopenshell.api.feature.add_feature(file=ifcfile, element=front_wall, feature=door_opening)



# back_wall


back_wall = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                ifc_class='IfcWall', 
                                                name='Back_Wall', 
                                                predefined_type='NOTDEFINED')


bw_rep = ifcopenshell.api.geometry.add_wall_representation(file=ifcfile,
                                                          context=body, 
                                                          length=kiosk_width_m, 
                                                          height=kiosk_side_height_m, 
                                                          thickness=wall_thickness_m)

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=back_wall, 
                                                representation=bw_rep)

# placement values are millimetres
y_displacement_mm = (kiosk_depth_m - wall_thickness_m) * 1000.0

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

side_length_m = kiosk_depth_m - (2.0 * wall_thickness_m)


# clip from 2 metres up the wall (side_hight_m)
triangle_height_m = kiosk_gable_height_m - kiosk_side_height_m
triangle_base_m = kiosk_depth_m / 2.0
clip1 = ifcopenshell.util.data.Clipping(location=(0.0, 0.0, kiosk_side_height_m), 
                                        normal=(-triangle_height_m, 0.0, triangle_base_m))
clip2 = ifcopenshell.util.data.Clipping(location=(side_length_m, 0.0, kiosk_side_height_m), 
                                        normal=(triangle_height_m, 0.0, triangle_base_m))
clipping_list = [clip1, clip2]

rsw_rep = ifcopenshell.api.geometry.add_wall_representation(file=ifcfile,
                                                          context=body, 
                                                          length=side_length_m, 
                                                          height=kiosk_gable_height_m, 
                                                          thickness=wall_thickness_m,
                                                          clippings=clipping_list)


ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=right_side_wall, 
                                                representation=rsw_rep)

x_displacement_mm = kiosk_width_m * 1000.0
y_displacement_mm = wall_thickness_m * 1000.0
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
                                                          length=side_length_m, 
                                                          height=kiosk_gable_height_m, 
                                                          thickness=wall_thickness_m,
                                                          clippings=clipping_list)

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=left_side_wall, 
                                                representation=lsw_rep)

x_displacement = wall_thickness_m * 1000.0
y_displacement_mm = wall_thickness_m * 1000.0
lsw_placement = make_placement_matrix(position=V(x_displacement, y_displacement_mm, 0),
                                      rotations = [(90, 'Z')])

ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=left_side_wall, 
                                                matrix=lsw_placement, 
                                                is_si=False)


## two slab roof

front_roof_slab = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                   ifc_class='IfcSlab', 
                                                   name='Front_Roof_Slab', 
                                                   predefined_type='ROOF')

rear_roof_slab = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                   ifc_class='IfcSlab', 
                                                   name='Rear_Roof_Slab', 
                                                   predefined_type='ROOF')

# one slab covers half the roof
slab_width_m = kiosk_width_m
half_depth_m = kiosk_depth_m / 2.0
theta = math.atan(triangle_height_m / half_depth_m)
theta_deg = math.degrees(theta)
slab_ylen_m = math.sqrt((half_depth_m * half_depth_m) + (triangle_height_m * triangle_height_m))

print(f"slab_ylen_m={slab_ylen_m}")

slab_points1 = [(0.0, 0.0), (kiosk_width_m, 0), (kiosk_width_m, slab_ylen_m), (0.0, slab_ylen_m)]
frslab_rep = ifcopenshell.api.geometry.add_slab_representation(file=ifcfile,
                                                          context=body, 
                                                          depth=wall_thickness_m,
                                                          direction_sense='POSITIVE',
                                                          polyline=slab_points1,
                                                          x_angle = 0 
                                                          )

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=front_roof_slab, 
                                                representation=frslab_rep)

wall_thickness_mm = wall_thickness_m * 1000.0
z_displacement_mm = kiosk_side_height_m * 1000.0
frslab_placement = make_placement_matrix(V(0.0, wall_thickness_mm, z_displacement_mm), rotations=[(theta_deg, 'X')])


ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=front_roof_slab, 
                                                matrix=frslab_placement, 
                                                is_si=False)

brslab_rep = ifcopenshell.api.geometry.add_slab_representation(file=ifcfile,
                                                          context=body, 
                                                          depth=wall_thickness_m,
                                                          direction_sense='POSITIVE',
                                                          polyline=slab_points1,
                                                          x_angle = 0
                                                          )

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=rear_roof_slab, 
                                                representation=brslab_rep)

triangle_height_mm = 1000.0 * triangle_height_m 
half_depth_mm = 1000.0 * half_depth_m 

brslab_placement = make_placement_matrix(position=V(0.0, half_depth_mm - wall_thickness_mm, z_displacement_mm + triangle_height_mm),
                                          rotations=[(-theta_deg, 'X')]) 

ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=rear_roof_slab, 
                                                matrix=brslab_placement, 
                                                is_si=False)


# Write out to a file
ifcfile.write("./output/kiosk.ifc")
