import math
import requests
import random
import uuid
from dotenv import load_dotenv

load_dotenv()
google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
class Game:
    class Player:
        def __init__(self, name):
            self.name = name
            self.id = str(uuid.uuid4())
            self.role = ""
            self.points = 0
        
        def to_dict(self):
            """Convert Player object to dictionary for JSON serialization"""
            return {
                "id": self.id,
                "name": self.name,
                "role": self.role,
                "points": self.points
            }
            
    class Progress:
        def __init__(self, points, seekers, hiders):
            self.curr_points = points
            self.seekers_cards = seekers
            self.hiders_cards = hiders
            
    class Location:
        def __init__(self, lat, lon):
                self.lat = lat
                self.lon = lon
                self.country = ""
                self.city = ""
                self.address = ""
                self.admin_1 = ""
                self.admin_2 = ""
                self.admin_3 = ""
                self.admin_4 = ""
                self.neighborhood = ""
                self.postal_code = ""
                self.natural_feature = ""
                self.park = ""
                self.point_of_interest = ""
                self.airport = ""
                
    def __init__(self, name="gamename1"):
        self.name = name
        self.passcode = random.randint(1000, 9999)
        self.id = str(uuid.uuid4())
        self.players = {}
        self.coords = []
        self.location = None
        self.points = 0
        self.progress_list = []
        self.tolerance = 80.4672
        self.hidden = False
        
    def add_player(self, player):
        self.players.append(player)
        
    def add_players(self, players):
        self.players.extend(players)
        
    def store_coords(self, lat, lon):
        link = "https://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&key={}".format(lat, lon, google_maps_key)
        result = requests.get(link)
        data = result.json()
        
        if not data.get('results') or len(data['results']) == 0:
            return "Could not fetch location data"
        
        # Create Location object
        location = self.Location(lat, lon)
        
        # Pick the first result (most accurate)
        if data.get('results') and len(data['results']) > 0:
            first_result = data['results'][0]
            
            # Set formatted address
            location.address = first_result.get('formatted_address', '')
            
            # Parse address components
            for component in first_result.get('address_components', []):
                types = component.get('types', [])
                long_name = component.get('long_name', '')
                
                if 'country' in types:
                    location.country = long_name
                    print("Country:", long_name)
                elif 'locality' in types:
                    location.city = long_name
                    print("City:", long_name)
                elif 'administrative_area_level_1' in types:
                    location.admin_1 = long_name
                    print("Admin 1:", long_name)
                elif 'administrative_area_level_2' in types:
                    location.admin_2 = long_name
                    print("Admin 2:", long_name)
                elif 'administrative_area_level_3' in types:
                    location.admin_3 = long_name
                    print("Admin 3:", long_name)
                elif 'administrative_area_level_4' in types:
                    location.admin_4 = long_name
                    print("Admin 4:", long_name)
                elif 'neighborhood' in types:
                    location.neighborhood = long_name
                    print("Neighborhood:", long_name)
                elif 'postal_code' in types:
                    location.postal_code = long_name
                    print("Postal Code:", long_name)
                elif 'natural_feature' in types:
                    location.natural_feature = long_name
                    print("Natural Feature:", long_name)
                elif 'park' in types:
                    location.park = long_name
                    print("Park:", long_name)
                elif 'point_of_interest' in types:
                    location.point_of_interest = long_name
                    print("Point of Interest:", long_name)
                elif 'airport' in types:
                    location.airport = long_name
                    print("Airport:", long_name)
        
        # Store location object
        self.location = location
        self.coords = [lat, lon]
        
    def compare_coords(self, lat, lon):
        hide_lat = self.coords[0]
        hide_lon = self.coords[1]
        rad = 6371
        dlat = math.radians(lat - hide_lat)
        dlon = math.radians(lon - hide_lon)
        a = (math.sin(dlat / 2) ** 2 + math.cos(math.radians(hide_lat)) *
             math.cos(math.radians(lat)) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = rad * c
        return distance
    
    def get_direction(self, lat, lon):
        """Calculate bearing (compass direction) from guess location to hidden location"""
        hide_lat_rad = math.radians(self.coords[0])
        hide_lon_rad = math.radians(self.coords[1])
        guess_lat_rad = math.radians(lat)
        guess_lon_rad = math.radians(lon)
        
        dlon = hide_lon_rad - guess_lon_rad
        
        y = math.sin(dlon) * math.cos(hide_lat_rad)
        x = (math.cos(guess_lat_rad) * math.sin(hide_lat_rad) -
             math.sin(guess_lat_rad) * math.cos(hide_lat_rad) * math.cos(dlon))
        
        bearing = math.atan2(y, x)
        bearing = math.degrees(bearing)
        direction = (bearing + 360) % 360
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        idx = round(direction / 45) % 8
        return directions[idx]
        
    
    def found_hider(self, distance):
        if distance <= self.tolerance:
            return True
        return False
    
    
        