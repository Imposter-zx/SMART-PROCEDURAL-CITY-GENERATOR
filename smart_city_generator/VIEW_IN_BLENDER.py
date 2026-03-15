import bpy
import json
import os
import sys
import random
import importlib

# PATH CONFIGURATION
GEO_PATH = r"c:\Users\HASSA\Desktop\SMART PROCEDURAL CITY GENERATOR\smart_city_generator\output\temp_geometry.json"
MODULE_PATH = r"c:\Users\HASSA\Desktop\SMART PROCEDURAL CITY GENERATOR\smart_city_generator\blender_module"

if MODULE_PATH not in sys.path:
    sys.path.append(MODULE_PATH)

# FORCE RELOAD OF MODULES
try:
    import building_generator
    import scene_setup
    import street_generator
    importlib.reload(building_generator)
    importlib.reload(scene_setup)
    importlib.reload(street_generator)
except ImportError:
    # First time import
    import building_generator
    import scene_setup
    import street_generator

def run_view():
    print("--- CITY GENERATOR START ---")
    if not os.path.exists(GEO_PATH):
        print(f"ERROR: Geometry file not found at {GEO_PATH}")
        return

    with open(GEO_PATH, 'r') as f:
        data = json.load(f)

    # 1. Clear Scene
    scene_setup.clear_scene()
    
    # 2. Setup environment
    style = data.get("style", "modern")
    time_of_day = data.get("time", "day")
    
    scene_setup.setup_lighting(style, time_of_day)
    cam = scene_setup.setup_camera()
    scene_setup.setup_terrain()
    if cam:
        scene_setup.setup_flythrough(cam)
    
    # 3. Generate Roads & Props
    roads = data.get("roads", [])
    for road in roads:
        start = (road['start']['x'], road['start']['y'])
        end = (road['end']['x'], road['end']['y'])
        street_generator.create_road_mesh(start, end, road['width'], road['type'])
        
        # Chance to place cars
        if random.random() < 0.2:
            import math
            angle = math.atan2(end[1]-start[1], end[0]-start[0])
            street_generator.place_street_prop("car", (start[0]+(end[0]-start[0])*0.3, start[1]+(end[1]-start[1])*0.3), rotation=angle)

    # 4. Generate Buildings
    building_generator.generate_city_from_data(data, style)
    
    print("--- CITY GENERATED SUCCESSFULLY ---")

if __name__ == "__main__":
    run_view()
