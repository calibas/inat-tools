# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based tool for querying the iNaturalist API to fetch observations of specific species with particular annotations. The main script (`api-query.py`) is designed to retrieve observations of Amelanchier alnifolia (Saskatoon berry) with "Fruits or Seeds" annotations in Siskiyou County, California.

## Dependencies

The script uses only Python standard library modules plus `requests`:
- `requests` - for HTTP API calls
- `requests_cache` - caching for API requests
- `pathlib` - for cross-platform path handling        
- `re` - for regex operations in filename sanitization
- `json` - for data serialization
- `csv` - for CSV output
- `time` - for rate limiting
- `datetime` - for timestamps
- `typing` - for type hints

## Running the Script

```bash
python api_query.py
```

The script will:
1. Look up taxon and place IDs via the iNaturalist API
2. Fetch all matching observations with pagination
3. Save results to timestamped CSV and JSON files in the `results/` directory

## Features (WIP)
- Coordinate-based searching - square bounding box support instead of just place_id
- Elevation data integration - two different elevation APIs
- Enhanced location processing - accurate location determination, geoprivacy handling
- Comprehensive caching - separate caches for iNat API and elevation data
- Place information lookup - extensive place database with thousands of locations

## Code Architecture

The script follows a functional approach with these key components:

- **API Lookup Functions**: 
- - `get_taxon_id()`, `get_place_id()` - resolve names to iNaturalist IDs
- - `elevation_get_request()` - USGS elevation API (with reliability issues noted)
- - `elevation_get_request_macrostrat()` - more reliable elevation API
- **Annotation Handling**: `analyze_annotations()` - iterate through observations and record annotation stats
- **Data Fetching**: 
- - `fetch_observations()` - get observations from iNaturalist API
- - `api_get_request()` - handle iNaturalist API requests
- - `elevation_get_request()` - handle nationalmap.gov API requests
- **Data Processing**: 
- - `extract_observation_data()` - transforms raw API responses into structured data
- - `get_location_data(`)` - comprehensive location data processing with elevation
- - `print_observation()` - formatted observation display
- - `fetch_place_info()` - individual place information lookup
- **Output Functions**: `save_to_csv()`, `save_to_json()` - export data in multiple formats
- **labels.py**: `get_term_label()`, `get_value_label()`, `get_place_info()` - label lookup functions

## Configuration

Key parameters are set as constants at the top of the script:
- `BASE_URL` - iNaturalist API endpoint
- `PER_PAGE` - API pagination size (200 max)
- `CACHE_DIR` - cache directory path
- `CACHE_DURATION` - cache expiration time
- `CLEAR_CACHE` - cache management flag
- `DEBUG_MODE` - enables verbose API response logging

Species and location are currently hardcoded in `main()` but can be easily modified.

## Rate Limiting

The script implements a 1-second delay between API requests via `api_get_request()` to respect iNaturalist's rate limits.