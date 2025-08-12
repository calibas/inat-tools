#!/usr/bin/env python3
"""
iNaturalist API Query Script
Fetches observations for given species in Siskiyou County, California
"""

from typing import Any
import json
import time
from datetime import datetime
import csv
from pathlib import Path
import re

from requests_cache import CachedSession
from labels import get_term_label, get_value_label, get_place_info

SPECIES_NAME = "Amelanchier alnifolia"
PLACE_NAME = "Siskiyou County, CA"

# API Configuration
BASE_URL = "https://api.inaturalist.org/v1"
# BASE_URL_V2 = "https://api.inaturalist.org/v2"
PER_PAGE = 200  # Maximum allowed per page
DEBUG_MODE = False
CACHE_DIR = Path("./inat_cache")
CACHE_DURATION = 86400  # 24 hours in seconds
CLEAR_CACHE = False # Delete entire cache on start

def get_place_id(place_name: str) -> (int | None):
    """
    Get the place ID for a given place name
    """
    url = f"{BASE_URL}/places/autocomplete"
    params = {
        "q": place_name,
        "per_page": 10
    }

    response = api_get_request(url, params)
    if response.status_code == 200:
        data = response.json()
        for place in data.get('results', []):
            if place['display_name'].lower() == place_name.lower():
                return place['id']
            # Also check for partial matches
            if place_name.lower() in place['display_name'].lower():
                print(f"Found place: {place['display_name']} (ID: {place['id']})")
                return place['id']
        if data['results'][0]:
            return data['results'][0]['id']
    return None

def get_taxon_id(species_name: str) -> (int | None):
    """
    Get the taxon ID for a given species name
    """
    url = f"{BASE_URL}/taxa/autocomplete"
    params = {
        "q": species_name,
        "per_page": 10
    }

    response = api_get_request(url, params)
    if response.status_code == 200:
        data = response.json()
        for taxon in data.get('results', []):
            if taxon['name'].lower() == species_name.lower():
                print(f"Found taxon: {taxon['name']} (ID: {taxon['id']})")
                return taxon['id']
    return None

def fetch_place_info(place_id: int) -> None:
    """
    Fetch place information from iNaturalist API and print in dict format
    """
    url = f"{BASE_URL}/places/{place_id}"
    params = {}

    response = api_get_request(url, params)
    if response.status_code == 200:
        data = response.json()
        if data.get('results') and len(data['results']) > 0:
            result = data['results'][0]
            place_id = result['id']
            name = result['name']
            bbox_area = result['bbox_area']
            place_type = result['place_type']

            print(f'{place_id}: {{"name": "{name}", "bbox_area": {bbox_area}, "place_type": {place_type}}},')
        else:
            print(f"No results found for place ID {place_id}")
    else:
        print(f"Error fetching place info: {response.status_code}")


def fetch_observations(
    taxon_id: int,
    place_id: int,
    annotation_term_id: int | None = None,
    annotation_value_id: int | None = None,
    coordinates: list[float] | None = None):
    """
    Fetch observations with specified parameters
    """
    all_observations = []
    page = 1
    total_results = None

    while True:
        params = {
            "taxon_id": taxon_id,
            "place_id": place_id,
            "per_page": PER_PAGE,
            "page": page,
            "order_by": "observed_on",
            "order": "desc"
        }   

        # Add annotation filters only if provided
        if annotation_term_id is not None:
            params["term_id"] = annotation_term_id
        if annotation_value_id is not None:
            params["term_value_id"] = annotation_value_id
        
        
        if coordinates and len(coordinates) == 4:
            params["place_id"] = "any"
            params["nelat"] = coordinates[0]
            params["nelng"] = coordinates[1]
            params["swlat"] = coordinates[2]
            params["swlng"] = coordinates[3]

        print(f"Fetching page {page}...")
        response = api_get_request(f"{BASE_URL}/observations", params, 300)

        if response.status_code == 200:
            data = response.json()

            if total_results is None:
                total_results = data.get('total_results', 0)
                print(f"Total observations found: {total_results}")

            observations = data.get('results', [])
            if not observations:
                break

            all_observations.extend(observations)

            # Check if we've retrieved all observations
            if len(all_observations) >= total_results:
                break

            page += 1
        else:
            print(f"Error fetching data: {response.status_code}")
            break

    return all_observations

