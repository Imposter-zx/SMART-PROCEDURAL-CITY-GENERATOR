#ifndef ROAD_GENERATOR_H
#define ROAD_GENERATOR_H

#include <vector>
#include <string>
#include <map>

struct Point {
    float x;
    float y;
};

struct Road {
    Point start;
    Point end;
    float width;
    std::string type;
};

class RoadGenerator {
public:
    RoadGenerator(const std::string& size_str, const std::string& style);
    
    void generate();
    std::vector<Road> get_roads() const;
    std::vector<std::vector<Point>> get_blocks() const;

private:
    float size;
    std::string style;
    std::vector<Road> roads;
    std::vector<std::vector<Point>> blocks;

    void generate_grid();
    void generate_radial();
    void generate_organic();
};

#endif // ROAD_GENERATOR_H
