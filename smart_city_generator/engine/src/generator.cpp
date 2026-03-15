#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "road_generator.h"

namespace py = pybind11;

// Pybind11 Module Definition
PYBIND11_MODULE(smart_city_engine, m) {
    m.doc() = "Smart Procedural City Generator - C++ High Performance Engine";

    // Bind Point struct
    py::class_<Point>(m, "Point")
        .def(py::init<float, float>())
        .def_readwrite("x", &Point::x)
        .def_readwrite("y", &Point::y);

    // Bind Road struct
    py::class_<Road>(m, "Road")
        .def(py::init<Point, Point, float, std::string>())
        .def_readwrite("start", &Road::start)
        .def_readwrite("end", &Road::end)
        .def_readwrite("width", &Road::width)
        .def_readwrite("type", &Road::type);

    // Bind RoadGenerator class
    py::class_<RoadGenerator>(m, "RoadGenerator")
        .def(py::init<const std::string&, const std::string&>(), py::arg("size_str"), py::arg("style"))
        .def("generate", &RoadGenerator::generate)
        .def("get_roads", &RoadGenerator::get_roads)
        .def("get_blocks", &RoadGenerator::get_blocks);

    // Provide a simplified helper function
    m.def("generate_roads", [](const std::string& size, const std::string& style, float density) {
        RoadGenerator generator(size, style);
        generator.generate();
        
        // Convert to a dictionary matching the Pydantic CityGeometry model
        py::dict result;
        
        py::list roads_list;
        for (const auto& r : generator.get_roads()) {
            py::dict road_dict;
            py::dict start_pt; start_pt["x"] = r.start.x; start_pt["y"] = r.start.y;
            py::dict end_pt; end_pt["x"] = r.end.x; end_pt["y"] = r.end.y;
            road_dict["start"] = start_pt;
            road_dict["end"] = end_pt;
            road_dict["width"] = r.width;
            road_dict["type"] = r.type;
            roads_list.append(road_dict);
        }
        
        py::list blocks_list;
        for (const auto& b : generator.get_blocks()) {
            py::list block_pts;
            for (const auto& p : b) {
                py::dict pt; pt["x"] = p.x; pt["y"] = p.y;
                block_pts.append(pt);
            }
            blocks_list.append(block_pts);
        }
        
        result["roads"] = roads_list;
        result["blocks"] = blocks_list;
        
        return result;
    }, "Helper function to generate roads and blocks directly as a Python dict",
       py::arg("size"), py::arg("style"), py::arg("density"));
}
