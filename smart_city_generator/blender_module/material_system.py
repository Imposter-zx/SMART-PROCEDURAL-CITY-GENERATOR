import bpy
import random

def create_advanced_material(name, color=(0.8, 0.8, 0.8, 1.0), metallic=0.0, roughness=0.5, emit=0.0):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Principled BSDF
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = color
    node_bsdf.inputs['Metallic'].default_value = metallic
    node_bsdf.inputs['Roughness'].default_value = roughness
    
    # Emission for cyberpunk/night mode
    if emit > 0:
        node_bsdf.inputs['Emission'].default_value = color
        node_bsdf.inputs['Emission Strength'].default_value = emit

    # Output
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def get_style_palette(style):
    if style == "cyberpunk":
        return [
            create_advanced_material("NeonBlue", (0.0, 0.5, 1.0, 1.0), emit=5.0),
            create_advanced_material("NeonPink", (1.0, 0.0, 0.5, 1.0), emit=5.0),
            create_advanced_material("DarkMetal", (0.1, 0.1, 0.1, 1.0), metallic=1.0, roughness=0.2),
            create_advanced_material("Glass", (0.8, 0.9, 1.0, 0.5), roughness=0.1)
        ]
    elif style == "medieval":
        return [
            create_advanced_material("Stone", (0.4, 0.4, 0.4, 1.0), roughness=0.8),
            create_advanced_material("Wood", (0.3, 0.2, 0.1, 1.0), roughness=0.9),
            create_advanced_material("Thatch", (0.6, 0.5, 0.2, 1.0), roughness=1.0)
        ]
    else: # modern
        return [
            create_advanced_material("Concrete", (0.6, 0.6, 0.6, 1.0), roughness=0.7),
            create_advanced_material("GlassModern", (0.7, 0.8, 1.0, 1.0), metallic=0.2, roughness=0.1),
            create_advanced_material("WhitePaint", (0.9, 0.9, 0.9, 1.0), roughness=0.5)
        ]

def apply_random_material(obj, palette):
    if not palette: return
    mat = random.choice(palette)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
