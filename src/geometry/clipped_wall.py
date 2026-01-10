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

def d2r(deg: float) -> float:
    return (deg * math.pi) / 180

# Create a blank model
ifcfile = ifcopenshell.api.project.create_file(version="IFC4X3")
project = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                              ifc_class="IfcProject", 
                                              name="Clipped Wall Project")

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

# clip from 2 metres up the wall
clip1 = ifcopenshell.util.data.Clipping(location=(0.0, 0.0, 2.0), normal=(-1.0, 0.0, 1.0))
clip2 = ifcopenshell.util.data.Clipping(location=(1.0, 0.0, 2.0), normal=(1.0, 0.0, 1.0))


clipping_list = [clip1, clip2]

wrep = ifcopenshell.api.geometry.add_wall_representation(file=ifcfile,
                                                         context=body,
                                                         length=1.0,
                                                         height=2.5,
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
ifcfile.write("./output/geometry_clipped_wall1.ifc")

