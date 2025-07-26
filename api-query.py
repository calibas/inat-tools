#!/usr/bin/env python3
"""
iNaturalist API Query Script
Fetches observations for Amelanchier alnifolia with "Fruits or Seeds" annotation
in Siskiyou County, California
"""

from typing import Any
import requests
import json
import time
from datetime import datetime
import csv

# API Configuration
BASE_URL = "https://api.inaturalist.org/v1"
PER_PAGE = 200  # Maximum allowed per page
DEBUG_MODE = False

def get_place_id(place_name):
    """
    Get the place ID for a given place name
    """
    url = f"{BASE_URL}/places/autocomplete"
    params = {
        "q": place_name,
        "per_page": 10
    }
    
    # response = requests.get(url, params=params, timeout=10)
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

    # response = requests.get(url, params=params, timeout=10)
    response = api_get_request(url, params)
    if response.status_code == 200:
        data = response.json()
        for taxon in data.get('results', []):
            if taxon['name'].lower() == species_name.lower():
                print(f"Found taxon: {taxon['name']} (ID: {taxon['id']})")
                return taxon['id']
    return None

def get_annotation_values():
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
    annotation_term_id: int,
    annotation_value_id: int):
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
            "term_id": annotation_term_id,
            "term_value_id": annotation_value_id,
            "per_page": PER_PAGE,
            "page": page,
            "order_by": "observed_on",
            "order": "desc"
        }

        print(f"Fetching page {page}...")
        # response = requests.get(f"{BASE_URL}/observations", params=params, timeout=10)
        response = api_get_request(f"{BASE_URL}/observations", params)

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

def extract_observation_data(obs):
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
        annotations.append(f"{controlled_term.get('label', 'Unknown')}: {controlled_value.get('label', 'Unknown')}")
    
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

def save_to_csv(observations, filename):
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

def save_to_json(observations, filename):
    """
    Save raw observations data to JSON file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(observations, f, indent=2, ensure_ascii=False)

    print(f"Saved raw data to {filename}")

def api_get_request(url: str, params: object) -> Any:
    """
    Handle iNat API GET requests
    """
    response = requests.get(url, params=params, timeout=10)
    time.sleep(1)  # Rate limiting - 1 request per second
    return response

def main():
    """
    Main function to execute the query
    """
    print("iNaturalist API Query Script")
    print("=" * 50)
    
    # Configuration
    species_name = "Amelanchier alnifolia"
    place_name = "Siskiyou County, CA"
    
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
    print("\nSetting up annotation filter for 'Fruits or Seeds'")
    annotation_ids = get_annotation_values()
    
    # Fetch observations
    print("\nFetching observations...")
    observations = fetch_observations(
        taxon_id=taxon_id,
        place_id=place_id,
        annotation_term_id=annotation_ids["term_id"],
        annotation_value_id=annotation_ids["term_value_id"]
    )
    
    if observations:
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"results/amelanchier_alnifolia_fruits_{timestamp}.csv"
        json_filename = f"results/amelanchier_alnifolia_fruits_{timestamp}.json"
        
        # Save data
        save_to_csv(observations, csv_filename)
        save_to_json(observations, json_filename)
        
        # Print summary
        print("\nSummary:")
        print(f"Total observations retrieved: {len(observations)}")
        print(f"Date range: {observations[-1].get('observed_on')} to {observations[0].get('observed_on')}")
        
        # Quality grade breakdown
        quality_grades = {}
        for obs in observations:
            grade = obs.get('quality_grade', 'unknown')
            quality_grades[grade] = quality_grades.get(grade, 0) + 1
        
        print("\nQuality grades:")
        for grade, count in quality_grades.items():
            print(f"  {grade}: {count}")
    else:
        print("\nNo observations found matching the criteria.")

if __name__ == "__main__":
    main()