#!/usr/bin/env python3
"""
iNaturalist API Query Script
Fetches observations for Amelanchier alnifolia with "Fruits or Seeds" annotation
in Siskiyou County, California
"""

from typing import Any
import json
import time
from datetime import datetime
import csv
from pathlib import Path
import re

from requests_cache import CachedSession

# API Configuration
BASE_URL = "https://api.inaturalist.org/v1"
PER_PAGE = 200  # Maximum allowed per page
DEBUG_MODE = False
CACHE_DIR = Path("./inat_cache")
CACHE_DURATION = 86400  # 24 hours in seconds
CLEAR_CACHE = False # Delete entire cache

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
    if DEBUG_MODE:
        print(response.json())
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

def get_annotation_values() -> Any:
    """
    Get annotation term and value IDs for "Flowers and Fruits: Fruits or Seeds"
    Common annotation IDs (these are typically stable):
    - Plant Phenology (term_id: 12)
      - Flowering (value_id: 13)
      - Fruiting (value_id: 14)
      - Flower Budding (value_id: 15)
      - No Evidence of Flowering (value_id: 16)
    """
    # For "Fruits or Seeds", we use Plant Phenology term with Fruiting value
    return {
        "term_id": 12,  # Plant Phenology
        "term_value_id": 14  # Fruiting
    }

def fetch_observations(
    taxon_id: int,
    place_id: int,
    annotation_term_id: (int | None) = None,
    annotation_value_id: (int | None) = None):
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

        print(f"Fetching page {page}...")
        response = api_get_request(f"{BASE_URL}/observations", params, 30)

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
    observations_with_annotations = 0
    
    for obs in observations:
        annotations = obs.get('annotations', [])
        if annotations:
            observations_with_annotations += 1
            
        for annotation in annotations:
            controlled_term = annotation.get('controlled_attribute', {})
            controlled_value = annotation.get('controlled_value', {})
            
            term_label = controlled_term.get('label', 'Unknown Term')
            value_label = controlled_value.get('label', 'Unknown Value')
            
            if term_label not in annotation_stats:
                annotation_stats[term_label] = {}
            
            if value_label not in annotation_stats[term_label]:
                annotation_stats[term_label][value_label] = 0
            
            annotation_stats[term_label][value_label] += 1
    
    return {
        'total_observations': len(observations),
        'observations_with_annotations': observations_with_annotations,
        'annotation_percentage': (observations_with_annotations / len(observations) * 100) if observations else 0,
        'annotation_breakdown': annotation_stats
    }

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
        print(response)
    if hasattr(response, 'from_cache') and response.from_cache:
        print(f"  Using cache ({url})")
    else:
        time.sleep(1)  # Rate limiting - 1 request per second
    return response

def main() -> None:
    """
    Main function to execute the query
    """
    print("iNaturalist API Query Script")
    print("=" * 50)

    # Configuration
    species_name = "Amelanchier alnifolia"
    place_name = "Siskiyou County, CA"

    session = CachedSession(
        cache_name=str(CACHE_DIR / 'inat_api_cache'),
        backend='sqlite',  # Uses SQLite for storage
    )
    
    if CLEAR_CACHE:
        session.cache.clear()
    else:
        session.cache.remove_expired_responses()

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

    # Get annotation IDs for "Fruits or Seeds"
    # print("\nSetting up annotation filter for 'Fruits or Seeds'")
    # annotation_ids = get_annotation_values()

    # Fetch all observations (without annotation filtering)
    print("\nFetching all observations...")
    observations = fetch_observations(
        taxon_id=taxon_id,
        place_id=place_id
    )

    if observations:
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
        print(f"Observations with annotations: {annotation_analysis['observations_with_annotations']} ({annotation_analysis['annotation_percentage']:.1f}%)")
        print(f"Date range: {observations[-1].get('observed_on')} to {observations[0].get('observed_on')}")

        # Quality grade breakdown
        quality_grades = {}
        for obs in observations:
            grade = obs.get('quality_grade', 'unknown')
            quality_grades[grade] = quality_grades.get(grade, 0) + 1

        print("\nQuality grades:")
        for grade, count in quality_grades.items():
            print(f"  {grade}: {count}")
            
        # Annotation breakdown
        print("\nAnnotation breakdown:")
        for term, values in annotation_analysis['annotation_breakdown'].items():
            print(f"  {term}:")
            for value, count in values.items():
                print(f"    {value}: {count}")
    else:
        print("\nNo observations found matching the criteria.")

if __name__ == "__main__":
    main()
