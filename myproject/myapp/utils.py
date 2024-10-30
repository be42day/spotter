import os
import requests
from geopy.distance import geodesic
import pandas as pd
from haversine import haversine, Unit
from django.conf import settings



def find_all_routes(city1_lat, city1_long, city2_lat, city2_long):
    """
    Finds all pathes between the tow coordinates
    """
    # input points
    start = f"{city1_long},{city1_lat}"
    end = f"{city2_long},{city2_lat}"

    # Request URL
    cities_url = f"http://router.project-osrm.org/route/v1/driving/{start};{end}?geometries=geojson&alternatives=true"

    cities_response = requests.get(cities_url)
    cities_data = cities_response.json()

    return cities_data


def find_next_city(city_coordinate_list, beginning_index,
                   cumulative_distance, target_distance_miles):
    """
    Finds the next city in a route according to target_distance_miles
    """
    next_city_idx = beginning_index
    previous_point = city_coordinate_list[beginning_index]

    # Check the cities to reach 500 miles
    for point in city_coordinate_list[beginning_index+1:]:
        
        segment_distance = geodesic(previous_point[::-1], point[::-1]).miles
        cumulative_distance += segment_distance
        
        if cumulative_distance >= target_distance_miles:
            break

        next_city_idx += 1
        previous_point = point

    return next_city_idx


def find_optimal_route(cities_data, fuel_info_path):
    """
    Finds the cheepest route according to fuel cost
    """
    # Fuel data
    df = pd.read_csv(fuel_info_path)

    target_distance_miles = 500
    mile_per_galon = 10
    car_capacity = target_distance_miles / mile_per_galon

    all_results = []

    # For each route
    for route in cities_data["routes"]:

        route_coordinates = route["geometry"]["coordinates"]

        # Waypoints list and total cost
        final_route = [["start",route_coordinates[0][::-1]]]
        total_cost = 0

        # Calculate the next city
        beginning_index = 0
        cumulative_distance = 0
        gas_station_price = 0

        # Continue to reach the destination city
        while True:

            previous_point = route_coordinates[beginning_index]
            next_city_idx = find_next_city(route_coordinates, beginning_index,
                                           cumulative_distance, target_distance_miles)

            
            next_point = route_coordinates[next_city_idx]
            distance_to_target_point = geodesic(previous_point[::-1], next_point[::-1]).miles
            

            if next_point == route_coordinates[-1]:
                final_route.append(["end", next_point[::-1]])
                fuel_residue_in_car = (target_distance_miles - distance_to_target_point) * car_capacity / target_distance_miles
                total_cost -= (gas_station_price * fuel_residue_in_car)
                all_results.append({"route_cost"  : float(total_cost),
                                    "route_points": final_route})
                break


            # print(target_point)
            final_route.append(["city_point", next_point[::-1]])

            # Get the distance of each fuel sation to the city
            df['distance_to_city'] = df.apply(lambda row: haversine(next_point[::-1], (row['latitude'], row['longitude']), unit=Unit.MILES), axis=1)

            # Find the nearest fuel station
            nearest_station = df.loc[df['distance_to_city'].idxmin()]
            final_route.append(["fuel_point", [float(nearest_station['latitude']), float(nearest_station['longitude'])]])
            distance_to_gas_station = nearest_station["distance_to_city"]
            gas_station_price = float(nearest_station["Retail Price"])

            movement = distance_to_target_point + distance_to_gas_station
            used_fuel = car_capacity * movement / target_distance_miles

            total_cost += used_fuel * gas_station_price

            # Back to the target city from the gas station
            cumulative_distance = distance_to_gas_station
            beginning_index = next_city_idx


    # Sort by the 'cost' key
    optimal_route = sorted(all_results, key=lambda x: x['route_cost'])[0]
    return optimal_route


def main(city1_lat, city1_long, city2_lat, city2_long):

    # Define the path to the CSV file
    fuel_info_path = os.path.join(settings.BASE_DIR, 'myapp', 'data', 'cleaned_fuel_data.csv')

    all_pathes    = find_all_routes(city1_lat, city1_long, city2_lat, city2_long)
    optimal_route = find_optimal_route(all_pathes, fuel_info_path)

    return optimal_route