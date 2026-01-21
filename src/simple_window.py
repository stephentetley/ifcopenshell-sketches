import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
from ifcopenshell.api.geometry.add_window_representation import WindowPanelProperties, WindowLiningProperties
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
                                              name="Simple Window Project")

model3d = ifcopenshell.api.context.add_context(file=ifcfile, context_type="Model")


# To investigate - add_window_representation not producing the 
# expected drawing if we use CENTI units
length = ifcopenshell.api.unit.add_si_unit(file=ifcfile, 
                                           unit_type="LENGTHUNIT", 
                                           prefix="MILLI")
ifcopenshell.api.unit.assign_unit(file=ifcfile, units=[length])

body = ifcopenshell.api.context.add_context(file=ifcfile,
                                            context_type="Model", 
                                            context_identifier="Body", 
                                            target_view="MODEL_VIEW", 
                                            parent=model3d)
## window_1

window1 = ifcopenshell.api.root.create_entity(file=ifcfile,  
                                            ifc_class='IfcWindow', 
                                            name='Window_1', 
                                            predefined_type='NOTDEFINED')

lining_props = WindowLiningProperties(LiningDepth=50.0, LiningOffset=50.0)
panel_props = WindowPanelProperties(FrameDepth=35.0, FrameThickness=35.0)


wrep = ifcopenshell.api.geometry.add_window_representation(file=ifcfile,
                                                           context=body,
                                                           overall_height=1200.0,
                                                           overall_width=400.0,
                                                           lining_properties=lining_props,
                                                           panel_properties=[panel_props])

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=window1, 
                                                representation=wrep)


placement_matrix = make_placement_matrix(V(0.0, 0.0, 0.0))

ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=window1,
                                                matrix=placement_matrix)

# Write out to a file
ifcfile.write("./output/simple_window1.ifc")

