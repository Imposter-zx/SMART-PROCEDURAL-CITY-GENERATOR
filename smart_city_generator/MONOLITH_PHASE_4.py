import bpy
import bmesh
import json
import os
import random
import math
import mathutils

# ==========================================
# 1. CONFIGURATION
# ==========================================
GEO_PATH = r"c:\Users\HASSA\Desktop\SMART PROCEDURAL CITY GENERATOR\smart_city_generator\output\temp_geometry.json"

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def setup_lighting(style, time_of_day="day"):
    try:
        # Engine setup
        for eng in ['BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'CYCLES']:
            try:
                bpy.context.scene.render.engine = eng
                break
            except: continue
            
        world = bpy.context.scene.world
        if not world: world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
        world.use_nodes = True
        nodes = world.node_tree.nodes
        nodes.clear()
        
        node_out = nodes.new('ShaderNodeOutputWorld')
        node_bg = nodes.new('ShaderNodeBackground')
        
        if time_of_day == "day":
            try:
                node_sky = nodes.new('ShaderNodeSkyTexture')
                node_sky.sky_type = 'NISHITA'
                world.node_tree.links.new(node_sky.outputs['Color'], node_bg.inputs['Color'])
            except:
                node_bg.inputs['Color'].default_value = (0.7, 0.8, 1.0, 1.0)
        else:
            node_bg.inputs['Color'].default_value = (0.01, 0.01, 0.05, 1.0)
            
        world.node_tree.links.new(node_bg.outputs['Background'], node_out.inputs['Surface'])
        
        light_data = bpy.data.lights.new(name="Sun", type='SUN')
        light_obj = bpy.data.objects.new(name="Sun", object_data=light_data)
        bpy.context.collection.objects.link(light_obj)
        light_obj.location = (0, 0, 100)
        light_data.energy = 4.0 if time_of_day == "day" else 0.2
    except Exception as e:
        print(f"Lighting error (skipped): {e}")

def setup_camera():
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (800, -800, 600)
    cam_obj.rotation_euler = (0.8, 0, 0.785)
    bpy.context.scene.camera = cam_obj
    return cam_obj

def setup_flythrough(cam_obj):
    """ Animated camera path """
    cam_obj.animation_data_create()
    cam_obj.animation_data.action = bpy.data.actions.new(name="CinematicFly")
    
    # Simple orbital path
    for f in range(1, 251):
        angle = math.radians(f)
        dist = 1000
        cam_obj.location = (math.cos(angle)*dist, math.sin(angle)*dist, 400 + math.sin(f*0.05)*100)
        cam_obj.keyframe_insert(data_path="location", frame=f)

# ==========================================
# 2. ADVANCED GENERATORS
# ==========================================

def apply_mat(obj, color, emit=0.0):
    mat = bpy.data.materials.new(name="CityMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        if emit > 0:
            try:
                if 'Emission' in bsdf.inputs:
                    bsdf.inputs['Emission'].default_value = color
                    bsdf.inputs['Emission Strength'].default_value = emit
            except: pass
    obj.data.materials.append(mat)

def create_building_v4(center, size, style, zone):
    w, d = size
    if zone == "downtown":
        h = random.uniform(100, 300)
        layers = random.randint(2, 4)
    else:
        h = random.uniform(15, 50)
        layers = 1
        
    mesh = bpy.data.meshes.new("Bldg")
    obj = bpy.data.objects.new("Building", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = (center[0], center[1], 0)
    
    bm = bmesh.new()
    curr_h = 0
    curr_w, curr_d = w, d
    
    for i in range(layers):
        lh = h / layers
        bmesh.ops.create_cube(bm, size=1.0)
        verts = bm.verts[-8:]
        bmesh.ops.scale(bm, vec=(curr_w, curr_d, lh), verts=verts)
        bmesh.ops.translate(bm, vec=(0, 0, curr_h + lh/2), verts=verts)
        
        # Details on layer
        if i == layers - 1 and layers > 1: # Roof props
            bmesh.ops.create_cone(bm, segments=8, radius1=1.0, radius2=0, depth=20)
            bmesh.ops.translate(bm, vec=(0, 0, curr_h + lh + 10), verts=bm.verts[-9:])
            
        curr_h += lh
        curr_w *= 0.8
        curr_d *= 0.8

    bm.to_mesh(mesh)
    bm.free()
    
    color = (random.uniform(0.4, 0.6), random.uniform(0.4, 0.6), random.uniform(0.5, 0.7), 1.0)
    emit = 2.0 if style == "cyberpunk" and random.random() > 0.4 else 0.0
    apply_mat(obj, color, emit)

# ==========================================
# 3. MAIN EXECUTION
# ==========================================
def main():
    if not os.path.exists(GEO_PATH):
        print("Fatal: JSON not found")
        return
        
    with open(GEO_PATH, 'r') as f:
        data = json.load(f)
        
    clear_scene()
    setup_lighting(data.get("style"), data.get("time", "day"))
    cam = setup_camera()
    setup_flythrough(cam)
    
    # Ground
    bpy.ops.mesh.primitive_plane_add(size=10000)
    
    # Batch Generation
    lots = data.get("lots", [])
    for lot in lots:
        poly = lot['footprint']
        cx = sum(p['x'] for p in poly) / len(poly)
        cy = sum(p['y'] for p in poly) / len(poly)
        xs = [p['x'] for p in poly]; ys = [p['y'] for p in poly]
        create_building_v4((cx, cy), (max(xs)-min(xs), max(ys)-min(ys)), data.get("style"), lot['zone'])

    print("--- PHASE 4 GENERATION COMPLETE ---")

if __name__ == "__main__":
    main()
