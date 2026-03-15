import bpy
import bmesh
import random
import math
import mathutils
import os
import sys

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from material_system import get_style_palette, apply_random_material

def create_building(location, dimensions, style, zone):
    """
    Procedurally generate a building mesh.
    zone: downtown / residential / commercial / industrial
    """
    w, d, h = dimensions
    
    # Zone-based height adjustments
    if zone == "downtown":
        h = random.uniform(60, 150) # Skyscrapers
    elif zone == "commercial":
        h = random.uniform(30, 70)
    elif zone == "residential":
        h = random.uniform(10, 25) # Houses
    elif zone == "industrial":
        w *= 1.5
        d *= 1.5
        h = random.uniform(15, 30)
    
    mesh = bpy.data.meshes.new(f"Bldg_{zone}")
    obj = bpy.data.objects.new("Building", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    bm = bmesh.new()
    
    # 1. Base footprint
    v1 = bm.verts.new((-w/2, -d/2, 0))
    v2 = bm.verts.new((w/2, -d/2, 0))
    v3 = bm.verts.new((w/2, d/2, 0))
    v4 = bm.verts.new((-w/2, d/2, 0))
    base_face = bm.faces.new((v1, v2, v3, v4))
    
    # 2. Extrude Main Body
    ret = bmesh.ops.extrude_discrete_faces(bm, faces=[base_face])
    top_face = ret['faces'][0]
    bmesh.ops.translate(bm, vec=(0, 0, h), verts=top_face.verts)
    
    # 3. Procedural Style logic
    palette = get_style_palette(style)
    
    if style == "cyberpunk":
        # Add a glowing middle section
        if h > 40:
            bmesh.ops.inset_region(bm, faces=[top_face], thickness=1.0, depth=0)
            ret = bmesh.ops.extrude_discrete_faces(bm, faces=[top_face])
            top_face = ret['faces'][0]
            bmesh.ops.translate(bm, vec=(0, 0, h*0.2), verts=top_face.verts)
        
        # Add antenna for high buildings
        if h > 80:
            bmesh.ops.inset_region(bm, faces=[top_face], thickness=w*0.4, depth=0)
            ret = bmesh.ops.extrude_discrete_faces(bm, faces=[top_face])
            bmesh.ops.translate(bm, vec=(0, 0, 15), verts=ret['faces'][0].verts)

    elif style == "medieval" or (zone == "residential" and style == "modern"):
        # Simple pitched roof
        verts = top_face.verts[:]
        bmesh.ops.translate(bm, vec=(0, 0, 4.0), verts=[verts[0], verts[1]])
        
    elif style == "futuristic":
        # Dramatic twist
        bmesh.ops.rotate(bm, cent=top_face.calc_center_bounds(), matrix=mathutils.Matrix.Rotation(math.radians(30), 3, 'Z'), verts=top_face.verts)
        # Inset and extrude again
        bmesh.ops.inset_region(bm, faces=[top_face], thickness=w*0.1, depth=-1.0)

    # Finalize Mesh
    bm.to_mesh(mesh)
    
    # 4. Add Window Geometry (High Detail)
    if h > 20:
        create_window_grid(obj, h, w, d)

    bm.free()
    
    # Apply Material based on palette
    apply_random_material(obj, palette)
    
    return obj

def create_window_grid(obj, h, w, d):
    """ Generates window-like subdivisions on building faces using BMesh """
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    # We only target side faces (vertical ones)
    faces_to_process = [f for f in bm.faces if abs(f.normal.z) < 0.1]
    
    for f in faces_to_process:
        # Inset for a "frame" effect
        # Simple subdivision approach for windows
        # (This is a simplified version for performance)
        res = bmesh.ops.inset_region(bm, faces=[f], thickness=0.5, depth=-0.2)
        
    bm.to_mesh(obj.data)
    bm.free()

def generate_city_from_data(geometry_data, style):
    """ Builds the city using the new lot-based data """
    lots = geometry_data.get("lots", [])
    
    print(f"Generating {len(lots)} building lots...")
    for lot in lots:
        poly = lot['footprint']
        zone = lot['zone']
        
        cx = sum(p['x'] for p in poly) / len(poly)
        cy = sum(p['y'] for p in poly) / len(poly)
        
        # Calculate bounding box for dimensions
        xs = [p['x'] for p in poly]
        ys = [p['y'] for p in poly]
        width = max(xs) - min(xs)
        depth = max(ys) - min(ys)
        
        create_building((cx, cy, 0), (width, depth, 15), style, zone)
        
    # Handle Parks (simplified scatter)
    parks = geometry_data.get("parks", [])
    for park in parks:
        # Create a simple green plane for the park
        mesh = bpy.data.meshes.new("Park")
        obj = bpy.data.objects.new("Park", mesh)
        bpy.context.collection.objects.link(obj)
        bm = bmesh.new()
        p_verts = [bm.verts.new((p['x'], p['y'], 0.1)) for p in park]
        bm.faces.new(p_verts)
        bm.to_mesh(mesh)
        bm.free()
        
        # Green color
        mat = bpy.data.materials.new(name="ParkGrass")
        mat.diffuse_color = (0.1, 0.5, 0.1, 1.0)
        obj.data.materials.append(mat)
        
        # Scatter Trees in park
        cx = sum(p['x'] for p in park) / len(park)
        cy = sum(p['y'] for p in park) / len(park)
        for _ in range(10):
            tx = cx + random.uniform(-50, 50)
            ty = cy + random.uniform(-50, 50)
            try:
                from street_generator import place_street_prop
                place_street_prop("tree", (tx, ty, 0))
            except: pass

if __name__ == "__main__":
    generate_city_from_data({}, "modern")
