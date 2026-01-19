import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.util.placement
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.shape_builder 
from ifcopenshell.util.shape_builder import V
import numpy
import math


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
                                              name="Two Slab Roof Project")

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
                                                   predefined_type='ROOF')

slab2 = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                   ifc_class='IfcSlab', 
                                                   name='Slab_2', 
                                                   predefined_type='ROOF')


builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)

width_m = 2.4
side_height_m = 1.6
side_center_height_m = 1.8
depth_m = 0.8

# one slab covers half the roof
slab_width_m = width_m
half_depth_m = depth_m / 2.0
gable_height_m = side_center_height_m - side_height_m
theta = math.atan(gable_height_m / half_depth_m)
theta_deg = math.degrees(theta)
slab_ylen_m = math.sqrt((half_depth_m * half_depth_m) + (gable_height_m * gable_height_m))

slab_points1 = [(0.0, 0.0), (width_m, 0), (width_m, slab_ylen_m), (0.0, slab_ylen_m)]
srep1 = ifcopenshell.api.geometry.add_slab_representation(file=ifcfile,
                                                          context=body, 
                                                          depth=0.08,
                                                          direction_sense='POSITIVE',
                                                          polyline=slab_points1,
                                                          x_angle = theta # math.radians(30)
                                                          )

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=slab1, 
                                                representation=srep1)

placement_matrix1 = make_placement_angle_matrix_x(theta_deg, 0.0, 0.0, 0.0)

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=slab1, 
                                                matrix=placement_matrix1, 
                                                is_si=False)

# slab_points2 = [(0.0, slab_ylen_m), (width_m, slab_ylen_m), (width_m, slab_ylen_m * 2.0), (0.0, slab_ylen_m * 2.0)]
srep2 = ifcopenshell.api.geometry.add_slab_representation(file=ifcfile,
                                                          context=body, 
                                                          depth=0.08,
                                                          direction_sense='POSITIVE',
                                                          polyline=slab_points1,
                                                          x_angle = -theta # math.radians(-30)
                                                          )

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=slab2, 
                                                representation=srep2)

gable_height_mm = 1000 * gable_height_m 
half_depth_mm = 1000 * half_depth_m 
placement_matrix2 = make_placement_angle_matrix_x(-theta_deg, 0.0, 447.21, 223.61) # half_depth_mm, gable_height_mm)

ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=slab2, 
                                                matrix=placement_matrix2, 
                                                is_si=False)

# Write out to a file
ifcfile.write("./output/two_slab_roof1.ifc")
