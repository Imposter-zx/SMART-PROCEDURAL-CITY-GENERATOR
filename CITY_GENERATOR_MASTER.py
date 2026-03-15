import bpy
import bmesh
import random
import math
import mathutils

# ==============================================================================
# SMART PROCEDURAL CITY GENERATOR - MASTER EDITION (V5.0)
# ==============================================================================
# Author: Senior Graphics Engineer (Antigravity) & Imposter-zx
# Goal: Professional Procedural Urban Generation
# Features: Layout Synthesis, District Zoning, Skyscraper Modeling, Cinematic RIG
# ==============================================================================

# --- MASTER CONFIGURATION ---
CONF = {
    "city_size": 2000,           # Total sprawl radius
    "density": 0.8,              # 0.0 to 1.0 (Building density)
    "style": "Modern",           # Modern, Cyberpunk, Arabic, Futuristic
    "layout": "Grid",            # Grid, Organic, Radial
    "time_of_day": "Sunset",     # Day, Sunset, Night
    "generate_traffic": True,
    "cinematic_mode": True
}

# ==========================================
# 1. CORE UTILS & CLEARING
# ==========================================
def clear_scene():
    """ Wipes everything to start fresh """
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for mat in bpy.data.materials: bpy.data.materials.remove(mat)

def get_active_obj():
    """ Robust context-agnostic object retriever """
    if hasattr(bpy.context, "view_layer"): return bpy.context.view_layer.objects.active
    return bpy.context.active_object

# ==========================================
# 2. LAYOUT GENERATION ENGINE
# ==========================================
def generate_layout(config):
    """ Creates road segments and building lots organically """
    roads = []
    lots = []
    
    size = config["city_size"]
    style = config["layout"]
    
    if style == "Grid":
        spacing = 300
        for i in range(-size, size + spacing, spacing):
            # Vertical
            roads.append(((i, -size), (i, size)))
            # Horizontal
            roads.append(((-size, i), (size, i)))
            
            # Subdivide into lots
            for j in range(-size, size, spacing):
                # Create 2x2 lots per block
                hs = spacing / 2 - 10
                lots.append({
                    "center": (i + spacing/4, j + spacing/4),
                    "size": (hs, hs),
                    "dist": math.sqrt((i+spacing/4)**2 + (j+spacing/4)**2)
                })
                lots.append({
                    "center": (i + 3*spacing/4, j + 3*spacing/4),
                    "size": (hs, hs),
                    "dist": math.sqrt((i+3*spacing/4)**2 + (j+3*spacing/4)**2)
                })

    elif style == "Radial":
        rings = 6
        spacing = size / rings
        for r in range(1, rings + 1):
            radius = r * spacing
            steps = r * 8
            for s in range(steps):
                a1 = (s / steps) * 2 * math.pi
                a2 = ((s + 1) / steps) * 2 * math.pi
                roads.append(((math.cos(a1)*radius, math.sin(a1)*radius), (math.cos(a2)*radius, math.sin(a2)*radius)))
                # Radial spokes
                if r < rings:
                    roads.append(((math.cos(a1)*radius, math.sin(a1)*radius), (math.cos(a1)*(radius+spacing), math.sin(a1)*(radius+spacing))))
                
                # Lots between rings
                lots.append({
                    "center": (math.cos(a1+0.1)*(radius+spacing/2), math.sin(a1+0.1)*(radius+spacing/2)),
                    "size": (spacing*0.8, (radius*2*math.pi/steps)*0.6),
                    "dist": radius
                })

    return roads, lots

