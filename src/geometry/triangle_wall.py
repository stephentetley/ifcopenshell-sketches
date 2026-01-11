import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.unit
import ifcopenshell.api.geometry
import ifcopenshell.api.root
from ifcopenshell.util.shape_builder import V
import ifcopenshell.util.data
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

    

# Create a blank model
ifcfile = ifcopenshell.api.project.create_file(version="IFC4X3")
project = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                              ifc_class="IfcProject", 
                                              name="Triangle Wall Project")

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


## wall_1

wall1 = ifcopenshell.api.root.create_entity(file=ifcfile,  
                                            ifc_class='IfcWall', 
                                            name='Wall_1', 
                                            predefined_type='NOTDEFINED')




# triangle - base=0.5m, height=0.30m
triangle_base = 0.5
triangle_height = 0.30

clip1 = ifcopenshell.util.data.Clipping(location=(0.0, 0.0, 0.0), 
                                        normal=(-triangle_height, 0.0, triangle_base))
clipping_list = [clip1]

# height here is arbitrary, must be >= triangle_height 
wrep = ifcopenshell.api.geometry.add_wall_representation(file=ifcfile,
                                                         context=body,
                                                         length=triangle_base,
                                                         height=triangle_height + 1.0,
                                                         thickness=0.1,
                                                         clippings=clipping_list
                                                         )


ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=wall1, 
                                                representation=wrep)



# placement values are centimetres
placement1 = make_placement_matrix(0, 0, 0)



# Use `is_si=False`...  
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=wall1, 
                                                matrix=placement1, 
                                                is_si=False)


# Write out to a file
ifcfile.write("./output/geometry_triangle_wall1.ifc")

