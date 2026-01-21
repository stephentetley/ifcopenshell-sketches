import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
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
                                              name="Simple Railing Project")

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
## railing_1

railing1 = ifcopenshell.api.root.create_entity(file=ifcfile,
                                               ifc_class='IfcRailing', 
                                               name='Railing_1', 
                                               predefined_type='NOTDEFINED')

rpath = [V(0, 0, 1000.0), V(1000.0, 0, 1000.0), V(2000.0, 0, 1000.0)]
rrep = ifcopenshell.api.geometry.add_railing_representation(file=ifcfile,
                                                            context=body,
                                                            railing_type='WALL_MOUNTED_HANDRAIL',
                                                            railing_path=rpath,
                                                            height=1000.0,                                                        
                                                            railing_diameter=50.0,
                                                            support_spacing=700.0,
                                                            clear_width=40.0)


ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=railing1, 
                                                representation=rrep)


placement_matrix = make_placement_matrix(V(0, 0, 0))

ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=railing1,
                                                matrix=placement_matrix)

# Write out to a file
ifcfile.write("./output/simple_railing1.ifc")

