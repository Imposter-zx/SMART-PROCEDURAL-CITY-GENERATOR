import bpy

def clear_scene():
    """ Delete all existing objects in the default Blender scene """
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
    except:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

def setup_lighting(style, time_of_day="day"):
    """ Professional lighting setup that works on ANY Blender version """
    
    # 1. Skip Render Engine setting if it causes issues - EEVEE is usually default
    try:
        if hasattr(bpy.context.scene.render, "engine"):
            # Try to find a valid engine
            valid_engines = ['BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'CYCLES']
            for eng in valid_engines:
                try:
                    bpy.context.scene.render.engine = eng
                    break
                except:
                    continue
    except:
        pass # Better to have a city without custom engine than no city at all
    
    # Enable Bloom/AO if available
    try:
        if hasattr(bpy.context.scene, "eevee"):
            bpy.context.scene.eevee.use_bloom = True
            bpy.context.scene.eevee.use_gtao = True
    except:
        pass

    # 2. Setup World Sky
    try:
        world = bpy.context.scene.world
        if not world:
            world = bpy.data.worlds.new("World")
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
    except:
        pass
    
    # 3. Sunlight
    try:
        light_data = bpy.data.lights.new(name="SunLight", type='SUN')
        light_obj = bpy.data.objects.new(name="SunLight", object_data=light_data)
        bpy.context.collection.objects.link(light_obj)
        light_obj.location = (0, 0, 100)
        light_obj.rotation_euler = (0.7, 0, 0.7)
        light_data.energy = 4.0 if time_of_day == "day" else 0.2
    except:
        pass

def setup_camera():
    """ Setup a cinematic 3D perspective camera """
    try:
        cam_data = bpy.data.cameras.new("MainCamera")
        cam_obj = bpy.data.objects.new("MainCamera", cam_data)
        bpy.context.collection.objects.link(cam_obj)
        cam_obj.location = (500, -500, 400)
        cam_obj.rotation_euler = (0.8, 0, 0.785)
        bpy.context.scene.camera = cam_obj
        cam_data.lens = 28
        return cam_obj
    except:
        return None

def setup_flythrough(cam_obj):
    """ Animates the camera for a cinematic flythrough """
    if not cam_obj: return
    try:
        cam_obj.animation_data_create()
        cam_obj.animation_data.action = bpy.data.actions.new(name="Flythrough")
        cam_obj.location = (600, -600, 500)
        cam_obj.keyframe_insert(data_path="location", frame=1)
        cam_obj.location = (-400, 400, 300)
        cam_obj.keyframe_insert(data_path="location", frame=250)
    except:
        pass

def setup_terrain(size=5000):
    """ Creates a ground plane """
    try:
        bpy.ops.mesh.primitive_plane_add(size=size, location=(0,0,0))
        ground = None
        if hasattr(bpy.context, "view_layer"):
            ground = bpy.context.view_layer.objects.active
        elif hasattr(bpy.context, "active_object"):
            ground = bpy.context.active_object
        
        if ground:
            ground.name = "Terrain"
            mat = bpy.data.materials.new(name="TerrainMat")
            ground.data.materials.append(mat)
    except:
        pass
