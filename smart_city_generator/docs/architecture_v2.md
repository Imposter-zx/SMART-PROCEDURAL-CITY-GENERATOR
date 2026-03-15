# Smart Procedural City Generator - Advanced GIS Architecture

## System Overview
The system now supports real-world data injection via OpenStreetMap (OSM), allowing it to synthesize 1:1 city layouts with high-fidelity procedural detail.

```mermaid
graph TD
    A[User Input: City Name] --> B[OSM Processor]
    B -->|Fetch Roads/Buildings| C[GeoPandas / OSMNX]
    C -->|Projected UTM| D[CityGeometry JSON]
    D --> E[C++ High-Performance Engine]
    E -->|Optimize Graph / Parcel Sub| F[Geometric Bundles]
    F --> G[Blender Python API]
    G -->|Advanced Procedural Modeling| H[High-Fidelity 3D City]
    H --> I[Cinematic Render / FBX Export]
```

## Key Components

### 1. GIS Layer (Python)
- **Engine:** OSMNX + GeoPandas
- **Task:** Downloads vector data from OSM. Projects spherical coordinates (Lat/Lon) to planar meters (UTM).
- **Extraction:** Isolates building footprints, road hierarchy (Motorway vs Residential), and environmental zones (Parks/Water).

### 2. Algorithmic Layer (C++)
- **Optimization:** Simplifies dense GIS road graphs into clean geometric meshes.
- **Zoning:** Automates lot subdivision using recursive Voronoi or OBB (Oriented Bounding Box) splitting.

### 3. Rendering Layer (Blender)
- **Materials:** PBR shaders for glass, asphalt, and concrete.
- **Cinematic Studio:** Automated camera rigs for flythroughs and atmospheric lighting (Nishita Sky).
```
