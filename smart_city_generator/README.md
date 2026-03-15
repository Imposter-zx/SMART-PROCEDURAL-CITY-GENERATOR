# Smart Procedural City Generator

## Requirements
- Python 3.9+
- CMake 3.15+
- C++17 compatible compiler (MSVC, GCC, Clang)
- Blender 3.6+ (Added to system PATH so the `blender` command works globally)

## Setup Instructions

### 1. Install Python Dependencies
Open a terminal in the project root and run:
```bash
pip install -r requirements.txt
```

### 2. Build the C++ Engine (Pybind11)
The Python core relies on the high-performance C++ engine. Compile it with CMake:
```bash
cd engine
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

Once built, you need to copy the resulting compiled file (e.g., `smart_city_engine.cp311-win_amd64.pyd` on Windows or `.so` on Linux) into the `python_core` folder so Python can import it.
```bash
# On Windows (adjust depending on your python version/architecture)
copy Release\smart_city_engine*.pyd ..\..\python_core\
```

### 3. Run the Generator
Navigate to the `python_core` folder and execute the Python application.
```bash
cd ../../python_core
python cli.py --size medium --style cyberpunk --density 0.8
```

This will:
1. Call Python to process inputs.
2. Trigger the compiled C++ engine to generate the math geometry.
3. Automatically launch Blender in the background to build the 3D scene.
4. Export the resulting files to the `output/` directory.