def extract_observation_data(obs: Any):
    """
    Extract relevant data from an observation
    """
    # Get coordinates
    location = obs.get('location', '').split(',') if obs.get('location') else [None, None]
    lat = location[0] if len(location) > 0 else None
    lon = location[1] if len(location) > 1 else None

    # Get annotations
    annotations = []
    for annotation in obs.get('annotations', []):
        controlled_term = annotation.get('controlled_attribute', {})
        controlled_value = annotation.get('controlled_value', {})
        annotations.append(
            f"{controlled_term.get('label', 'Unknown')}: {controlled_value.get('label', 'Unknown')}"
            )

    return {
        'id': obs.get('id'),
        'observed_on': obs.get('observed_on'),
        'created_at': obs.get('created_at'),
        'place_guess': obs.get('place_guess'),
        'latitude': lat,
        'longitude': lon,
        'positional_accuracy': obs.get('positional_accuracy'),
        'geoprivacy': obs.get('geoprivacy'),
        'taxon_name': obs.get('taxon', {}).get('name', 'Unknown'),
        'common_name': obs.get('taxon', {}).get('preferred_common_name', ''),
        'user_login': obs.get('user', {}).get('login', 'Unknown'),
        'user_name': obs.get('user', {}).get('name', ''),
        'quality_grade': obs.get('quality_grade'),
        'annotations': '; '.join(annotations),
        'description': obs.get('description', ''),
        'url': f"https://www.inaturalist.org/observations/{obs.get('id')}"
    }

def save_to_csv(observations: Any, filename: str):
    """
    Save observations to CSV file
    """
    if not observations:
        print("No observations to save.")
        return

    fieldnames = [
        'id', 'observed_on', 'created_at', 'place_guess', 
        'latitude', 'longitude', 'positional_accuracy', 'geoprivacy',
        'taxon_name', 'common_name', 'user_login', 'user_name',
        'quality_grade', 'annotations', 'description', 'url'
    ]

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for obs in observations:
            obs_data = extract_observation_data(obs)
            writer.writerow(obs_data)

    print(f"Saved {len(observations)} observations to {filename}")

