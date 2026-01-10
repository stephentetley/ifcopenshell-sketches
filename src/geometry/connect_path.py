import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.unit
import ifcopenshell.api.geometry
import ifcopenshell.api.root
from ifcopenshell.util.shape_builder import V
import ifcopenshell.util.shape_builder
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


# Create a blank model
ifcfile = ifcopenshell.api.project.create_file(version="IFC4X3")
project = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                              ifc_class="IfcProject", 
                                              name="ConnectPath Project")

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
                       x_length= 100,
                       y_length= 10,
                       z_length= 10)

block2 = builder.block(position= V(100,0,0), 
                       x_length= 100,
                       y_length= 10,
                       z_length= 10)

rep1 = builder.get_representation(context=body, items=[block1])
rep2 = builder.get_representation(context=body, items=[block2])


ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=wall1, 
                                                representation=rep1)

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=wall2, 
                                                representation=rep2)

# placement values are centimetres
placement1 = make_placement_matrix(0, 0, 0)

path1 = ifcopenshell.api.geometry.connect_path(file=ifcfile, 
                                               relating_element=wall1,
                                               related_element=wall2,
                                               relating_connection="ATEND",
                                               related_connection="ATSTART")


# walls have been connected into a "path" so we can 
# place the path rather than the individual walls
# Use `is_si=False`...
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=path1, 
                                                matrix=placement1, 
                                                is_si=False)


# Write out to a file
ifcfile.write("./output/geometry_connect_path1.ifc")
