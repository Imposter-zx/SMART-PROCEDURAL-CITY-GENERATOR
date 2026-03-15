cmake_minimum_required(VERSION 3.15)
project(SmartCityEngine)

# Use C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Fetch Pybind11 (will download it automatically)
include(FetchContent)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG        v2.11.1
)
FetchContent_MakeAvailable(pybind11)

# Create the Python module
pybind11_add_module(smart_city_engine 
    src/generator.cpp 
    src/road_generator.cpp
)

# Optional: Add any extra optimizations here for the high-performance engine
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(smart_city_engine PRIVATE -O3 -march=native)
elseif(MSVC)
    target_compile_options(smart_city_engine PRIVATE /O2 /fp:fast)
endif()
