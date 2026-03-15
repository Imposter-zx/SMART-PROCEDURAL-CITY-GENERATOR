import json
import subprocess
import os
import sys

# Add the current directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from city_models import CityParameters, CityGeometry

# Mock import for the C++ engine
try:
    import smart_city_engine
except ImportError:
    smart_city_engine = None
    print("Warning: C++ engine not found. Using high-performance Python fallback.")

def generate_city(params: CityParameters) -> CityGeometry:
    print(f"Phase 2 Generation: {params.city_size} {params.city_type} city.")
    
    if smart_city_engine:
        # C++ engine logic would need update to Phase 2 models
        # For now, we prefer the enhanced Python fallback for realism
        from python_fallback import generate_roads_fallback
        geometry = generate_roads_fallback(params.city_size, params.road_style, params.building_density)
    else:
        from python_fallback import generate_roads_fallback
        geometry = generate_roads_fallback(params.city_size, params.road_style, params.building_density)
    
    # Export to output
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    temp_file = os.path.join(output_dir, "temp_geometry.json")
    
    # Handling Pydantic V1/V2 serialization
    geometry_json = ""
    if hasattr(geometry, "model_dump_json"):
        geometry_json = geometry.model_dump_json()
    elif hasattr(geometry, "json"):
        geometry_json = geometry.json()
    else:
        import json
        geometry_json = json.dumps(geometry, default=lambda o: o.__dict__, indent=2)

    with open(temp_file, "w") as f:
        f.write(geometry_json)
        
    print(f"Advanced geometry saved to {temp_file}")
    
    # Run Blender
    run_blender_generation(temp_file, params.city_type, params.time_of_day)
    
    return geometry

def run_blender_generation(geometry_file: str, style: str, time_of_day: str):
    blender_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "blender_module", "main_render.py"))
    
    # Check if blender is in path
    cmd = [
        "blender", "--background", "--python", blender_script,
        "--", "--geometry", geometry_file, "--style", style, "--time", time_of_day
    ]
    
    print(f"Launching Blender Phase 2 Pipeline...")
    # subprocess.run(cmd) - only if blender in path
