import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
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


# Create a blank model
ifcfile = ifcopenshell.api.project.create_file(version="IFC4X3")
project = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                              ifc_class="IfcProject", 
                                              name="Simple Door Project")

model3d = ifcopenshell.api.context.add_context(file=ifcfile, context_type="Model")

length = ifcopenshell.api.unit.add_si_unit(file=ifcfile, 
                                           unit_type="LENGTHUNIT", 
                                           prefix="MILLI")
ifcopenshell.api.unit.assign_unit(file=ifcfile, units=[length])

body = ifcopenshell.api.context.add_context(file=ifcfile,
                                            context_type="Model", 
                                            context_identifier="Body", 
                                            target_view="MODEL_VIEW", 
                                            parent=model3d)
## door_1

door1 = ifcopenshell.api.root.create_entity(file=ifcfile,  
                                            ifc_class='IfcDoor', 
                                            name='Door_1', 
                                            predefined_type='NOTDEFINED')

# panel_props = ifcopenshell.api.geometry.add_door_representation.DoorPanelProperties()

drep = ifcopenshell.api.geometry.add_door_representation(file=ifcfile,
                                                         context=body,
                                                         overall_height=2000.0,
                                                         overall_width=900.0,
                                                         operation_type='SINGLE_SWING_LEFT',
                                                         panel_properties=None)

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=door1, 
                                                representation=drep)


placement_matrix = make_placement_matrix(0, 0, 0)

ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=door1,
                                                matrix=placement_matrix)

# Write out to a file
ifcfile.write("./output/simple_door1.ifc")

