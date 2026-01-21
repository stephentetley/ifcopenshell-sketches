import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.unit
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


# Create a file
ifcfile = ifcopenshell.api.project.create_file(version="IFC4X3")
project = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                              ifc_class="IfcProject", 
                                              name="Profile Rep Project")

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


## tube


tube_profile = ifcfile.create_entity("IfcCircleHollowProfileDef", 
                                     ProfileName="300CHS", 
                                     ProfileType="AREA",
                                     Radius=150,
                                     WallThickness=5)

tube_entity = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                   ifc_class='IfcBuildingElementProxy', 
                                                   name='Tube_1', 
                                                   predefined_type='NOTDEFINED')


builder1 = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)


extruded1 = builder1.extrude(profile_or_curve=tube_profile, 
                             magnitude= 60.0, 
                             position = V(0, 0, 0)) 

repr = builder1.get_representation(context=body, 
                                   items=[extruded1], 
                                   representation_type=None)

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=tube_entity, 
                                                representation=repr)

# placement values are centimetres
placement_matrix = make_placement_matrix(V(0.0, 0.0, 0.0))

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=tube_entity, 
                                                matrix=placement_matrix, 
                                                is_si=False)

# Write out to a file
ifcfile.write("./output/profile_rep1.ifc")
