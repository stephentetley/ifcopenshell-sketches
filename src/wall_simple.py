import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.unit
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
                                              name="Wall Simple Project")

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


## Wall_1

entity_wall1 = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                   ifc_class='IfcWall', 
                                                   name='Wall_1', 
                                                   predefined_type='NOTDEFINED')


repr_wall1 = ifcopenshell.api.geometry.add_wall_representation(file=ifcfile,
                                                                context=body, 
                                                                length=2.0, 
                                                                height=1.4, 
                                                                thickness=0.01)

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=entity_wall1, 
                                                representation=repr_wall1)

# placement values are centimetres
placement_wall1 = make_placement_angle_matrix(0, 50.0, 50.0, 0)

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=entity_wall1, 
                                                matrix=placement_wall1, 
                                                is_si=False)

## Wall_1

entity_wall2 = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                   ifc_class='IfcWall', 
                                                   name='Wall_2', 
                                                   predefined_type='NOTDEFINED')

repr_wall2 = ifcopenshell.api.geometry.add_wall_representation(file=ifcfile, 
                                                               context=body, 
                                                               length=0.6,
                                                               height=1.4,
                                                               thickness=0.01)

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=entity_wall2, 
                                                representation=repr_wall2)


placement_wall2 = make_placement_angle_matrix(90.0, 50.0 + 200.0, 50.0, 0)

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=entity_wall2, 
                                                matrix=placement_wall2, 
                                                is_si=False)

# Write out to a file
ifcfile.write("./output/wall_simple1.ifc")
