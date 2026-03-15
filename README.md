# 🏙️ Smart Procedural City Generator

A powerful, high-performance procedural generation suite that combines **Python orchestration**, **C++ algorithmic speed**, and **Blender 3D visualization**. Generate entire realistic cities in seconds with professional urban zoning, advanced materials, and cinematic flythroughs.

![City Preview](https://img.shields.io/badge/Status-Professional_Edition-brightgreen)
![Blender](https://img.shields.io/badge/Blender-4.2%2B-orange)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)

---

## 🚀 Key Features

- **🏛️ Urban Zoning System:** Intelligent subdivision into **Downtown (Skyscrapers)**, **Residential (Houses)**, **Commercial**, and **Parks**.
- **🛣️ Advanced Road Layouts:** Support for **Grid**, **Organic**, **Radial**, and **Voronoi/European** street patterns.
- **💎 High-Fidelity Details:** Procedural **window grids**, street-level **vehicles**, street lights, and localized vegetation.
- **🎨 PBR Material Suite:** Dynamic palettes for **Cyberpunk (Neon)**, **Medieval (Stone/Wood)**, **Futuristic**, and **Modern** aesthetics.
- **🎬 Cinematic Pipeline:** Automatic **Nishita Sky** lighting setup and a pre-configured 250-frame animated flythrough camera.
- **⚡ High Performance:** Optimized batch mesh processing to prevent Blender freezing during large-scale generations.

---

## 🛠️ Installation

1. **Clone the Repo:**
   ```bash
   git clone https://github.com/Imposter-zx/SMART-PROCEDURAL-CITY-GENERATOR.git
   cd SMART-PROCEDURAL-CITY-GENERATOR
   ```

2. **Install Dependencies:**
   ```bash
   pip install pydantic numpy shapely
   ```

3. **Blender Setup:** Ensure you have **Blender 4.0+** installed and added to your system PATH.

---

## 🎮 How to Use

### Step 1: Generate Geometry
Run the CLI to generate the city data using your desired style and density:
```bash
python smart_city_generator/python_core/cli.py --city_type cyberpunk --road_style voronoi --time night --density 0.8
```

### Step 2: View in Blender
1. Open **Blender**.
2. Go to the **Scripting** tab.
3. Open `smart_city_generator/MONOLITH_DEBUG.py` and click **Run Script**.
4. Press **Spacebar** in the viewport to watch the cinematic flythrough.

---

## 🏗️ Architecture

- **Python Core:** Orchestrates the logic, performs district subdivision, and handles CLI inputs.
- **Blender Module:** Procedural mesh generation using `bmesh` and advanced PBR material assignment.
- **C++ Engine (Optional):** High-speed core for complex road network calculations.

---

## 🌟 License
Distributed under the MIT License. See `LICENSE` for more information.

---
*Created with ❤️ by Antigravity & Imposter-zx*