# ==========================================
# 3. ADVANCED MODELING (BMESH)
# ==========================================
def create_building(center, size, style, dist_from_center):
    """ High-fidelity building synthesis """
    w, d = size
    
    # 1. Zoning Logic
    if dist_from_center < 600:
        zone = "Downtown"
        h = random.uniform(100, 300)
    elif dist_from_center < 1200:
        zone = "Commercial"
        h = random.uniform(40, 100)
    else:
        zone = "Residential"
        h = random.uniform(15, 45)

    mesh = bpy.data.meshes.new(f"Bldg_{zone}")
    obj = bpy.data.objects.new("Building", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = (center[0], center[1], 0)
    
    bm = bmesh.new()
    
    # 2. Layered Volumetrics (Architectural Flow)
    layers = 1 if zone != "Downtown" else random.randint(2, 4)
    curr_h = 0
    cw, cd = w, d
    
    for i in range(layers):
        lh = h / layers
        bmesh.ops.create_cube(bm, size=1.0)
        verts = bm.verts[-8:]
        bmesh.ops.scale(bm, vec=(cw, cd, lh), verts=verts)
        bmesh.ops.translate(bm, vec=(0, 0, curr_h + lh/2), verts=verts)
        
        # Rooftop Detailing
        if i == layers - 1:
            if zone == "Downtown" and random.random() > 0.4:
                # Antenna
                bmesh.ops.create_cone(bm, segments=8, radius1=0.4, radius2=0, depth=20)
                bmesh.ops.translate(bm, vec=(0,0, curr_h + lh + 10), verts=bm.verts[-9:])
            if zone == "Residential":
                # Pitched Roof
                top_faces = [f for f in bm.faces if f.normal.z > 0.9]
                if top_faces:
                    bmesh.ops.translate(bm, vec=(0,0, 5), verts=top_faces[0].verts[:2])

        curr_h += lh
        if zone == "Downtown": cw *= 0.8; cd *= 0.8 # Taper skyscrapers

    bm.to_mesh(mesh)
    bm.free()
    
    # 3. Material Synthesis
    apply_city_material(obj, zone, style)

def apply_city_material(obj, zone, style):
    mat = bpy.data.materials.new(name=f"Mat_{zone}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    # Base Color Palettes
    if zone == "Downtown": col = (0.2, 0.3, 0.5, 1.0)
    elif zone == "Commercial": col = (0.5, 0.4, 0.4, 1.0)
    else: col = (0.6, 0.6, 0.55, 1.0)
    
    if style == "Cyberpunk": col = (0.1, 0.05, 0.2, 1.0)
    
    if bsdf:
        bsdf.inputs['Base Color'].default_value = col
        bsdf.inputs['Metallic'].default_value = 0.8 if zone == "Downtown" else 0.1
        bsdf.inputs['Roughness'].default_value = 0.2
        
        # Neon Emission
        if style == "Cyberpunk" or (CONF["time_of_day"] != "Day" and zone == "Downtown"):
            if random.random() > 0.5:
                try:
                    if 'Emission' in bsdf.inputs:
                        bsdf.inputs['Emission'].default_value = (0.0, 0.8, 1.0, 1.0) if random.random() > 0.5 else (1.0, 0.0, 0.8, 1.0)
                        bsdf.inputs['Emission Strength'].default_value = 5.0
                except: pass
                
    obj.data.materials.append(mat)

# ==========================================
# 4. LIGHTING & CINEMATICS
# ==========================================
def setup_environment(config):
    time = config["time_of_day"]
    
    # World Sky
    world = bpy.context.scene.world
    if not world: world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()
    
    node_out = nodes.new('ShaderNodeOutputWorld')
    node_bg = nodes.new('ShaderNodeBackground')
    
    try:
        sky = nodes.new('ShaderNodeSkyTexture')
        sky.sky_type = 'NISHITA'
        if time == "Sunset": sky.sun_elevation = 0.05
        elif time == "Night": sky.sun_elevation = -0.5
        world.node_tree.links.new(sky.outputs['Color'], node_bg.inputs['Color'])
    except:
        node_bg.inputs['Color'].default_value = (0.02, 0.02, 0.05, 1.0) if time == "Night" else (0.4, 0.6, 1.0, 1.0)
        
    world.node_tree.links.new(node_bg.outputs['Background'], node_out.inputs['Surface'])
    
    # Sun
    light_data = bpy.data.lights.new(name="Sun", type='SUN')
    sun = bpy.data.objects.new(name="Sun", object_data=light_data)
    bpy.context.collection.objects.link(sun)
    sun.location = (0, 0, 1000)
    light_data.energy = 5.0 if time != "Night" else 0.1

def setup_cinematics():
    cam_data = bpy.data.cameras.new("CinematicCam")
    cam = bpy.data.objects.new("CinematicCam", cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    
    cam.animation_data_create()
    action = bpy.data.actions.new(name="CityFlythrough")
    cam.animation_data.action = action
    
    for f in range(1, 401): # 400 frames
        t = f / 400
        angle = t * 2 * math.pi
        dist = 1200 + math.sin(t*10)*200
        cam.location = (math.cos(angle)*dist, math.sin(angle)*dist, 400 + math.sin(t*5)*150)
        # Look at center
        direction = mathutils.Vector((0,0,100)) - cam.location
        cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        cam.keyframe_insert(data_path="location", frame=f)
        cam.keyframe_insert(data_path="rotation_euler", frame=f)

# ==========================================
# 5. MASTER EXECUTION
# ==========================================
def main():
    print("--- 🏙️ STARTING MASTER GENERATION ---")
    clear_scene()
    
    # 1. Environment
    setup_environment(CONF)
    
    # 2. Ground
    bpy.ops.mesh.primitive_plane_add(size=CONF["city_size"] * 2)
    ground = get_active_obj()
    ground.name = "Ground"
    
    # 3. Layout Discovery
    roads, lots = generate_layout(CONF)
    
    # 4. Rendering Infrastructure
    if CONF["cinematic_mode"]:
        setup_cinematics()
    
    # 5. Build!
    # Roads
    for r in roads:
        # Simplified road creation (single mesh or lines)
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        road_obj = get_active_obj()
        p1, p2 = r
        dx, dy = p2[0]-p1[0], p2[1]-p1[1]
        dist = math.sqrt(dx**2 + dy**2)
        road_obj.location = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, 0.05)
        road_obj.scale = (dist, 14, 0.1)
        road_obj.rotation_euler[2] = math.atan2(dy, dx)
    
    # Buildings
    step = 1 # Optimization: Render all lots
    for i in range(0, len(lots), step):
        lot = lots[i]
        if random.random() < CONF["density"]:
            create_building(lot["center"], lot["size"], CONF["style"], lot["dist"])
            
    # Final Optimization: Merge Roads
    # (Optional: Add for better viewport performance)

    print("--- 💎 MASTER CITY GENERATOR COMPLETE ---")
    print("Next: Press SPACEBAR to start flythrough!")

if __name__ == "__main__":
    main()
