#include "road_generator.h"
#include <cmath>
#include <cstdlib>

RoadGenerator::RoadGenerator(const std::string& size_str, const std::string& style) : style(style) {
    if (size_str == "small") size = 1000.0f;
    else if (size_str == "medium") size = 3000.0f;
    else if (size_str == "large") size = 6000.0f;
    else size = 3000.0f;
}

void RoadGenerator::generate() {
    if (style == "grid") {
        generate_grid();
    } else if (style == "radial") {
        generate_radial();
    } else if (style == "organic") {
        generate_organic();
    } else {
        generate_grid();
    }
}

void RoadGenerator::generate_grid() {
    float step = 200.0f;
    // Generate vertical roads
    for (float x = -size/2; x <= size/2; x += step) {
        roads.push_back({{x, -size/2}, {x, size/2}, 10.0f, "main"});
    }
    // Generate horizontal roads
    for (float y = -size/2; y <= size/2; y += step) {
        roads.push_back({{-size/2, y}, {size/2, y}, 10.0f, "main"});
    }
    
    // Simplistic block generation based on intersections
    for (float x = -size/2; x < size/2; x += step) {
        for (float y = -size/2; y < size/2; y += step) {
            std::vector<Point> block = {
                {x, y}, {x + step, y}, {x + step, y + step}, {x, y + step}
            };
            blocks.push_back(block);
        }
    }
}

void RoadGenerator::generate_radial() {
    // Initial algorithm for radial logic
    int num_spokes = 8;
    int num_rings = 5;
    float ring_spacing = size / (2.0f * num_rings);
    
    for (int i = 0; i < num_spokes; ++i) {
        float angle = (i * 2.0f * M_PI) / num_spokes;
        float x = (size/2) * std::cos(angle);
        float y = (size/2) * std::sin(angle);
        roads.push_back({{0, 0}, {x, y}, 12.0f, "main"});
    }
    // Basic ring roads (approximated as line segments)
    // To be implemented fully...
}

void RoadGenerator::generate_organic() {
    // Random walk or L-System based growth
    // To be implemented...
}

std::vector<Road> RoadGenerator::get_roads() const { return roads; }
std::vector<std::vector<Point>> RoadGenerator::get_blocks() const { return blocks; }
