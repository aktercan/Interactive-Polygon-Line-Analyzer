# Interactive-Polygon-Line-Analyzer

This project is a QGIS plugin designed for interactive area selection, shapefile
analysis, and line addition based on polygon-line proximity. It integrates
seamlessly with the QGIS environment, enabling efficient geospatial analysis.

## Features

    •    Interactive Area Selection: Users can draw polygons on the map interactively to define areas of interest.
    •    Shapefile Integration: Supports loading and analyzing polygon and line shapefiles.
    •    Line Addition: Automatically adds new lines based on the proximity of polygons to existing lines.
    •    Dynamic Updates: Updates the map with newly added lines and features in real-time.

## Scientific Background

Spatial analysis is a fundamental part of geospatial applications, requiring
precise and efficient tools for feature interaction. This plugin leverages QGIS
APIs to provide an interactive framework for users to define, analyze, and modify
geospatial features dynamically. Its design ensures usability in urban planning,
network analysis, and infrastructure management.

## Requirements

To run the plugin, you need:
    •    QGIS 3.x installed.
    •    Python libraries:
        •    rtree

## Usage

    1.    Clone the repository:
        git clone git@github.com:aktercan/Interactive-Polygon-Line-Analyzer.git
        cd Interactive-Polygon-Line-Analyzer
        
    2.    Place the plugin folder in your QGIS plugin directory:
        •    Linux/macOS: ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
        •    Windows: %AppData%\QGIS\QGIS3\profiles\default\python/plugins/
    
    3.    Restart QGIS and enable the plugin from the Plugin Manager.
    
    4.    Use the toolbar icon or menu entry to activate the plugin:
        •    Load polygon and line shapefiles.
        •    Interactively select areas on the map.
        •    Add new lines based on polygon-line proximity.

## Example Output

    •    Interactive Area Selection: Draw polygons dynamically on the map.
    •    Updated Layers: New lines added based on proximity calculations.


