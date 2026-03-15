import sys
import argparse
import json
import os
import bpy

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from scene_setup import clear_scene, setup_lighting, setup_camera
from building_generator import generate_city_from_data
from street_generator import create_road_mesh, place_street_prop

def main():
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser()
    parser.add_argument("--geometry", required=True)
    parser.add_argument("--style", required=True)
    parser.add_argument("--time", default="day")
    
    args = parser.parse_args(argv)
    
    with open(args.geometry, "r") as f:
        geometry_data = json.load(f)
        
    clear_scene()
    setup_lighting(args.style) # (Would be updated for time of day)
    setup_camera()
    
    # 1. Generate Streets and Props
    roads = geometry_data.get("roads", [])
    for road in roads:
        start = (road['start']['x'], road['start']['y'])
        end = (road['end']['x'], road['end']['y'])
        create_road_mesh(start, end, road['width'], road['type'])
        
        # Simple prop scattering along segments
        if road['type'] == "local":
            place_street_prop("light", (start[0] + (end[0]-start[0])*0.5, start[1] + (end[1]-start[1])*0.5))

    # 2. Generate Buildings (District aware)
    generate_city_from_data(geometry_data, args.style)
    
    # Save
    output_blend = os.path.abspath(os.path.join(current_dir, "..", "output", "pro_city_v2.blend"))
    os.makedirs(os.path.dirname(output_blend), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=output_blend)
    print(f"Successfully rendered Phase 2 City to: {output_blend}")

if __name__ == "__main__":
    main()
