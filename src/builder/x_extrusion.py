import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.unit
import ifcopenshell.api.geometry
import ifcopenshell.api.root
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
                                              name="SB X-Axis Extrusion Project")

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

entity_proxy1 = ifcopenshell.api.root.create_entity(file=ifcfile,  
                                                   ifc_class='IfcBuildingElementProxy', 
                                                   name='Proxy_1', 
                                                   predefined_type='NOTDEFINED')

builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)

# 2D (x, y)
points1 = [V(0,0), V(100, 0), V(100, 200), V(50, 225), V(0, 200)]


# points must be in 2D to be closed...
polygon1 = builder.polyline(points = points1,
                            closed=True, 
                            arc_points=[])


solid1 = builder.extrude(profile_or_curve=polygon1, 
                         magnitude=10.0,
                         extrusion_vector=V(0,0,1)
                         )




representation = builder.get_representation(context=body, items=[solid1])


ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=entity_proxy1, 
                                                representation=representation)


# placement values are centimetres
# Use rotations to build in the yz plane and extrude on the x axis
placement1 = make_placement_matrix(position=V(0, 0, 0), 
                                   rotations=[(90, 'X'), (90, 'Z')])

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=entity_proxy1, 
                                                matrix=placement1, 
                                                is_si=False)


# Write out to a file
ifcfile.write("./output/builder_x_extrusion1.ifc")
