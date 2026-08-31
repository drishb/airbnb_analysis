"""
Geospatial helpers. Pure NumPy — no geopandas, no shapely (PRD §7).

Distances are in kilometres. At LA County's scale (roughly 120 km across)
the difference between great-circle and planar distance is under 0.1%, so
point-to-segment work is done in a local equirectangular projection and
only the landmark distances use full haversine.
"""

import numpy as np

from . import config

EARTH_RADIUS_KM = 6371.0088


def haversine(lat1, lon1, lat2, lon2) -> np.ndarray:
    """
    Great-circle distance in km. Vectorised over any broadcastable inputs.
    PRD req 8.
    """
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def _to_local_xy(lat, lon, lat0):
    """
    Equirectangular projection to km, centred on lat0. Longitude degrees
    shrink by cos(latitude) as you move from the equator; this accounts for
    that so x and y are in the same units.
    """
    km_per_deg_lat = np.pi * EARTH_RADIUS_KM / 180.0
    x = np.asarray(lon, dtype=float) * km_per_deg_lat * np.cos(np.radians(lat0))
    y = np.asarray(lat, dtype=float) * km_per_deg_lat
    return x, y


def distance_to_polyline(lat, lon, polyline=None) -> np.ndarray:
    """
    Distance in km from each point to the nearest point on a polyline.
    PRD req 9.

    For every segment, the query point is projected onto the segment and the
    projection parameter is clamped to [0, 1] so it lands on the segment
    rather than its infinite extension. The minimum across segments is the
    answer. Vectorised: all points against all segments at once.
    """
    polyline = polyline or config.COASTLINE
    verts = np.asarray(polyline, dtype=float)
    lat0 = verts[:, 0].mean()

    px, py = _to_local_xy(lat, lon, lat0)
    px = np.atleast_1d(px)[:, None]          # (n_points, 1)
    py = np.atleast_1d(py)[:, None]

    vx, vy = _to_local_xy(verts[:, 0], verts[:, 1], lat0)
    ax, ay = vx[:-1][None, :], vy[:-1][None, :]   # (1, n_segments)
    bx, by = vx[1:][None, :], vy[1:][None, :]

    sx, sy = bx - ax, by - ay
    seg_len_sq = sx**2 + sy**2
    seg_len_sq = np.where(seg_len_sq == 0, 1e-12, seg_len_sq)   # zero-length guard

    t = ((px - ax) * sx + (py - ay) * sy) / seg_len_sq
    t = np.clip(t, 0.0, 1.0)

    cx, cy = ax + t * sx, ay + t * sy
    return np.sqrt((px - cx) ** 2 + (py - cy) ** 2).min(axis=1)


def add_distance_columns(df):
    """
    Attach distance-to-landmark and distance-to-coast columns.
    PRD req 8-9; task 1.8 decision (b) for island listings.
    """
    df = df.copy()
    for name, (lat, lon) in config.LANDMARKS.items():
        df[f"dist_{name}_km"] = haversine(df["latitude"], df["longitude"], lat, lon)

    df["dist_coast_km"] = distance_to_polyline(
        df["latitude"].to_numpy(), df["longitude"].to_numpy()
    )

    # Task 1.8 decision (b): Catalina listings are coastal, just not on this
    # coastline. Measuring them to the mainland would report ~35 km for
    # beachfront property, so they are set to zero rather than measured.
    df.loc[df["is_island"], "dist_coast_km"] = 0.0

    return df
