import bpy
import bmesh
import json
import os
import random
import math

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
    except: pass

# ==========================================
# 2. BATCH GENERATOR (SUPER FAST)
# ==========================================

def create_city_batch(data):
    style = data.get("style", "modern")
    
    # --- 1. ROADS ---
    print("Generating Roads...")
    road_mesh = bpy.data.meshes.new("Roads")
    road_obj = bpy.data.objects.new("Roads", road_mesh)
    bpy.context.collection.objects.link(road_obj)
    bm_road = bmesh.new()
    
    roads = data.get("roads", [])
    for r in roads:
        start, end = r['start'], r['end']
        width = r['width']
        dx, dy = end['x']-start['x'], end['y']-start['y']
        length = math.sqrt(dx**2 + dy**2)
        if length < 0.1: continue
        ux, uy = -dy/length, dx/length
        hw = width/2
        
        v1 = bm_road.verts.new((start['x']-ux*hw, start['y']-uy*hw, 0.01))
        v2 = bm_road.verts.new((start['x']+ux*hw, start['y']+uy*hw, 0.01))
        v3 = bm_road.verts.new((end['x']+ux*hw, end['y']+uy*hw, 0.01))
        v4 = bm_road.verts.new((end['x']-ux*hw, end['y']-uy*hw, 0.01))
        bm_road.faces.new((v1, v2, v3, v4))
        
    bm_road.to_mesh(road_mesh)
    bm_road.free()
    
    # --- 2. BUILDINGS ---
    print("Generating Buildings...")
    bldg_mesh = bpy.data.meshes.new("Buildings")
    bldg_obj = bpy.data.objects.new("Buildings", bldg_mesh)
    bpy.context.collection.objects.link(bldg_obj)
    bm_bldg = bmesh.new()
    
    lots = data.get("lots", [])
    for lot in lots:
        poly = lot['footprint']
        cx = sum(p['x'] for p in poly) / len(poly)
        cy = sum(p['y'] for p in poly) / len(poly)
        
        # Simple height based on zone
        zone = lot['zone']
        if zone == "downtown": h = random.uniform(100, 250)
        elif zone == "residential": h = random.uniform(15, 40)
        else: h = random.uniform(40, 80)
        
        # Create footprint verts
        verts = [bm_bldg.verts.new((p['x'], p['y'], 0)) for p in poly]
        face = bm_bldg.faces.new(verts)
        
        # Extrude
        res = bmesh.ops.extrude_face_region(bm_bldg, geom=[face])
        verts_extruded = [v for v in res['geom'] if isinstance(v, bmesh.types.BMVert)]
        bmesh.ops.translate(bm_bldg, vec=(0,0,h), verts=verts_extruded)
        
    bm_bldg.to_mesh(bldg_mesh)
    bm_bldg.free()
    
    # --- 3. MATERIALS ---
    mat_r = bpy.data.materials.new("RoadMat")
    mat_r.diffuse_color = (0.05, 0.05, 0.05, 1)
    road_obj.data.materials.append(mat_r)
    
    mat_b = bpy.data.materials.new("BldgMat")
    mat_b.diffuse_color = (0.6, 0.6, 0.7, 1)
    bldg_obj.data.materials.append(mat_b)

def main():
    if not os.path.exists(GEO_PATH):
        print("Fatal: JSON not found")
        return
        
    with open(GEO_PATH, 'r') as f:
        data = json.load(f)
        
    print("Cleaning...")
    clear_scene()
    
    print("Setup Scene...")
    setup_lighting(data.get("style"), data.get("time", "day"))
    
    print("Starting Batch Build...")
    create_city_batch(data)
    
    # Ground
    bpy.ops.mesh.primitive_plane_add(size=5000)
    
    print("Done!")

if __name__ == "__main__":
    main()
