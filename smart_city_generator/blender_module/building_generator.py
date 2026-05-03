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

def create_building(center, size, style, zone):
    """ Advanced building generator with zoning and styling """
    w, d, h_target = size
    
    # 1. Zone-Specific Scaling
    if zone == "downtown":
        h = random.uniform(80, 220)
        is_skyscraper = True
    elif zone == "commercial":
        h = random.uniform(30, 80)
        is_skyscraper = False
    else: # Residential / Secondary
        h = random.uniform(10, 30)
        is_skyscraper = False

    mesh = bpy.data.meshes.new("Bldg")
    obj = bpy.data.objects.new("Building", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = (center[0], center[1], 0)
    
    bm = bmesh.new()
    
    # 2. Layered Architecture (Podiums & Steps)
    current_h = 0
    layers = 1 if not is_skyscraper else random.randint(2, 4)
    layer_w, layer_d = w, d
    
    for i in range(layers):
        layer_h = h / layers
        # Create Layer Cube
        bmesh.ops.create_cube(bm, size=1.0)
        # Transform Layer
        v_start = len(bm.verts) - 8
        layer_verts = bm.verts[v_start:]
        bmesh.ops.scale(bm, vec=(layer_w, layer_d, layer_h), verts=layer_verts)
        bmesh.ops.translate(bm, vec=(0, 0, current_h + layer_h/2), verts=layer_verts)
        
        # Inset for next layer if skyscraper
        if is_skyscraper and i < layers - 1:
            layer_w *= 0.8
            layer_d *= 0.8
        
        current_h += layer_h

    # 3. Rooftop Equipment
    if is_skyscraper:
        # Antenna
        if random.random() > 0.5:
            bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.5, radius2=0, depth=15)
            # Find the new verts and move them to top
            bmesh.ops.translate(bm, vec=(0, 0, current_h + 7.5), verts=bm.verts[-9:])
        # Helipad Circle (Simplified)
        if random.random() > 0.8:
            bmesh.ops.create_circle(bm, cap_ends=True, segments=16, radius=5)
            bmesh.ops.translate(bm, vec=(0, 0, current_h + 0.1), verts=bm.verts[-17:])

    bm.to_mesh(mesh)
    bm.free()
    
    # 4. Detailing (Windows)
    if h > 20:
        create_window_grid(obj, h, w, d)
    
    # Apply Palette Material
    palette = get_style_palette(style)
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
        try:
            res = bmesh.ops.inset_region(bm, faces=[f], thickness=0.4, depth=-0.1)
        except: pass
        
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
        
        create_building((cx, cy, 0), (width, depth, 0), style, zone)
        
    # Handle Parks
    parks = geometry_data.get("parks", [])
    for park in parks:
        mesh = bpy.data.meshes.new("Park")
        obj = bpy.data.objects.new("Park", mesh)
        bpy.context.collection.objects.link(obj)
        bm = bmesh.new()
        p_verts = [bm.verts.new((p['x'], p['y'], 0.1)) for p in park]
        bm.faces.new(p_verts)
        bm.to_mesh(mesh)
        bm.free()
        
        mat = bpy.data.materials.new(name="ParkGrass")
        mat.diffuse_color = (0.1, 0.5, 0.1, 1.0)
        obj.data.materials.append(mat)
        
        # Scatter Trees
        cx = sum(p['x'] for p in park) / len(park)
        cy = sum(p['y'] for p in park) / len(park)
        for _ in range(10):
            tx = cx + random.uniform(-50, 50)
            ty = cy + random.uniform(-50, 50)
            try:
                from street_generator import place_street_prop
                place_street_prop("tree", (tx, ty, 0))
            except: pass

    # Handle Water
    waters = geometry_data.get("water", [])
    for poly in waters:
        mesh = bpy.data.meshes.new("Water")
        obj = bpy.data.objects.new("WaterBody", mesh)
        bpy.context.collection.objects.link(obj)
        bm = bmesh.new()
        w_verts = [bm.verts.new((p['x'], p['y'], -0.2)) for p in poly] # Slightly below ground
        bm.faces.new(w_verts)
        bm.to_mesh(mesh)
        bm.free()
        
        mat = bpy.data.materials.new(name="WaterMat")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.05, 0.2, 0.5, 1.0)
            bsdf.inputs['Metallic'].default_value = 0.9
            bsdf.inputs['Roughness'].default_value = 0.1
        obj.data.materials.append(mat)

if __name__ == "__main__":
    generate_city_from_data({}, "modern")
