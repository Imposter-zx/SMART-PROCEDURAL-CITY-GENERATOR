import argparse
from city_models import CityParameters
from main import generate_city

def run_cli():
    parser = argparse.ArgumentParser(description="Smart Procedural City Generator CLI")
    
    parser.add_argument("--city_type", type=str, default="modern", 
                        choices=["modern", "medieval", "cyberpunk", "arabic", "futuristic"],
                        help="Stylistic configuration of the city.")
    
    parser.add_argument("--size", type=str, default="medium",
                        choices=["small", "medium", "large"],
                        help="Overall footprint size of the city.")
                        
    parser.add_argument("--density", type=float, default=0.7,
                        help="Building density 0.0 to 1.0")
                        
    parser.add_argument("--parks", type=int, default=5,
                        help="Number of procedural parks")
                        
    parser.add_argument("--road_style", type=str, default="grid",
                        choices=["grid", "organic", "radial", "voronoi"],
                        help="Base algorithm for road layout generation.")
    
    parser.add_argument("--time", type=str, default="day",
                        choices=["day", "night"],
                        help="Time of day for the render.")

    args = parser.parse_args()

    # Model input
    params = CityParameters(
        city_type=args.city_type,
        city_size=args.size,
        building_density=args.density,
        number_of_parks=args.parks,
        road_style=args.road_style,
        time_of_day=args.time
    )
    
    # Start generation
    generate_city(params)

if __name__ == "__main__":
    run_cli()
