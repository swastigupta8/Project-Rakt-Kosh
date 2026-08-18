from django.conf import settings
from geopy.distance import geodesic
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim


def geocode(location_text):
    """Resolve free-text place text to (latitude, longitude), or None if it can't be resolved."""
    if not location_text:
        return None
    geolocator = Nominatim(user_agent=settings.GEOPY_USER_AGENT, timeout=10)
    try:
        result = geolocator.geocode(location_text)
    except (GeocoderServiceError, GeocoderTimedOut):
        return None
    if result is None:
        return None
    return (result.latitude, result.longitude)


def distance_km(lat1, lon1, lat2, lon2):
    """Straight-line distance in kilometers between two lat/lng points."""
    return geodesic((lat1, lon1), (lat2, lon2)).km


def sorted_by_distance(objects, origin_lat, origin_lon):
    """Attach a `.distance_km` to each object and return them sorted nearest-first.

    Each object must already have `.latitude` / `.longitude` set.
    """
    annotated = []
    for obj in objects:
        obj.distance_km = round(distance_km(origin_lat, origin_lon, obj.latitude, obj.longitude), 1)
        annotated.append(obj)
    annotated.sort(key=lambda obj: obj.distance_km)
    return annotated
