import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.unit
import ifcopenshell.api.root
import ifcopenshell.util.placement
import ifcopenshell.util.shape_builder
import ifcopenshell.util.shape
import ifcopenshell.geom
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
                                              name="Sphere Project")

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


## sphere1

sphere_entity = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                                   ifc_class='IfcBuildingElementProxy', 
                                                   name='Sphere_1', 
                                                   predefined_type='NOTDEFINED')

builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)

bsphere1 = builder.sphere(radius=50.0, center=V(0, 0, 0))



repr = builder.get_representation(context=body, 
                                   items=[bsphere1], 
                                   representation_type=None)

ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=sphere_entity, 
                                                representation=repr)

# placement values are centimetres
placement_proxy1 = make_placement_matrix(V(0.0, 0.0, 0))

# need to use `is_si=False`
ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=sphere_entity, 
                                                matrix=placement_proxy1, 
                                                is_si=False)

settings = ifcopenshell.geom.settings()


shape1 = ifcopenshell.geom.create_shape(settings=settings, inst=sphere_entity)
area = ifcopenshell.util.shape.get_area(geometry=shape1.geometry)
print(f"Area: {area}")
verts = ifcopenshell.util.shape.get_shape_vertices(shape=shape1, geometry=shape1.geometry)
bbox = ifcopenshell.util.shape.get_bbox(vertices=verts)
print(f"BBox: {bbox}")


# Write out to a file
ifcfile.write("./output/builder_sphere1.ifc")
