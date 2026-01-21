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
                                              name="SB Sweep Project")

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

curve1 = builder.polyline(points = [V(0,0,0), 
                                    V(50, 0, 0),
                                    V(87, 0, 0),  # AP
                                    V(100, 0, 20),
                                    V(113, 0, 40), # AP
                                    V(150, 0, 40),
                                    V(200,0, 40),
                                    ],
                          closed=False, 
                          arc_points=[2, 4])


swept_disk_solid1 = builder.create_swept_disk_solid(path_curve=curve1, radius=6.0)




representation = builder.get_representation(context=body, items=[swept_disk_solid1])


ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=entity_proxy1, 
                                                representation=representation)


# placement values are centimetres
placement1 = make_placement_matrix(V(0, 0, 0))

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=entity_proxy1, 
                                                matrix=placement1, 
                                                is_si=False)


# Write out to a file
ifcfile.write("./output/builder_sweep1.ifc")
