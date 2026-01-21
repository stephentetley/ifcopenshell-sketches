import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.placement
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
                                              name="Blocks Difference2 Project")

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

builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)

block1 = builder.block(position=V(0, 0, 0), 
                       x_length=40.0,
                       y_length=40.0,
                       z_length=20.0)

block2 = builder.block(position=V(5, 5, 0), 
                       x_length=30.0,
                       y_length=30.0,
                       z_length=20.0)                       



repr = builder.get_representation(context=body, items=[block1, block2], representation_type=None)
booleans = ifcopenshell.api.geometry.add_boolean(file=ifcfile,
                                      first_item=block1,
                                      second_items=[block2],
                                      operator='DIFFERENCE')


ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=proxy1, 
                                                representation=repr)

# placement values are centimetres
placement_proxy1 = make_placement_matrix(V(0.0, 0.0, 0.0))

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=proxy1, 
                                                matrix=placement_proxy1, 
                                                is_si=False)


# Write out to a file
ifcfile.write("./output/add_boolean_blocks_difference2.ifc")

