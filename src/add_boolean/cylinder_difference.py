import ifcopenshell.api.context
import ifcopenshell.api.project
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
                                              name="AddBoolean Cylinder Difference Project")

model3d = ifcopenshell.api.context.add_context(file=ifcfile, context_type="Model")

length = ifcopenshell.api.unit.add_si_unit(file=ifcfile, unit_type="LENGTHUNIT", prefix="MILLI")
ifcopenshell.api.unit.assign_unit(file=ifcfile, units=[length])

proxy1 = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                             ifc_class="IfcBuildingElementProxy", 
                                             name="Proxy1")

body = ifcopenshell.api.context.add_context(file=ifcfile,
                                            context_type="Model", 
                                            context_identifier="Body", 
                                            target_view="MODEL_VIEW", 
                                            parent=model3d)

builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)


cirle1 = builder.circle(center=V(0.0, 0.0),
                        radius = 30)  
cylinder1 = builder.extrude(profile_or_curve=builder.profile(cirle1), 
                            magnitude= 12.0, 
                            position = V(0, 0, 0)) 

cirle2 = builder.circle(center=V(0.0, 0.0),
                        radius = 24.0)  
cylinder2 = builder.extrude(profile_or_curve=builder.profile(cirle2), 
                            magnitude= 12.0, 
                            position = V(0, 0, 0)) 

booleans = ifcopenshell.api.geometry.add_boolean(file=ifcfile,
                                      first_item=cylinder1,
                                      second_items=[cylinder2],
                                      operator='DIFFERENCE')

representation = builder.get_representation(context=body, items=[cylinder1, cylinder2])

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=proxy1, 
                                                representation=representation)

cylinder1_placement_matrix = make_placement_matrix(0, 0, 0)

ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=proxy1,
                                                matrix=cylinder1_placement_matrix)

# Write out to a file
ifcfile.write("./output/add_boolean_cylinder_difference1.ifc")
