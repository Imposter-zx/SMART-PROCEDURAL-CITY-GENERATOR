import requests
import json
import os
import math

def fetch_osm_data(city_query):
    """ Fetches simple building and road data from Overpass API (Library-free) """
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Simple Overpass QL query: 500m radius around city center
    query = f"""
    [out:json];
    area[name="{city_query}"]->.a;
    (
      way["highway"](area.a);
      way["building"](area.a);
    );
    out body;
    >;
    out skel qt;
    """
    
    print(f"📡 Querying Overpass API for {city_query}...")
    response = requests.get(overpass_url, params={'data': query})
    if response.status_code != 200:
        print("❌ API Error")
        return None
        
    data = response.json()
    return data

def parse_osm_to_city(data, output_path):
    nodes = {n['id']: n for n in data.get('elements', []) if n['type'] == 'node'}
    ways = [w for w in data.get('elements', []) if w['type'] == 'way']
    
    roads_data = []
    lots_data = []
    
    # Simple projection (Mercator-ish approx in meters)
    def project(lat, lon, lat_ref, lon_ref):
        r = 6371000
        x = r * math.radians(lon - lon_ref) * math.cos(math.radians(lat_ref))
        y = r * math.radians(lat - lat_ref)
        return x, y

    if not nodes: return
    ref_node = list(nodes.values())[0]
    lat0, lon0 = ref_node['lat'], ref_node['lon']

    for way in ways:
        w_nodes = [nodes.get(nid) for nid in way.get('nodes', []) if nodes.get(nid)]
        if not w_nodes: continue
        
        tags = way.get('tags', {})
        pts = [project(n['lat'], n['lon'], lat0, lon0) for n in w_nodes]
        
        if 'highway' in tags:
            roads_data.append({
                "start": {"x": pts[0][0], "y": pts[0][1]},
                "end": {"x": pts[-1][0], "y": pts[-1][1]},
                "width": 15,
                "type": "highway" if tags['highway'] in ['primary', 'motorway'] else "local"
            })
        elif 'building' in tags:
            lots_data.append({
                "footprint": [{"x": p[0], "y": p[1]} for p in pts],
                "zone": "downtown" if tags.get('building') == 'office' else "residential"
            })

    output = {
        "roads": roads_data,
        "lots": lots_data,
        "style": "modern",
        "time": "day"
    }
    
    with open(output_path, 'w') as f:
        json.dump(output, f)
    print(f"✅ Library-free GIS data saved to {output_path}")

if __name__ == "__main__":
    import sys
    city = sys.argv[1] if len(sys.argv) > 1 else "Casablanca"
    raw = fetch_osm_data(city)
    if raw:
        out_file = os.path.join(os.path.dirname(__file__), "..", "output", "temp_geometry.json")
        parse_osm_to_city(raw, out_file)
