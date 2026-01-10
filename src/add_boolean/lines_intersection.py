import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
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
                                              name="AddBoolean Lines Intersection Project")

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

proxy1 = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                   ifc_class='IfcBuildingElementProxy', 
                                                   name='Proxy_1', 
                                                   predefined_type='NOTDEFINED')

builder1 = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)

line1 = builder1.rectangle(size=V(100, 5), position=V(0, 0))
extruded1 = builder1.extrude(profile_or_curve=line1, 
                            magnitude= 50.0, 
                            position = V(0, 0, 0)) 

line2 = builder1.rectangle(size=V(50, 5), position=V(90, 0))
extruded2 = builder1.extrude(profile_or_curve=line2, 
                            magnitude= 60.0, 
                            position = V(0, 0, 0)) 

repr = builder1.get_representation(context=body, items=[extruded1, extruded2], representation_type=None)
booleans = ifcopenshell.api.geometry.add_boolean(file=ifcfile,
                                      first_item=extruded1,
                                      second_items=[extruded2],
                                      operator='INTERSECTION')


ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=proxy1, 
                                                representation=repr)

# placement values are centimetres
placement_proxy1 = make_placement_angle_matrix(0, 0.0, 0.0, 0)

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=proxy1, 
                                                matrix=placement_proxy1, 
                                                is_si=False)



# Write out to a file
ifcfile.write("./output/add_boolean_lines_intersection.ifc")
