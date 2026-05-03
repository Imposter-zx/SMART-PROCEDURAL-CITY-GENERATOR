import math
import random
import os
import sys

# Ensure the current directory is in sys.path for sibling imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from city_models import CityGeometry, RoadSegment, Point2D, BuildingLot

def generate_roads_fallback(size_str, style, density):
    """ Pure Python fallback for road generation if C++ engine is not compiled """
    size_str = str(size_str)
    style = str(style)
    density = float(density)
    
    if size_str == "small": size = 1000.0
    elif size_str == "medium": size = 3000.0
    else: size = 6000.0
        
    roads = []
    lots = []
    parks = []
    
    if style == "grid" or style == "organic":
        step = 300.0
        x_coords = [x for x in range(int(-size/2), int(size/2), int(step))]
        y_coords = [y for y in range(int(-size/2), int(size/2), int(step))]
        
        # Roads
        for x in x_coords:
            roads.append(RoadSegment(start=Point2D(x=x, y=-size/2), end=Point2D(x=x, y=size/2), width=15.0, type="highway" if abs(x) < 100 else "local"))
        for y in y_coords:
            roads.append(RoadSegment(start=Point2D(x=-size/2, y=y), end=Point2D(x=size/2, y=y), width=15.0, type="highway" if abs(y) < 100 else "local"))
            
        # Lots and Districts
        for x in x_coords[:-1]:
            for y in y_coords[:-1]:
                # Zoning logic based on distance to center (simplified Downtown)
                dist = math.sqrt(x**2 + y**2)
                if dist < size * 0.2:
                    zone = "downtown"
                elif dist < size * 0.4:
                    zone = "commercial"
                else:
                    zone = "residential"
                
                if random.random() < 0.1: # 10% chance for a park
                    parks.append([
                        Point2D(x=x+10, y=y+10), Point2D(x=x+step-10, y=y+10),
                        Point2D(x=x+step-10, y=y+step-10), Point2D(x=x+10, y=y+step-10)
                    ])
                    continue

                if random.random() < density:
                    # Subdivide block into smaller lots for residential
                    if zone == "residential":
                        sub_step = step / 2
                        for sx in [x, x + sub_step]:
                            for sy in [y, y + sub_step]:
                                lots.append(BuildingLot(
                                    footprint=[
                                        Point2D(x=sx+5, y=sy+5), Point2D(x=sx+sub_step-5, y=sy+5),
                                        Point2D(x=sx+sub_step-5, y=sy+sub_step-5), Point2D(x=sx+5, y=sy+sub_step-5)
                                    ],
                                    zone=zone
                                ))
                    else:
                        lots.append(BuildingLot(
                            footprint=[
                                Point2D(x=x+10, y=y+10), Point2D(x=x+step-10, y=y+10),
                                Point2D(x=x+step-10, y=y+step-10), Point2D(x=x+10, y=y+step-10)
                            ],
                            zone=zone
                        ))
                    
    elif style == "voronoi" or style == "organic":
        # Simplified "Organic" subdivision for European looks
        # We use a jittered grid to simulate voronoi-like blocks
        step = 400.0
        points = []
        for x in range(int(-size/2), int(size/2) + 1, int(step)):
            for y in range(int(-size/2), int(size/2) + 1, int(step)):
                # Jitter points
                jx = x + random.uniform(-step*0.3, step*0.3)
                jy = y + random.uniform(-step*0.3, step*0.3)
                points.append((jx, jy))
        
        # We treat these as hubs and connect them
        # (Very simplified neighborhood logic)
        for i in range(len(points)-1):
            p1 = points[i]
            p2 = points[i+1]
            if math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) < step * 1.5:
                roads.append(RoadSegment(start=Point2D(x=p1[0], y=p1[1]), end=Point2D(x=p2[0], y=p2[1]), width=12.0, type="local"))
        
        # Create blocks from jittered rectangles
        for i in range(len(points)):
            p = points[i]
            if random.random() < density:
                dist = math.sqrt(p[0]**2 + p[1]**2)
                zone = "downtown" if dist < size*0.2 else ("residential" if dist > size*0.4 else "commercial")
                w, h = 120.0, 120.0
                lots.append(BuildingLot(
                    footprint=[
                        Point2D(x=p[0]-w/2, y=p[1]-h/2), Point2D(x=p[0]+w/2, y=p[1]-h/2),
                        Point2D(x=p[0]+w/2, y=p[1]+h/2), Point2D(x=p[0]-w/2, y=p[1]+h/2)
                    ],
                    zone=zone
                ))

    # Water / River Generation
    water_polys = []
    if style != "grid": # Grid cities might not have a river for simplicity
        river_width = 150.0
        river_points = []
        # Create a winding river from left to right
        for x in range(int(-size/2), int(size/2) + 1, 200):
            offset = math.sin(x * 0.002) * 200.0
            river_points.append((x, offset))
        
        # Create a thick polygon for the river
        poly = []
        for p in river_points:
            poly.append(Point2D(x=p[0], y=p[1] - river_width/2))
        for p in reversed(river_points):
            poly.append(Point2D(x=p[0], y=p[1] + river_width/2))
        
        water_polys.append(poly)
        
        # Remove lots that intersect with the river
        def is_in_river(pt):
            for poly in water_polys:
                # Simple bounding box check for the river winding
                for i in range(len(river_points)-1):
                    p1, p2 = river_points[i], river_points[i+1]
                    if pt.x >= p1[0] and pt.x <= p2[0]:
                        avg_y = (p1[1] + p2[1]) / 2
                        if abs(pt.y - avg_y) < river_width/2 + 20:
                            return True
            return False
            
        lots = [l for l in lots if not any(is_in_river(p) for p in l.footprint)]
        
        # Identify bridges
        for r in roads:
            if is_in_river(r.start) or is_in_river(r.end):
                r.type = "bridge"
        
        # Only remove roads that are completely submerged
        roads = [r for r in roads if not (is_in_river(r.start) and is_in_river(r.end))]

    return CityGeometry(roads=roads, lots=lots, parks=parks, water=water_polys)
