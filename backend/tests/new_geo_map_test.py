import pytest
from unittest.mock import patch, MagicMock
import folium
from flask import current_app, Flask

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.new_geo_map import create_geo_map, save_geo_map, create_empty_map

@patch('app.services.new_geo_map.Nominatim.geocode')
def test_create_geo_map_success(mock_geocode, app):
    mock_geocode.return_value = MagicMock(latitude=51.5285582, longitude=-0.2416815)
    results = [
        {
            "file_path": "test.jpg",
            "description": "Test description",
            "address": "Test address",
            "latitude": 51.5285582,
            "longitude": -0.2416815,
            "distance_km": 1.0
        }
    ]
    map_obj = create_geo_map(results, address="Test address")
    assert isinstance(map_obj, folium.Map)

@patch('app.services.new_geo_map.Nominatim.geocode')
def test_create_geo_map_invalid_address(mock_geocode):
    mock_geocode.return_value = None
    results = [
        {
            "file_path": "test.jpg",
            "description": "Test description",
            "address": "Test address",
            "latitude": 51.5285582,
            "longitude": -0.2416815,
            "distance_km": 1.0
        }
    ]
    with pytest.raises(ValueError, match="无法找到地址: Invalid Address"):
        create_geo_map(results, address="Invalid Address")

def test_create_geo_map_no_results():
    with pytest.raises(ValueError, match="无有效的地图数据"):
        create_geo_map([])

@patch('app.services.new_geo_map.Nominatim.geocode')
def test_create_empty_map_success(mock_geocode):
    mock_geocode.return_value = MagicMock(latitude=51.5285582, longitude=-0.2416815)
    map_obj = create_empty_map(address="Test address")
    assert isinstance(map_obj, folium.Map)

@patch('app.services.new_geo_map.Nominatim.geocode')
def test_create_empty_map_invalid_address(mock_geocode):
    mock_geocode.return_value = None
    with pytest.raises(ValueError, match="无法找到地址: Invalid Address"):
        create_empty_map(address="Invalid Address")
        

@patch('app.services.new_geo_map.os.makedirs')
def test_save_geo_map(mock_makedirs, app):
    app.root_path = "/test/path"
    map_obj = MagicMock()
    filename = "test_map.html"
    
    map_path = save_geo_map(map_obj, filename)
    expected_path = os.path.join(app.root_path, "templates", filename)
    
    assert map_path == expected_path
    mock_makedirs.assert_called_with(os.path.join(app.root_path, "templates"), exist_ok=True)
    map_obj.save.assert_called_with(expected_path)
    
    
@patch('app.services.new_geo_map.Nominatim.geocode')    
def test_create_empty_map_success(mock_geocode):
    mock_geocode.return_value = MagicMock(latitude=51.5285582, longitude=-0.2416815)
    map_obj = create_empty_map(address="Test address")
    assert isinstance(map_obj, folium.Map)
    assert map_obj.location == [51.5285582, -0.2416815]

@patch('app.services.new_geo_map.Nominatim.geocode')
def test_create_empty_map_invalid_address(mock_geocode):
    mock_geocode.return_value = None
    with pytest.raises(ValueError, match="无法找到地址: Invalid Address"):
        create_empty_map(address="Invalid Address")

def test_create_empty_map_no_address():
    map_obj = create_empty_map(center_lat=51.5285582, center_lon=-0.2416815)
    assert isinstance(map_obj, folium.Map)
    assert map_obj.location == [51.5285582, -0.2416815]
