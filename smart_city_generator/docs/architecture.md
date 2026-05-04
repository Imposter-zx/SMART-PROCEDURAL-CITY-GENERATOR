# Smart Procedural City Generator - Architecture

## 1. Overview
The Smart Procedural City Generator is a hybrid system combining Python for orchestration, C++ for high-performance combinatorial and geometric algorithms, and Blender (Python API) for 3D procedural generation and rendering.

## 2. Folder Structure
```text
smart_city_generator/
├── docs/
│   └── architecture.md          # This document
├── engine/                      # C++ High-Performance Engine
│   ├── CMakeLists.txt           # Build configuration
│   ├── src/
│   │   ├── generator.cpp        # C++ Python bindings (pybind11)
│   │   ├── road_generator.cpp   # Road generation algorithms
│   │   └── road_generator.h
│   └── include/
├── python_core/                 # Main City Generation Logic
│   ├── main.py                  # CLI / API entry point
│   ├── city_models.py           # Pydantic models for user input
│   └── engine_bridge.py         # Interfacing with the compiled C++ engine
├── blender_module/              # Blender Generation Scripts
│   ├── scene_setup.py           # Lighting, camera
│   ├── building_generator.py    # Procedural buildings logic
│   └── main_render.py           # Entry script for Blender headless execution
└── output/                      # Renders and exported assets
```

## 3. Data Flow
1. **User Input:** User provides parameters (e.g., city style, density, size, district types).
2. **Orchestration (Python):** Python core receives the input, validates it, and calculates **District Maps**.
3. **Generation (C++/Python Fallback):** Computes the road network and subdivides blocks into smaller lots with assigned zoning (Residential, Commercial, etc.).
4. **Data Handoff (Python -> Blender):** Formats the C++ output into a structured JSON.
5. **3D Generation (Blender):** 
   - **Roads:** Generates road meshes with sidewalks.
   - **Buildings:** District-aware procedural buildings (Skyscrapers vs Small Houses).
   - **Props:** Scatters street lights, trees, and cars.
   - **Materials:** Assigns realistic textures and shaders.
6. **Rendering:** Configures environment lighting (HDRI/Sky Texture) and renders.

## 4. GIS Integration (New)
The system now supports real-world data injection via **OpenStreetMap (OSM)**:
1.  **Extraction:** Python's `OSMNX` extracts road nodes and building footprints.
2.  **Projection:** Spherical coordinates are projected into planar meters (UTM).
3.  **Handoff:** The GIS data is fed into the C++ engine for parcel subdivision and geometric optimization.

## 5. Technologies
- **Python**: `pydantic`, `numpy`, `osmnx`, `geopandas`
- **C++**: `pybind11` (for Python bindings)
- **Blender**: `bpy` (Blender Python API), `bmesh`

