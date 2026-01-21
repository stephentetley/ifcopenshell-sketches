import ifcopenshell.api.context
import ifcopenshell.api.project
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
                                              name="Cylinder Shape Project")

model3d = ifcopenshell.api.context.add_context(file=ifcfile, context_type="Model")

length = ifcopenshell.api.unit.add_si_unit(file=ifcfile, unit_type="LENGTHUNIT", prefix="MILLI")
ifcopenshell.api.unit.assign_unit(file=ifcfile, units=[length])

element = ifcopenshell.api.root.create_entity(file=ifcfile, ifc_class="IfcBuildingElementProxy", name="Cylinder1")

body = ifcopenshell.api.context.add_context(file=ifcfile,
                                            context_type="Model", 
                                            context_identifier="Body", 
                                            target_view="MODEL_VIEW", 
                                            parent=model3d)

builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)


cirle1 = builder.circle(center=V(0.0, 0.0),
                        radius = 2000.0)  

# "below ground"
cylinder1 = builder.extrude(profile_or_curve=builder.profile(cirle1), 
                            magnitude= 1500.0, 
                            position = V(0, 0, -1500.0)) 

representation = builder.get_representation(context=body, items=[cylinder1])

ifcopenshell.api.geometry.assign_representation(file=ifcfile, product=element, representation=representation)

cylinder1_placement_matrix = make_placement_matrix(V(0, 0, 0))

ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=element,
                                                matrix=cylinder1_placement_matrix)

# Write out to a file
ifcfile.write("./output/builder_cylinder.ifc")
