Authors: Anthony Campos, Cassandra Cinzori, and Ian Solberg

# Mapping Urban Change Through 311 Service Requests

How Boston neighborhoods changed between 2015 and 2025, read through the 311
service requests residents file for potholes, broken street lights, and missed
trash pickups. A DS4200: Information Presentation and Data Visualization
project (Northeastern University, Spring 2026) with a live interactive site.

## What it does

Analyzes over 226,000 cleaned service requests across both years, groups
neighborhoods by their "complaint signature" (the relative frequency of each
request type), and measures how far those signatures drifted between 2015 and
2025. A separate tract-level analysis cross-references complaint patterns with
U.S. Census socioeconomic data to validate the findings.

## What it found

East Boston, South Boston, and the South Boston Waterfront show the highest
signature drift, consistent with their well-documented rapid development and
demographic shifts over the decade. Seasonal patterns in core infrastructure
requests (snow plowing, potholes, street lights) stayed remarkably stable
citywide, so fundamental service demand persists even as neighborhoods change.

## Visualizations

The site includes seven figures, listed in full below:

1. Seasonal Patterns - heatmap of monthly request volumes by type, 2015 and 2025
2. Neighborhood Composition - interactive grouped bars of top request types across busiest neighborhoods
3. Signature Drift - bar chart ranking neighborhoods by complaint-profile change
4. Cluster Profiles - how neighborhoods group by similar complaint patterns, and how groups shifted
5. Interactive Neighborhood Explorer - dropdown for any neighborhood's year-over-year breakdown
6. Tract-Level Validation - D3 scatter plot of census tract poverty rates vs. complaint change
7. Geographic Map - side-by-side interactive maps (run locally via `map_app.py`)

## Start here

View the live site at https://iasolb.github.io/DS4200_GroupProject/, or run
`map_app.py` locally to explore the geographic maps.