import numpy as np
from src import geo, config


def test_haversine_known_pair():
    """Santa Monica Pier to LA City Hall: 4.98 km north + 23.49 km east = 24.0 km."""
    d = geo.haversine(34.0089, -118.4973, 34.0537, -118.2428)
    assert 23.5 < float(d) < 24.5


def test_haversine_zero():
    assert float(geo.haversine(34.0, -118.0, 34.0, -118.0)) == 0.0


def test_polyline_vertex_is_zero_distance():
    lat, lon = config.COASTLINE[3]
    d = geo.distance_to_polyline([lat], [lon])
    assert float(d[0]) < 0.01


def test_polyline_inland_point_positive():
    """Downtown LA is ~20 km from the Santa Monica coast."""
    d = geo.distance_to_polyline([34.0537], [-118.2428])
    assert 10.0 < float(d[0]) < 30.0


def test_polyline_clamps_to_segment():
    """A point far north-west of Point Dume must not project past the
    polyline's end onto its infinite extension."""
    endpoint_lat, endpoint_lon = config.COASTLINE[0]
    d = geo.distance_to_polyline([endpoint_lat + 1.0], [endpoint_lon - 1.0])
    direct = geo.haversine(endpoint_lat + 1.0, endpoint_lon - 1.0,
                           endpoint_lat, endpoint_lon)
    assert abs(float(d[0]) - float(direct)) < 2.0


def test_island_coast_distance_zero():
    import pandas as pd
    df = pd.DataFrame({
        "latitude": [33.3428, 34.0537],
        "longitude": [-118.3270, -118.2428],
        "is_island": [True, False],
    })
    out = geo.add_distance_columns(df)
    assert out.loc[0, "dist_coast_km"] == 0.0
    assert out.loc[1, "dist_coast_km"] > 5.0
