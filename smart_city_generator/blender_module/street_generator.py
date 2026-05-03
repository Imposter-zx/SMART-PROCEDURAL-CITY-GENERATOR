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
    z_offset = 5.0 if type == "bridge" else 0.01
    
    v1 = bm.verts.new((start[0] - ux * half_w, start[1] - uy * half_w, z_offset))
    v2 = bm.verts.new((start[0] + ux * half_w, start[1] + uy * half_w, z_offset))
    v3 = bm.verts.new((end[0] + ux * half_w, end[1] + uy * half_w, z_offset))
    v4 = bm.verts.new((end[0] - ux * half_w, end[1] - uy * half_w, z_offset))
    face = bm.faces.new((v1, v2, v3, v4))
    
    # Bridge Supports
    if type == "bridge":
        bmesh.ops.create_cube(bm, size=2.0)
        bmesh.ops.scale(bm, vec=(2.0, 2.0, 5.0), verts=bm.verts[-8:])
        bmesh.ops.translate(bm, vec=(start[0], start[1], 2.5), verts=bm.verts[-8:])
        
        bmesh.ops.create_cube(bm, size=2.0)
        bmesh.ops.scale(bm, vec=(2.0, 2.0, 5.0), verts=bm.verts[-8:])
        bmesh.ops.translate(bm, vec=(end[0], end[1], 2.5), verts=bm.verts[-8:])
    
    bm.to_mesh(mesh)
    bm.free()
    
    # Material
    mat = bpy.data.materials.new(name="RoadMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        color = (0.05, 0.05, 0.05, 1.0) if type != "bridge" else (0.3, 0.3, 0.3, 1.0)
        bsdf.inputs['Base Color'].default_value = color
    obj.data.materials.append(mat)
    
    return obj

def place_street_prop(prop_type, location, rotation=0):
    """ Scatters props like street lights, trees, and cars """
    if prop_type == "light":
        # Post
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=7, location=(location[0], location[1], 3.5))
        # Arm
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=2, location=(location[0]+0.5, location[1], 7))
        arm = bpy.context.active_object
        arm.rotation_euler[1] = 1.57 # 90 degrees
        # Light Source
        light_data = bpy.data.lights.new(name="StreetLamp", type='POINT')
        light_obj = bpy.data.objects.new(name="StreetLamp", object_data=light_data)
        bpy.context.collection.objects.link(light_obj)
        light_obj.location = (location[0]+1.5, location[1], 6.8)
        light_data.energy = 500.0
        light_data.color = (1.0, 0.9, 0.7) # Warm light
    elif prop_type == "tree":
        # Trunk
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=2, location=(location[0], location[1], 1))
        # Leaves (Layered)
        for i in range(3):
            bpy.ops.mesh.primitive_cone_add(radius=1.5 - i*0.3, depth=2, location=(location[0], location[1], 2 + i*1.2))
            leaf = bpy.context.active_object
            mat = bpy.data.materials.new(name="LeafMat")
            mat.diffuse_color = (0.1, 0.4 + i*0.1, 0.1, 1.0)
            leaf.data.materials.append(mat)
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
