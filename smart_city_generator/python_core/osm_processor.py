import osmnx as ox
import geopandas as gpd
from shapely.geometry import Polygon, LineString
import json
import os
import argparse

# Force OSMNX to use a specific cache directory
ox.config(use_cache=True, log_console=True)

class OSMProcessor:
    def __init__(self, city_name, output_path):
        self.city_name = city_name
        self.output_path = output_path
        
    def download_data(self, dist=1000):
        """ Downloads road networks and building footprints from OSM """
        print(f"🌍 Fetching data for {self.city_name}...")
        
        # Download Road Network (Drive)
        try:
            G = ox.graph_from_place(self.city_name, network_type='drive', buffer_dist=dist)
            # Project to UTM for accurate meters
            G_proj = ox.project_graph(G)
            self.roads = ox.graph_to_gdfs(G_proj, nodes=False, edges=True)
        except Exception as e:
            print(f"❌ Error fetching roads: {e}")
            self.roads = None

        # Download Buildings
        try:
            self.buildings = ox.geometries_from_place(self.city_name, tags={'building': True}, buffer_dist=dist)
            self.buildings = ox.project_gdf(self.buildings)
        except Exception as e:
            print(f"❌ Error fetching buildings: {e}")
            self.buildings = None
            
        # Download Parks & Water
        try:
            self.parks = ox.geometries_from_place(self.city_name, tags={'leisure': 'park', 'landuse': 'grass'}, buffer_dist=dist)
            self.parks = ox.project_gdf(self.parks)
        except:
            self.parks = None
            
        print("✅ Data download complete.")

    def process_to_json(self):
        """ Converts GeoPandas data to our internal CityGeometry JSON """
        if self.roads is None or self.buildings is None:
            print("❌ No data to process.")
            return

        roads_data = []
        for idx, row in self.roads.iterrows():
            if isinstance(row.geometry, LineString):
                coords = list(row.geometry.coords)
                # Normalize coordinates to center of city (simplified)
                roads_data.append({
                    "start": {"x": coords[0][0], "y": coords[0][1]},
                    "end": {"x": coords[-1][0], "y": coords[-1][1]},
                    "width": 12.0 if row.get('lanes', 1) == 1 else 18.0,
                    "type": "highway" if row.get('highway') in ['primary', 'motorway'] else "local"
                })

        lots_data = []
        for idx, row in self.buildings.iterrows():
            if isinstance(row.geometry, Polygon):
                coords = [{"x": p[0], "y": p[1]} for p in row.geometry.exterior.coords]
                # Guess zone based on building type or height
                zone = "downtown" if row.get('height') and float(row.get('height')) > 30 else "residential"
                lots_data.append({
                    "footprint": coords[:-1], # Remove duplicated last point
                    "zone": zone,
                    "style_override": ""
                })

        parks_data = []
        if self.parks is not None:
            for idx, row in self.parks.iterrows():
                if isinstance(row.geometry, Polygon):
                    coords = [{"x": p[0], "y": p[1]} for p in row.geometry.exterior.coords]
                    parks_data.append(coords[:-1])

        # Centering Logic (Shift all coords so the average is 0,0)
        all_x = [r['start']['x'] for r in roads_data] + [l['footprint'][0]['x'] for l in lots_data]
        all_y = [r['start']['y'] for r in roads_data] + [l['footprint'][0]['y'] for l in lots_data]
        if all_x and all_y:
            cx, cy = sum(all_x)/len(all_x), sum(all_y)/len(all_y)
            for r in roads_data:
                r['start']['x'] -= cx; r['start']['y'] -= cy
                r['end']['x'] -= cx; r['end']['y'] -= cy
            for l in lots_data:
                for p in l['footprint']:
                    p['x'] -= cx; p['y'] -= cy
            for p_list in parks_data:
                for p in p_list:
                    p['x'] -= cx; p['y'] -= cy

        final_data = {
            "roads": roads_data,
            "lots": lots_data,
            "parks": parks_data,
            "style": "modern",
            "time": "day"
        }

        with open(self.output_path, 'w') as f:
            json.dump(final_data, f)
        print(f"📦 Advanced GIS geometry saved to {self.output_path}")

def run_gis_pipeline(city_name):
    output = os.path.join(os.path.dirname(__file__), "..", "output", "temp_geometry.json")
    processor = OSMProcessor(city_name, output)
    processor.download_data(dist=500) # 500m radius
    processor.process_to_json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", type=str, default="Casablanca", help="City name to fetch from OSM")
    args = parser.parse_args()
    run_gis_pipeline(args.city)
