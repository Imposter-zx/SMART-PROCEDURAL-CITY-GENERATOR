# ⚙️ Smart City Generator: Technical Core

This directory contains the modular high-performance core of the Procedural City Generator. It is designed to be used as a standalone pipeline or integrated into larger simulations.

---

## 🛠️ Prerequisites

Ensure your environment meets the following requirements:
*   **Python:** 3.10+
*   **C++ Compiler:** C++17 compatible (MSVC 2019+, GCC 9+, Clang 10+)
*   **CMake:** 3.15+
*   **Blender:** 4.2+ (Must be accessible via system `PATH`)

---

## 🚀 Installation & Setup

### 1. Python Environment
Install the necessary spatial and geometric processing libraries:
```bash
pip install -r requirements.txt
```

### 2. Building the C++ Engine
The core geometric logic is offloaded to a C++ engine via `pybind11` for maximum performance.

```bash
cd engine
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

**Post-Build Step:**
Move the compiled binary (e.g., `.pyd` on Windows or `.so` on Linux) to the `python_core` directory:
```bash
# Example for Windows
copy Release\smart_city_engine*.pyd ..\..\python_core\
```

---

## 🎮 Execution Workflow

The pipeline follows a **Process -> Optimize -> Synthesize** flow.

1.  **Orchestration:** Navigate to `python_core` and run the CLI:
    ```bash
    python cli.py --size large --style futuristic --density 0.9
    ```
2.  **Synthesis:** The script will automatically trigger the C++ engine and launch Blender in a background/headless process to generate the 3D assets.
3.  **Output:** Check the `output/` directory for generated `.blend` files, `.fbx` exports, and renders.

---

## 📂 Key Modules

*   `engine/`: Source code for the pybind11 C++ geometry kernel.
*   `python_core/`: CLI, API, and the "Engine Bridge".
*   `blender_module/`: Procedural modeling scripts using Blender's `bpy` and `bmesh`.
*   `docs/`: Deep-dive architectural documentation.

