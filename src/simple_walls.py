import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.unit
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
                                              name="Simple Walls Project")

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

wall_thickness_metres = 0.01

## Wall_1

wall1 = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                            ifc_class='IfcWall', 
                                            name='Wall_1', 
                                            predefined_type='NOTDEFINED')


wrep1 = ifcopenshell.api.geometry.add_wall_representation(file=ifcfile,
                                                          context=body, 
                                                          length=2.0, 
                                                          height=1.4, 
                                                          thickness=wall_thickness_metres)

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=wall1, 
                                                representation=wrep1)

# placement values are centimetres
placement_wall1 = make_placement_angle_matrix(0, 500.0, 500.0, 0)

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=wall1, 
                                                matrix=placement_wall1, 
                                                is_si=False)

## Wall_2

wall2 = ifcopenshell.api.root.create_entity(file=ifcfile,
                                            ifc_class='IfcWall', 
                                            name='Wall_2', 
                                            predefined_type='NOTDEFINED')

wrepr2 = ifcopenshell.api.geometry.add_wall_representation(file=ifcfile, 
                                                           context=body, 
                                                           length=0.6-(2*wall_thickness_metres),
                                                           height=1.4,
                                                           thickness=wall_thickness_metres)

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=wall2, 
                                                representation=wrepr2)

# placement in mm
placement_wall2 = make_placement_angle_matrix(90.0, 500.0 + 2000.0, 500.0 + (wall_thickness_metres*1000.0), 0)

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=wall2, 
                                                matrix=placement_wall2, 
                                                is_si=False)

# Write out to a file
ifcfile.write("./output/simple_walls1.ifc")
