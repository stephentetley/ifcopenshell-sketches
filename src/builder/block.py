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
                                              name="Block Shape Project")

model3d = ifcopenshell.api.context.add_context(file=ifcfile, context_type="Model")

length = ifcopenshell.api.unit.add_si_unit(file=ifcfile, unit_type="LENGTHUNIT", prefix="MILLI")
ifcopenshell.api.unit.assign_unit(file=ifcfile, units=[length])

element = ifcopenshell.api.root.create_entity(file=ifcfile, ifc_class="IfcBuildingElementProxy", name="Block1")

body = ifcopenshell.api.context.add_context(file=ifcfile,
                                            context_type="Model", 
                                            context_identifier="Body", 
                                            target_view="MODEL_VIEW", 
                                            parent=model3d)

builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)


block1 = builder.block(position=V(0.0, 0.0, 0.0),
                          x_length = 3000.0,
                          y_length = 800.0,
                          z_length = 1500.0)

# can't translate an IfcBlock...
# shift_to_center = V(-3000.0 / 2, -800.0 / 2)
# builder.translate(curve_or_item=block1, translation=ifcopenshell.util.shape_builder.np_to_3d(shift_to_center))

representation = builder.get_representation(context=body, items=[block1])

ifcopenshell.api.geometry.assign_representation(file=ifcfile, product=element, representation=representation)

block1_placement_matrix = make_placement_angle_matrix(45, .1, 0, 0)

ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=element,
                                                matrix=block1_placement_matrix)

# Write out to a file
ifcfile.write("./output/builder_block1.ifc")