def save_to_json(observations: Any, filename: str):
    """
    Save raw observations data to JSON file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(observations, f, indent=2, ensure_ascii=False)

    print(f"Saved raw data to {filename}")

def analyze_annotations(observations: Any) -> dict:
    """
    Analyze annotations across all observations
    """
    annotation_stats = {}
    observations_with_annotations = []


    for obs in observations:
        annotations = obs.get('annotations', [])
        if annotations:
            observations_with_annotations.append(obs)

        for annotation in annotations:
            controlled_term: int = annotation.get('controlled_attribute_id', {})
            controlled_value: int = annotation.get('controlled_value_id', {})

            term_label = get_term_label(controlled_term)
            value_label = get_value_label(controlled_value)

            if term_label not in annotation_stats:
                annotation_stats[term_label] = {}

            if value_label not in annotation_stats[term_label]:
                annotation_stats[term_label][value_label] = 0

            annotation_stats[term_label][value_label] += 1

    return {
        'total_observations': len(observations),
        'observations_with_annotations': observations_with_annotations,
        'annotation_percentage': (len(observations_with_annotations) / len(observations) * 100) if observations else 0,
        'annotation_breakdown': annotation_stats
    }

def get_location_data(observation: Any):
    """
    Get info about the observation's location
    """
    elevation_data = elevation_get_request_macrostrat(observation['geojson']['coordinates'][1],observation['geojson']['coordinates'][0])
    if DEBUG_MODE:
        print(f"uri: {observation['uri']}")
        # Check geoprivacy to see if location is obscured:
        print(f"geoprivacy: {observation['geoprivacy']}")
        print(f"taxon_geoprivacy: {observation['taxon_geoprivacy']}")
        # true/false tag set by user:
        print(f"obscured: {observation['obscured']}")
        # positional_accuracy, null if obscured
        print(f"positional_accuracy: {observation['positional_accuracy']}")
        # public_positional_accuracy, null or very high if obscured
        print(f"public_positional_accuracy: {observation['public_positional_accuracy']}")
        print(f"geojson: {observation['geojson']}")
        print(f"{observation['geojson']['coordinates']}")
        print(f"geojson: {observation['place_ids']}")
        print(elevation_data)
    accurate_location = True if observation['geoprivacy'] != 'obscured' and (observation['positional_accuracy'] is None or observation['positional_accuracy'] < 1000) else False
    places_info = []
    country = ""
    state = ""
    county = ""
    status = ""
    annotations = observation.get('annotations', [])
    for annotation in annotations:
        controlled_term: int = annotation.get('controlled_attribute_id', {})
        controlled_value: int = annotation.get('controlled_value_id', {})
        if controlled_term == 12:
            status = get_value_label(controlled_value)
    for place_id in observation['place_ids']:
        place_info = get_place_info(place_id)
        if place_info:
            places_info.append(place_info)
            if place_info['place_type'] == 12:
                country = place_info['name']
            if place_info['place_type'] == 8:
                state =  place_info['name']
            if place_info['place_type'] in [9, 1001]:
                county = place_info['name']
    places_info = sorted(places_info, key=lambda x: x["bbox_area"])
    location_data = {
        "id": observation['id'],
        "uri": observation['uri'],
        "taxon": observation['taxon']['name'],
        "geoprivacy": observation['geoprivacy'],
        "coordinates": observation['geojson']['coordinates'],
        "positional_accuracy": observation['positional_accuracy'],
        "observed_on_details": observation['observed_on_details'],
        "quality_grade": observation['quality_grade'],
        "elevation": elevation_data,
        "accurate_location": accurate_location,
        "status": status,
        "country": country,
        "state": state,
        "county": county,
        "places_info": places_info,
        "place_ids": observation['place_ids'],
    }
    # print(f"location_is_exact: {observation['location_is_exact']}")

    # Find elevation - USGS (US locations only?)
    # https://epqs.nationalmap.gov/v1/json?x=-123.2228195295394&y=41.97714644545383&units=Feet&output=json
    return location_data

def api_get_request(url: str, params: object, custom_duration: int = -1) -> Any:
    """
    Handle iNat API GET requests
    """
    session = CachedSession(
        cache_name=str(CACHE_DIR / 'inat_api_cache'),
        backend='sqlite',  # Uses SQLite for storage
        expire_after=CACHE_DURATION if custom_duration < 0 else custom_duration,
        allowable_codes=[200],  # Only cache successful responses
        allowable_methods=['GET'],  # Only cache GET requests
        match_headers=False,  # Don't match on headers
        ignored_parameters=['_']  # Ignore cache-busting parameters
    )
    response = session.get(url, params=params, timeout=10)
    if DEBUG_MODE:
        print(session.options)
        print(response.json())
    if hasattr(response, 'from_cache') and response.from_cache and DEBUG_MODE:
        print(f"  Using cache ({url})")
    else:
        time.sleep(1)  # Rate limiting - 1 request per second
    return response

def elevation_get_request(lat: float, lng: float) -> Any:
    """
    Handle epqs.nationalmap.gov API GET requests
    """
    # TODO: This endpoint doesn't seem to be reliable?
    # 200: Call failed.  [Failed cloud operation: Open, Path: /vsimem/_000006A3.aux.xml]
    # 200: Invalid or missing input parameters.
    # Looks like there's also sections missing 41.2969568241, -122.3092979536 gives the error:
    # 200: The operation was attempted on an empty geometry.
    session = CachedSession(
        cache_name=str(CACHE_DIR / 'elevation_api_cache'),
        backend='sqlite',  # Uses SQLite for storage
        expire_after=CACHE_DURATION,
        allowable_codes=[200],  # Only cache successful responses
        allowable_methods=['GET'],  # Only cache GET requests
        match_headers=False,  # Don't match on headers
        ignored_parameters=['_']  # Ignore cache-busting parameters
    )
    response = session.get(f"https://epqs.nationalmap.gov/v1/json?x={lng}&y={lat}&units=Feet&output=json", timeout=10)
    if DEBUG_MODE:
        print(session.options)
        print(response.json())
    if response.status_code == 200 and response.content:
        try:
            data = response.json()
            return data['value']
        except ValueError:
            print("Response received but contains invalid JSON")
            print(f"Raw response: {response.text}")
            return "Error"
    else:
        print("Invalid API reponse")
        return "Error"

def elevation_get_request_macrostrat(lat: float, lng: float) -> Any:
    """
    Handle epqs.nationalmap.gov API GET requests
    """
    # TODO: Decide which elevation endpoint.
    # This one is reliable so far, no holes found yet
    # Also contains geologic and other information about location
    # API may be slower
    # A different of ~ 100 feet compared to nationalmap.gov, more accurate?
    session = CachedSession(
        cache_name=str(CACHE_DIR / 'elevation_api_cache_macrostrat'),
        backend='sqlite',  # Uses SQLite for storage
        expire_after=CACHE_DURATION,
        allowable_codes=[200],  # Only cache successful responses
        allowable_methods=['GET'],  # Only cache GET requests
        match_headers=False,  # Don't match on headers
        ignored_parameters=['_']  # Ignore cache-busting parameters
    )
    response = session.get(f"https://macrostrat.org/api/v2/mobile/map_query_v2?lng={lng}&lat={lat}&z=7", timeout=10)
    if DEBUG_MODE:
        print(session.options)
        print(response.json())
        print(f"https://macrostrat.org/api/v2/mobile/map_query_v2?lng={lng}&lat={lat}&z=7")
    if response.status_code == 200 and response.content:
        try:
            data = response.json()
            # Convert response to int, convert to feet, round, then convert back to string
            return str(int(int(data['success']['data']['elevation']) * 3.28084))
        except ValueError:
            print("Response received but contains invalid JSON")
            print(f"Raw response: {response.text}")
            return "Error"
    else:
        print("Invalid API reponse")
        return "Error"

def print_observation(obs: Any) -> None:
    """
    Print out observation info
    """
    taxon_text = obs['taxon']
    if len(taxon_text) > 29:
        taxon_text = taxon_text[:29] + "..."
    taxon = f"{taxon_text:<32}"
    month = str(obs['observed_on_details']['month']) if obs['observed_on_details'] else ''
    day = str(obs['observed_on_details']['day']) if obs['observed_on_details'] else ''
    if month:
        date = f"{(month + '-' + day):<5}"
    else:
        date = f"{'none':<5}"
    try:
        elevation = f"{int(obs['elevation']):>6}"
    except (ValueError, TypeError):
        if obs['elevation']:
            elevation = f"{obs['elevation']:>6}"
        else:
            elevation = f"{'????':>6}"
    status = f"{obs['status']:<21}"
    place_text = obs['places_info'][0]['name'] if obs['places_info'][0] else ''
    if len(place_text) > 27:
        place_text = place_text[:27] + "..."
    place = f"{place_text:<30}"
    uri = obs['uri']
    obscured = "(obscured)" if obs['geoprivacy'] else ''

    print(f"{taxon} {date} {elevation}  {status} {place} {uri} {obscured}")

def main() -> None:
    """
    Main function to execute the query
    """
    print("iNaturalist API Query Script")
    print("=" * 50)

    # Configuration
    species_name = SPECIES_NAME
    place_name = PLACE_NAME

    session = CachedSession(
        cache_name=str(CACHE_DIR / 'inat_api_cache'),
        backend='sqlite',  # Uses SQLite for storage
    )

    if CLEAR_CACHE:
        session.cache.clear()
    else:
        # session.cache.remove_expired_responses()
        session.cache.delete(expired=True)

    # Get IDs
    print(f"\nSearching for species: {species_name}")
    taxon_id = get_taxon_id(species_name)
    if not taxon_id:
        print(f"Could not find taxon ID for {species_name}")
        return

    print(f"\nSearching for place: {place_name}")
    place_id = get_place_id(place_name)
    if not place_id:
        print(f"Could not find place ID for {place_name}")
        return


    # Fetch all observations (without annotation filtering)
    print("\nFetching all observations...")
    observations = fetch_observations(
        taxon_id=taxon_id,
        place_id=place_id,
        coordinates=[41.73613304818642,-121.10813961208953,40.32734850734382,-123.20652828396453]
    )

    if observations:
        obs_rg_accurate = []
        obs_other = []
        
        all_place_ids = set()
        places_missing_info = set()
        
        # Analyze annotations
        print("\nAnalyzing annotations...")
        annotation_analysis = analyze_annotations(observations)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        species_name_safe = re.sub(r'[^\w\s-]', '', species_name.lower())
        species_name_safe = re.sub(r'[-\s]+', '-', species_name_safe).strip('-_')
        csv_filename = f"results/{species_name_safe}_all_{timestamp}.csv"
        json_filename = f"results/{species_name_safe}_all_{timestamp}.json"

        # Save data
        save_to_csv(observations, csv_filename)
        save_to_json(observations, json_filename)

        # Print summary
        print("\nSummary:")
        print(f"Total observations retrieved: {len(observations)}")
        print(f"Observations with annotations: {len(annotation_analysis['observations_with_annotations'])} ({annotation_analysis['annotation_percentage']:.1f}%)")
        print(f"Date range: {observations[-1].get('observed_on')} to {observations[0].get('observed_on')}")

        # Quality grade breakdown
        quality_grades = {}
        for obs in observations:
            grade = obs.get('quality_grade', 'unknown')
            quality_grades[grade] = quality_grades.get(grade, 0) + 1
            location_info = get_location_data(obs)
            # all_place_ids = list(set(all_place_ids) | set(location_info['place_ids']))
            all_place_ids |= set(location_info['place_ids'])
            if location_info['quality_grade'] == 'research' and location_info['accurate_location']:
                obs_rg_accurate.append(location_info)
            else:
                obs_other.append(location_info)

        obs_rg_accurate.sort(key=lambda x: x['observed_on_details']['day'] if x['observed_on_details'] else 99)
        obs_rg_accurate.sort(key=lambda x: x['observed_on_details']['month'] if x['observed_on_details'] else 99)
        obs_other.sort(key=lambda x: x['observed_on_details']['day'] if x['observed_on_details'] else 99)
        obs_other.sort(key=lambda x: x['observed_on_details']['month'] if x['observed_on_details'] else 99)
        print("\nQuality grades:")
        for grade, count in quality_grades.items():
            print(f"  {grade}: {count}")

        # Annotation breakdown
        print("\nAnnotation breakdown:")
        for term, values in annotation_analysis['annotation_breakdown'].items():
            print(f"  {term}:")
            for value, count in values.items():
                print(f"    {value}: {count}")
        # for obs in annotation_analysis['observations_with_annotations']:
        #     get_location_data(obs)
        print("\nAccurate locations & Research Grade:")
        for obs in obs_rg_accurate:
            print_observation(obs)
            # taxon = f"{obs['taxon']:<30}"
            # date = f"{obs['observed_on_details']['month']:>2}-{obs['observed_on_details']['day']:>2}"
            # elevation = f"{int(obs['elevation']):>6}"
            # status = f"{obs['status']:<15}"
            # place = f"{obs['places_info'][0]['name'] if obs['places_info'][0] else '':<25}"
            # uri = obs['uri']

            # print(f"{taxon} {date} {elevation} {status} {place} {uri}")
            # print(f"{obs['taxon']} {obs['observed_on_details']['month']}-{obs['observed_on_details']['day']} {int(obs['elevation'])} {obs['status']} {obs['places_info'][0]['name'] if obs['places_info'][0] else ''} {obs['uri']}")
        print("\nOther observations:")
        for obs in obs_other:
            print_observation(obs)
            # print(f"{obs['taxon']} {obs['observed_on_details']['month']}-{obs['observed_on_details']['day']} {int(obs['elevation'])} {obs['status']} {obs['places_info'][0]['name'] if obs['places_info'][0] else ''} {obs['uri']}")
        # all_place_ids.sort()
        for place_id in sorted([pid for pid in all_place_ids if pid is not None]):
            if get_place_info(place_id)["name"].startswith("Not found") and place_id not in places_missing_info:
                fetch_place_info(place_id)
                places_missing_info.add(place_id)
    else:
        print("\nNo observations found matching the criteria.")

    # for place_id in [179168,203162]:
    #     fetch_place_info(place_id)

    # all_place_ids.sort()
    # print(all_place_ids)

if __name__ == "__main__":
    main()
