import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.geometry
from ifcopenshell.util.shape_builder import V
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
                                              name="Site Shape with Opening Project")

model3d = ifcopenshell.api.context.add_context(file=ifcfile, context_type="Model")

length = ifcopenshell.api.unit.add_si_unit(file=ifcfile, unit_type="LENGTHUNIT", prefix="MILLI")
ifcopenshell.api.unit.assign_unit(file=ifcfile, units=[length])

site_extent = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                              ifc_class="IfcBuildingElementProxy", 
                                              name="Site Extent")

body = ifcopenshell.api.context.add_context(file=ifcfile,
                                            context_type="Model", 
                                            context_identifier="Body", 
                                            target_view="MODEL_VIEW", 
                                            parent=model3d)

builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)


# polygon
points = [
    V(-271.25, 698.25),
    V(1100.75, 1734.25),
    V(2157.75, 3064.25),
    V(3347.75, 3951.50),
    V(4131.75, 2966.25),
    V(5384.75, 1480.50),
    V(5377.75, 913.50),
    V(4229.75, 159.25),
    V(2325.75, -1008.00),
    V(1037.75, -1729.00),
    V(1.75, -3227.00),
    V(-628.25, -4123.00),
    V(-1342.25, -3437.00),
    V(-2574.25, -2079.00),
    V(-2854.25, -1127.00),
    V(-3092.25, -637.00),
    V(-2084.25, -105.00),
    V(-670.25, 385.00),
    V(-271.25, 698.25)
]

position = V(0, 0)
# #2=IfcIndexedPolyCurve(#1,(IfcLineIndex((1,2,3,4,1))),$)
polyline = builder.polyline(points, closed=True, position_offset=position)

# 
# extrpolyline1 = polyline


extrpolyline1 = builder.extrude(profile_or_curve=polyline, 
                                magnitude= 1.0, 
                                position = V(0, 0, 0)) 

representation = builder.get_representation(context=body, items=[extrpolyline1])

ifcopenshell.api.geometry.assign_representation(file=ifcfile, product=site_extent, representation=representation)

site_ext_placement_matrix = make_placement_matrix(0, 0, 0)

ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=site_extent,
                                                matrix=site_ext_placement_matrix)

# Create an opening for a circular tank
opening = ifcopenshell.api.root.create_entity(file=ifcfile, 
                                              ifc_class="IfcOpeningElement")

builder2 = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file=ifcfile)


cirle1 = builder2.circle(center=V(0.0, 0.0),
                         radius = 320.0)  


cylinder1 = builder.extrude(profile_or_curve=builder.profile(cirle1), 
                            magnitude= 1.0, 
                            position = V(0, 0, 0)) 


cyrepr = builder.get_representation(context=body, items=[cylinder1])
ifcopenshell.api.geometry.assign_representation(file=ifcfile, 
                                                product=opening, 
                                                representation=cyrepr)

tank_opening_placement_matrix = make_placement_matrix(1200, -600, 0)

ifcopenshell.api.geometry.edit_object_placement(file=ifcfile, 
                                                product=opening, 
                                                matrix=tank_opening_placement_matrix, 
                                                is_si=False)

# The opening will now void the wall.
ifcopenshell.api.feature.add_feature(file=ifcfile, feature=opening, element=site_extent)

# Write out to a file
ifcfile.write("./output/builder_site_with_opening1.ifc")

