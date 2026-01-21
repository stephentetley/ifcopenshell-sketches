import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.shape_builder
from ifcopenshell.util.shape_builder import V, VectorType
import numpy
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

block1_placement_matrix = make_placement_matrix(position=V(0.1, 0.0, 0.0),
                                                rotations=[(45, 'Z')])

ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=element,
                                                matrix=block1_placement_matrix)

# Write out to a file
ifcfile.write("./output/builder_block1.ifc")

