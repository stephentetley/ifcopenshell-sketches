import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.unit
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.util.data
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
                                              name="Clipped Gable Wall Project")

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


## wall_1
wall_length_m = 1.0
side_height_m = 2.0
gable_height_m = 2.25

wall1 = ifcopenshell.api.root.create_entity(file=ifcfile,  
                                            ifc_class='IfcWall', 
                                            name='Wall_1', 
                                            predefined_type='NOTDEFINED')


# clip from 2 metres up the wall (side_hight_m)
triangle_height_m = gable_height_m - side_height_m
triangle_base_m = wall_length_m / 2.0
clip1 = ifcopenshell.util.data.Clipping(location=(0.0, 0.0, side_height_m), 
                                        normal=(-triangle_height_m, 0.0, triangle_base_m))
clip2 = ifcopenshell.util.data.Clipping(location=(wall_length_m, 0.0, side_height_m), 
                                        normal=(triangle_height_m, 0.0, triangle_base_m))
clipping_list = [clip1, clip2]

wrep = ifcopenshell.api.geometry.add_wall_representation(file=ifcfile,
                                                         context=body,
                                                         length=wall_length_m,
                                                         height=gable_height_m,
                                                         thickness=0.1,
                                                         clippings=clipping_list
                                                         )


ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=wall1, 
                                                representation=wrep)



# placement values are centimetres
placement1 = make_placement_matrix(V(10.0, 0, 0), rotations=[(90, 'Z')])



# Use `is_si=False`...  
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=wall1, 
                                                matrix=placement1, 
                                                is_si=False)


# Write out to a file
ifcfile.write("./output/geometry_clipped_gable_wall1.ifc")

