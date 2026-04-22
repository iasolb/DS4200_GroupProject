# Mapping Urban Change Through 311 Service Requests

**Anthony Campos, Cassandra Cinzori, Ian Solberg**  
DS4200: Information Presentation and Data Visualization - Northeastern University, Spring 2026
 
[View the live site](https://iasolb.github.io/DS4200_GroupProject/)

---

## Overview

This project examines how Boston neighborhoods transformed between 2015 and 2025 through the lens of municipal 311 service request patterns. Residents file 311 requests to report non-emergency issues like potholes, broken street lights, and missed trash pickups. By analyzing how the mix of these complaints shifted over a decade, we identify which neighborhoods changed most dramatically - and what that might say about gentrification, infrastructure investment, and urban change.

We analyze over 226,000 cleaned service requests across both years, grouping neighborhoods by their "complaint signature" (the relative frequency of each request type) and measuring how much those signatures drifted between 2015 and 2025. A separate tract-level analysis cross-references complaint patterns with U.S. Census socioeconomic data to validate our findings.

## What We Found

East Boston, South Boston, and the South Boston Waterfront show the highest signature drift - consistent with their well-documented rapid development and demographic shifts over the past decade. Meanwhile, seasonal patterns in core infrastructure requests (snow plowing, potholes, street lights) remained remarkably stable citywide, suggesting that fundamental service demands persist even as neighborhood character evolves.

## Visualizations

The site includes seven figures:

1. **Seasonal Patterns** - Heatmap of monthly request volumes by type for 2015 and 2025
2. **Neighborhood Composition** - Interactive grouped bars comparing the top request types across Boston's busiest neighborhoods
3. **Signature Drift** - Bar chart ranking neighborhoods by how much their complaint profile changed
4. **Cluster Profiles** - How neighborhoods group by similar complaint patterns, and how those groups shifted
5. **Interactive Neighborhood Explorer** - Dropdown to explore any neighborhood's request breakdown year over year
6. **Tract-Level Validation** - D3 scatter plot comparing census tract poverty rates with complaint change
7. **Geographic Map** - Side-by-side interactive maps (run locally via `map_app.py`)