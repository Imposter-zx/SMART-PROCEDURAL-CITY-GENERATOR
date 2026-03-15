import bpy
import bmesh

def create_road_mesh(start, end, width, type="local"):
    """ Generates a road segment with sidewalks """
    mesh = bpy.data.meshes.new("Road")
    obj = bpy.data.objects.new("Road", mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # Calculate direction vectors
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = (dx**2 + dy**2)**0.5
    if length == 0: return None
    
    ux = -dy / length
    uy = dx / length
    
    # Main Road Surface
    half_w = width / 2
    v1 = bm.verts.new((start[0] - ux * half_w, start[1] - uy * half_w, 0.01))
    v2 = bm.verts.new((start[0] + ux * half_w, start[1] + uy * half_w, 0.01))
    v3 = bm.verts.new((end[0] + ux * half_w, end[1] + uy * half_w, 0.01))
    v4 = bm.verts.new((end[0] - ux * half_w, end[1] - uy * half_w, 0.01))
    bm.faces.new((v1, v2, v3, v4))
    
    # Sidewalks
    sw_w = 2.0
    sw_h = 0.2
    
    # Left Sidewalk
    sv1 = bm.verts.new((start[0] - ux * (half_w + sw_w), start[1] - uy * (half_w + sw_w), 0))
    sv2 = bm.verts.new((start[0] - ux * half_w, start[1] - uy * half_w, 0))
    # ... (simplifying extrusion for now)
    
    bm.to_mesh(mesh)
    bm.free()
    
    # Material
    mat_name = "RoadAsphalt" if type == "highway" else "RoadLocal"
    # (Material logic would go here)
    
    return obj

def place_street_prop(prop_type, location, rotation=0):
    """ Scatters props like street lights, trees, and cars """
    if prop_type == "light":
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=8, location=(location[0], location[1], 4))
    elif prop_type == "tree":
        bpy.ops.mesh.primitive_cone_add(radius=1.5, depth=5, location=(location[0], location[1], 2.5))
    elif prop_type == "car":
        # Simple low-poly car mesh (box + wheels placeholder)
        bpy.ops.mesh.primitive_cube_add(size=1.0, scale=(2.5, 1.2, 0.7), location=(location[0], location[1], 0.7))
        
        # Robustly get the new object
        car = None
        if hasattr(bpy.context, "view_layer"):
            car = bpy.context.view_layer.objects.active
        elif hasattr(bpy.context, "active_object"):
            car = bpy.context.active_object
        
        if car:
            car.rotation_euler[2] = rotation
            # Random Car color
            mat = bpy.data.materials.new(name="CarColor")
            mat.diffuse_color = (random.random(), random.random(), random.random(), 1.0)
            car.data.materials.append(mat)
