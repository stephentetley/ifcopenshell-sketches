import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.unit
import ifcopenshell.api.geometry
import ifcopenshell.api.root
from ifcopenshell.util.shape_builder import V
import ifcopenshell.util.shape_builder
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
                                              name="Rotate Translate Project")

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


## Block_1

entity_proxy1 = ifcopenshell.api.root.create_entity(file=ifcfile,  
                                                   ifc_class='IfcBuildingElementProxy', 
                                                   name='Block_1', 
                                                   predefined_type='NOTDEFINED')

builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)

rect1 = builder.rectangle(size=V(100, 10), position = V(0, 0))

# block1 = builder.block(position=V(0.0, 0.0, 0.0),
#                           x_length = 100.0,
#                           y_length = 10.0,
#                           z_length = 50.0)



extruded_rect = builder.extrude(profile_or_curve=rect1, 
                                magnitude=50.0)

builder.rotate(curve_or_item=extruded_rect, 
                  angle=-45.0,
                  create_copy=False)

builder.translate(curve_or_item=extruded_rect, 
                  translation=V(100, 0, 0),
                  create_copy=False)

builder.translate(curve_or_item=extruded_rect, 
                  translation=V(30, 0, 0),
                  create_copy=False)





representation = builder.get_representation(context=body, items=[extruded_rect])

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=entity_proxy1, 
                                                representation=representation)


# placement values are centimetres
placement1 = make_placement_matrix(0, 0, 0)

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=entity_proxy1, 
                                                matrix=placement1, 
                                                is_si=False)


# Write out to a file
ifcfile.write("./output/builder_rotate_and_translate1.ifc")

