"""
world_map.py – Stock Monitor Weltkarte (OpenStreetMap + Leaflet.js)
Erzeugt eine vollständige HTML-Seite mit Leaflet.js auf OSM-Basis.
Aufruf: html = generate_map_html(geo_data, lang='DE')
"""
import json
import math

# ── Kontinent-Farben ──────────────────────────────────────────────────────────
CONTINENT_COLORS = {
    'North America': '#4a9fd4',
    'South America': '#e8a838',
    'Europe':        '#6dbf8f',
    'Asia':          '#d45f5f',
    'Africa':        '#9b7fd4',
    'Oceania':       '#4ac9c9',
    'Unknown':       '#aaaaaa',
}

# ── Stadt-Koordinaten ─────────────────────────────────────────────────────────
CITY_COORDS = {
    # USA
    'San Jose': (37.339, -121.894), 'San Francisco': (37.774, -122.419),
    'San Diego': (32.716, -117.162), 'Los Angeles': (34.052, -118.244),
    'Seattle': (47.606, -122.332), 'Portland': (45.523, -122.676),
    'New York': (40.713, -74.006), 'New York City': (40.713, -74.006),
    'Chicago': (41.878, -87.630), 'Houston': (29.760, -95.370),
    'Dallas': (32.776, -96.797), 'Austin': (30.267, -97.743),
    'Denver': (39.739, -104.984), 'Phoenix': (33.448, -112.074),
    'Miami': (25.774, -80.190), 'Atlanta': (33.749, -84.388),
    'Boston': (42.360, -71.059), 'Detroit': (42.331, -83.045),
    'Minneapolis': (44.977, -93.265), 'St. Louis': (38.627, -90.197),
    'Philadelphia': (39.952, -75.165), 'Washington': (38.895, -77.037),
    'Las Vegas': (36.174, -115.137), 'Salt Lake City': (40.760, -111.891),
    'Kansas City': (39.099, -94.578), 'Charlotte': (35.227, -80.843),
    'Raleigh': (35.772, -78.638), 'Nashville': (36.174, -86.767),
    'Boise': (43.615, -116.202), 'Omaha': (41.257, -95.937),
    'Tulsa': (36.154, -95.993), 'Tampa': (27.947, -82.459),
    'Orlando': (28.538, -81.379), 'Pittsburgh': (40.441, -79.996),
    'Cincinnati': (39.103, -84.512), 'Cleveland': (41.499, -81.695),
    'Indianapolis': (39.768, -86.158), 'Columbus': (39.961, -82.999),
    'Memphis': (35.149, -90.049), 'Louisville': (38.253, -85.759),
    'Richmond': (37.541, -77.434), 'Irvine': (33.684, -117.773),
    'Sunnyvale': (37.371, -122.038), 'Santa Clara': (37.354, -121.969),
    'Fremont': (37.548, -121.989), 'Scottsdale': (33.494, -111.926),
    'Beaverton': (45.487, -122.804), 'Hillsboro': (45.523, -122.990),
    'Bellevue': (47.614, -122.192), 'Redmond': (47.674, -122.121),
    'Plano': (33.020, -96.699), 'Irving': (32.814, -96.948),
    'Round Rock': (30.508, -97.679), 'Chandler': (33.303, -111.841),
    'Tempe': (33.425, -111.940), 'Tucson': (32.222, -110.970),
    'San Antonio': (29.424, -98.494), 'Fort Worth': (32.755, -97.330),
    'Jacksonville': (30.332, -81.656), 'Sacramento': (38.582, -121.494),
    'Fresno': (36.737, -119.787), 'Bakersfield': (35.373, -119.019),
    'Aurora': (39.729, -104.832), 'Boca Raton': (26.351, -80.083),
    'Waltham': (42.377, -71.236), 'Cambridge': (42.373, -71.110),
    'Wilmington': (39.744, -75.547), 'Stamford': (41.053, -73.538),
    'Overland Park': (38.983, -94.671), 'Westlake': (32.899, -97.177),
    'Merriam': (38.985, -94.700), 'Lenexa': (38.953, -94.734),
    # Silicon Valley / Bay Area (häufige yfinance-Städte)
    'Palo Alto': (37.441, -122.143), 'Menlo Park': (37.453, -122.182),
    'Mountain View': (37.386, -122.084), 'Cupertino': (37.323, -122.032),
    'Redwood City': (37.485, -122.236), 'San Mateo': (37.563, -122.323),
    'Foster City': (37.554, -122.268), 'Burlingame': (37.584, -122.366),
    'San Bruno': (37.630, -122.411), 'Milpitas': (37.432, -121.899),
    'Campbell': (37.288, -121.950), 'Los Gatos': (37.226, -121.982),
    'Saratoga': (37.264, -122.023), 'Los Altos': (37.385, -122.114),
    'Santa Cruz': (36.974, -122.031), 'Walnut Creek': (37.906, -122.064),
    'San Ramon': (37.780, -121.978), 'Pleasanton': (37.662, -121.875),
    'Livermore': (37.682, -121.768), 'Concord': (37.978, -122.031),
    'Oakland': (37.804, -122.271), 'Berkeley': (37.872, -122.272),
    'South San Francisco': (37.654, -122.408),
    # Weitere USA (häufig in yfinance)
    'Armonk': (41.124, -73.718), 'Purchase': (41.043, -73.712),
    'White Plains': (41.034, -73.763), 'Norwalk': (41.118, -73.408),
    'Bridgeport': (41.186, -73.195), 'Hartford': (41.763, -72.685),
    'New Haven': (41.308, -72.928), 'Providence': (41.824, -71.413),
    'Newark': (40.736, -74.172), 'Jersey City': (40.718, -74.043),
    'Hoboken': (40.744, -74.032), 'Princeton': (40.357, -74.665),
    'Parsippany': (40.858, -74.425), 'Basking Ridge': (40.706, -74.548),
    'Short Hills': (40.745, -74.324), 'Florham Park': (40.778, -74.386),
    'Iselin': (40.574, -74.322), 'Bedminster': (40.685, -74.648),
    'Morristown': (40.797, -74.481), 'McLean': (38.934, -77.178),
    'Bethesda': (38.985, -77.094), 'Rockville': (39.083, -77.152),
    'Herndon': (38.970, -77.386), 'Reston': (38.960, -77.357),
    'Tysons': (38.919, -77.231), 'Alexandria': (38.805, -77.047),
    'Fairfax': (38.846, -77.306), 'Falls Church': (38.882, -77.171),
    'Deerfield': (42.171, -87.844), 'Northbrook': (42.128, -87.828),
    'Schaumburg': (42.033, -88.084), 'Naperville': (41.786, -88.148),
    'Downers Grove': (41.808, -88.011), 'Lisle': (41.796, -88.072),
    'Oak Brook': (41.840, -87.954), 'Rosemont': (41.988, -87.868),
    'Minnetonka': (44.921, -93.468), 'Eden Prairie': (44.855, -93.471),
    'Bloomington': (44.841, -93.334), 'Edina': (44.880, -93.349),
    'Wayzata': (44.975, -93.509), 'Plymouth': (45.011, -93.456),
    'Alpharetta': (34.075, -84.294), 'Marietta': (33.953, -84.550),
    'Peachtree City': (33.397, -84.596), 'Duluth': (34.002, -84.145),
    'Norcross': (33.941, -84.207),
    'Bellevue': (47.614, -122.192), 'Kirkland': (47.681, -122.209),
    'Bothell': (47.762, -122.205), 'Issaquah': (47.530, -122.036),
    'Tacoma': (47.253, -122.444), 'Olympia': (47.042, -122.893),
    'Spokane': (47.659, -117.426),
    'Henderson': (36.040, -114.982), 'North Las Vegas': (36.199, -115.117),
    'Gilbert': (33.352, -111.789), 'Glendale': (33.539, -112.186),
    'Mesa': (33.416, -111.831), 'Peoria': (33.581, -112.237),
    'Longmont': (40.167, -105.102), 'Boulder': (40.015, -105.271),
    'Colorado Springs': (38.833, -104.821), 'Fort Collins': (40.585, -105.084),
    'Broomfield': (39.921, -105.087), 'Englewood': (39.648, -104.988),
    'Greenwood Village': (39.614, -104.934),
    'Lehi': (40.392, -111.850), 'Provo': (40.234, -111.658),
    'Orem': (40.297, -111.695), 'Murray': (40.667, -111.888),
    'Midvale': (40.613, -111.900), 'South Jordan': (40.562, -111.929),
    'West Jordan': (40.605, -111.981),
    'Frisco': (33.150, -96.823), 'McKinney': (33.198, -96.640),
    'Allen': (33.103, -96.671), 'Richardson': (32.948, -96.730),
    'Addison': (32.962, -96.829), 'Carrollton': (32.954, -96.897),
    'The Woodlands': (30.158, -95.487), 'Sugar Land': (29.620, -95.635),
    'Katy': (29.786, -95.824), 'Cypress': (29.969, -95.697),
    'Pearland': (29.563, -95.286),
    'San Ramon': (37.780, -121.978), 'Walnut Creek': (37.906, -122.064),
    'Emeryville': (37.832, -122.285), 'Richmond': (37.936, -122.348),
    'Novato': (38.107, -122.570), 'San Rafael': (37.974, -122.531),
    'Petaluma': (38.232, -122.636), 'Santa Rosa': (38.440, -122.714),
    # Kanada weitere
    'Mississauga': (43.589, -79.644), 'Brampton': (43.684, -79.761),
    'Markham': (43.856, -79.337), 'Richmond Hill': (43.882, -79.440),
    'Oakville': (43.467, -79.687), 'Burlington': (43.326, -79.800),
    'Hamilton': (43.256, -79.869), 'London': (42.984, -81.244),
    'Kitchener': (43.451, -80.493), 'Quebec City': (46.814, 71.208),
    'Victoria': (48.428, -123.365), 'Kelowna': (49.888, -119.496),
    # UK weitere
    'Edinburgh': (55.953, -3.189), 'Manchester': (53.480, -2.244),
    'Birmingham': (52.480, -1.902), 'Bristol': (51.454, -2.588),
    'Leeds': (53.800, -1.549), 'Glasgow': (55.861, -4.251),
    'Liverpool': (53.408, -2.992), 'Oxford': (51.752, -1.258),
    'Cambridge': (52.205, 0.121), 'Reading': (51.455, -0.972),
    # DACH weitere
    'Zollikon': (47.344, 8.581), 'Küsnacht': (47.322, 8.584),
    'Wollerau': (47.188, 8.729), 'Pfäffikon': (47.204, 8.774),
    'Rotkreuz': (47.141, 8.427), 'Baar': (47.196, 8.528),
    'Schaffhausen': (47.695, 8.635), 'Frauenfeld': (47.558, 8.896),
    'Dübendorf': (47.397, 8.617), 'Regensdorf': (47.433, 8.466),
    'Glattbrugg': (47.432, 8.564), 'Kloten': (47.451, 8.585),
    'Luzern': (47.050, 8.309), 'Thun': (46.758, 7.629),
    'Biel': (47.137, 7.246), 'Solothurn': (47.208, 7.537),
    'Aarau': (47.391, 8.044), 'Baden': (47.473, 8.307),
    'Münchenbuchsee': (47.033, 7.456),
    'Ingolstadt': (48.764, 11.424), 'Regensburg': (49.013, 12.102),
    'Würzburg': (49.791, 9.954), 'Freiburg': (47.999, 7.842),
    'Heidelberg': (49.399, 8.673), 'Ulm': (48.402, 9.997),
    'Kiel': (54.323, 10.136), 'Rostock': (54.092, 12.100),
    'Wiesbaden': (50.082, 8.240), 'Mainz': (49.999, 8.274),
    'Saarbrücken': (49.234, 6.997), 'Kassel': (51.312, 9.480),
    'Halle': (51.498, 11.969), 'Magdeburg': (52.120, 11.628),
    'Leverkusen': (51.030, 7.000), 'Oberhausen': (51.470, 6.851),
    'Wolfsburg': (52.423, 10.787), 'Braunschweig': (52.268, 10.527),
    'Osnabrück': (52.279, 8.047), 'Münster': (51.961, 7.628),
    'Linz': (48.306, 14.286), 'Graz': (47.070, 15.440),
    'Salzburg': (47.798, 13.046), 'Innsbruck': (47.268, 11.393),
    # Frankreich weitere
    'Toulouse': (43.605, 1.444), 'Bordeaux': (44.837, -0.580),
    'Nice': (43.710, 7.262), 'Nantes': (47.218, -1.554),
    'Strasbourg': (48.573, 7.752), 'Montpellier': (43.611, 3.877),
    'Sophia Antipolis': (43.616, 7.056),
    # Benelux weitere
    'Antwerp': (51.221, 4.400), 'Ghent': (51.054, 3.717),
    'Bruges': (51.209, 3.224), 'Liège': (50.633, 5.567),
    'The Hague': (52.078, 4.288), 'Utrecht': (52.090, 5.122),
    'Delft': (52.012, 4.362), 'Groningen': (53.219, 6.567),
    'Luxembourg': (49.612, 6.132),
    # Nordics weitere
    'Gothenburg': (57.707, 11.967), 'Malmö': (55.605, 13.000),
    'Uppsala': (59.858, 17.644), 'Linköping': (58.411, 15.621),
    'Espoo': (60.205, 24.656), 'Tampere': (61.498, 23.761),
    'Bergen': (60.391, 5.324), 'Trondheim': (63.431, 10.395),
    'Aarhus': (56.163, 10.204), 'Odense': (55.396, 10.389),
    # Asien weitere
    'Yokohama': (35.443, 139.638), 'Nagoya': (35.181, 136.907),
    'Kyoto': (35.012, 135.768), 'Kobe': (34.690, 135.196),
    'Fukuoka': (33.589, 130.420), 'Sapporo': (43.062, 141.354),
    'Busan': (35.180, 129.075), 'Incheon': (37.456, 126.705),
    'Suwon': (37.264, 127.029), 'Daejeon': (36.351, 127.385),
    'Nanjing': (32.061, 118.798), 'Hangzhou': (30.274, 120.155),
    'Chengdu': (30.572, 104.066), 'Wuhan': (30.593, 114.305),
    'Tianjin': (39.125, 117.191), 'Chongqing': (29.563, 106.551),
    'Xi an': (34.341, 108.940), "Xi'an": (34.341, 108.940),
    'Suzhou': (31.299, 120.585), 'Dongguan': (23.021, 113.752),
    'Foshan': (23.022, 113.122),
    'Hsinchu': (24.803, 120.968), 'Tainan': (22.999, 120.227),
    'Taichung': (24.148, 120.674),
    'New Taipei City': (25.012, 121.465), 'Kaohsiung': (22.627, 120.302),
    'Penang': (5.414, 100.330), 'Johor Bahru': (1.492, 103.741),
    'Jakarta': (-6.211, 106.845), 'Surabaya': (-7.257, 112.752),
    'Bangalore': (12.972, 77.594), 'Hyderabad': (17.387, 78.491),
    'Chennai': (13.083, 80.270), 'Pune': (18.520, 73.857),
    'Kolkata': (22.573, 88.364), 'Ahmedabad': (23.023, 72.572),
    # Australien/NZ
    'Sydney': (-33.869, 151.209), 'Melbourne': (-37.814, 144.963),
    'Brisbane': (-27.471, 153.024), 'Perth': (-31.953, 115.857),
    'Adelaide': (-34.929, 138.601), 'Canberra': (-35.282, 149.129),
    'Auckland': (-36.850, 174.763), 'Wellington': (-41.286, 174.776),
    # Lateinamerika
    'São Paulo': (-23.549, -46.633), 'Rio de Janeiro': (-22.906, -43.173),
    'Buenos Aires': (-34.614, -58.440), 'Santiago': (-33.457, -70.648),
    'Bogotá': (-4.710, -74.073), 'Lima': (-12.043, -77.029),
    'Mexico City': (19.433, -99.133), 'Monterrey': (25.686, -100.316),
    'Guadalajara': (20.660, -103.350),
    # Naher Osten / Afrika
    'Dubai': (25.205, 55.271), 'Abu Dhabi': (24.466, 54.367),
    'Riyadh': (24.688, 46.722), 'Tel Aviv': (32.085, 34.782),
    'Johannesburg': (-26.205, 28.040), 'Cape Town': (-33.924, 18.424),
    'Cairo': (30.044, 31.236), 'Lagos': (6.524, 3.379),
    'Nairobi': (-1.286, 36.822),
    # Kanada
    'Toronto': (43.651, -79.383), 'Vancouver': (49.246, -123.116),
    'Montreal': (45.502, -73.567), 'Calgary': (51.045, -114.057),
    'Ottawa': (45.421, -75.691), 'Waterloo': (43.467, -80.524),
    'Edmonton': (53.546, -113.491),
    # Deutschland
    'Munich': (48.135, 11.582), 'Berlin': (52.520, 13.405),
    'Hamburg': (53.551, 9.994), 'Frankfurt': (50.110, 8.682),
    'Cologne': (50.938, 6.960), 'Stuttgart': (48.775, 9.182),
    'Düsseldorf': (51.227, 6.773), 'Dortmund': (51.514, 7.468),
    'Essen': (51.458, 7.012), 'Leipzig': (51.340, 12.375),
    'Bremen': (53.075, 8.808), 'Dresden': (51.050, 13.738),
    'Hannover': (52.374, 9.738), 'Nuremberg': (49.453, 11.077),
    'Augsburg': (48.370, 10.898), 'Mannheim': (49.487, 8.466),
    'Karlsruhe': (49.006, 8.404), 'Bonn': (50.733, 7.100),
    'Erlangen': (49.598, 11.004), 'Munich': (48.135, 11.582),
    # Schweiz
    'Zurich': (47.376, 8.541), 'Zug': (47.166, 8.516),
    'Geneva': (46.204, 6.143), 'Basel': (47.558, 7.585),
    'Bern': (46.948, 7.448), 'Lausanne': (46.520, 6.633),
    'Winterthur': (47.500, 8.724), 'St. Gallen': (47.424, 9.377),
    # Europa
    'Paris': (48.856, 2.352), 'London': (51.507, -0.127),
    'Amsterdam': (52.370, 4.895), 'Stockholm': (59.334, 18.063),
    'Copenhagen': (55.676, 12.568), 'Oslo': (59.913, 10.752),
    'Helsinki': (60.169, 24.938), 'Dublin': (53.331, -6.249),
    'Brussels': (50.850, 4.352), 'Vienna': (48.208, 16.373),
    'Prague': (50.075, 14.438), 'Warsaw': (52.230, 21.012),
    'Budapest': (47.497, 19.040), 'Madrid': (40.417, -3.703),
    'Barcelona': (41.385, 2.173), 'Milan': (45.464, 9.190),
    'Rome': (41.902, 12.496), 'Lisbon': (38.717, -9.139),
    'Athens': (37.983, 23.727), 'Bucharest': (44.426, 26.103),
    'Eindhoven': (51.441, 5.479), 'Rotterdam': (51.923, 4.478),
    'Lyon': (45.750, 4.847), 'Marseille': (43.296, 5.381),
    # Asien
    'Tokyo': (35.689, 139.692), 'Osaka': (34.693, 135.502),
    'Seoul': (37.566, 126.978), 'Beijing': (39.904, 116.407),
    'Shanghai': (31.230, 121.473), 'Shenzhen': (22.543, 114.058),
    'Guangzhou': (23.129, 113.264), 'Hong Kong': (22.320, 114.169),
    'Taipei': (25.047, 121.519), 'Singapore': (1.352, 103.820),
    'Kuala Lumpur': (3.140, 101.686), 'Bangkok': (13.756, 100.502),
    'Mumbai': (19.076, 72.878), 'Delhi': (28.660, 77.229),
    'New Delhi': (28.614, 77.209), 'Bangalore': (12.971, 77.594),
    'Hyderabad': (17.385, 78.486), 'Chennai': (13.083, 80.270),
    'Pune': (18.520, 73.856), 'Dubai': (25.204, 55.270),
    'Abu Dhabi': (24.453, 54.377), 'Riyadh': (24.688, 46.724),
    'Tel Aviv': (32.085, 34.781), 'Herzliya': (32.166, 34.844),
    'Istanbul': (41.015, 28.979),
    # Pazifik / Rest
    'Sydney': (-33.869, 151.209), 'Melbourne': (-37.814, 144.963),
    'Brisbane': (-27.471, 153.021), 'Perth': (-31.953, 115.857),
    'Auckland': (-36.860, 174.763),
    'São Paulo': (-23.550, -46.633), 'Buenos Aires': (-34.604, -58.381),
    'Rio de Janeiro': (-22.906, -43.173), 'Bogotá': (4.711, -74.072),
    'Santiago': (-33.453, -70.674), 'Lima': (-12.046, -77.043),
    'Mexico City': (19.433, -99.133),
    'Johannesburg': (-26.204, 28.046), 'Cape Town': (-33.925, 18.424),
    'Nairobi': (-1.292, 36.821), 'Lagos': (6.455, 3.384),
    'Cairo': (30.044, 31.235), 'Casablanca': (33.574, -7.589),
}

# ── Land-Mittelpunkte ─────────────────────────────────────────────────────────
COUNTRY_COORDS = {
    'United States': (39.50, -98.35), 'USA': (39.50, -98.35),
    'Germany': (51.17, 10.45), 'France': (46.60, 2.20),
    'United Kingdom': (54.00, -2.00), 'UK': (54.00, -2.00),
    'Japan': (36.20, 138.25), 'China': (35.86, 104.19),
    'South Korea': (35.91, 127.77), 'Taiwan': (23.70, 121.00),
    'Netherlands': (52.37, 4.90), 'Switzerland': (46.82, 8.23),
    'Sweden': (60.13, 18.64), 'Denmark': (55.68, 10.00),
    'Norway': (60.47, 8.47), 'Finland': (64.00, 26.00),
    'Ireland': (53.41, -8.24), 'Belgium': (50.50, 4.47),
    'Austria': (47.52, 14.55), 'Italy': (41.87, 12.57),
    'Spain': (40.46, -3.75), 'Portugal': (39.40, -8.22),
    'Canada': (56.13, -106.35), 'Australia': (-25.27, 133.78),
    'Singapore': (1.35, 103.82), 'India': (20.59, 78.96),
    'Israel': (31.05, 34.85), 'Brazil': (-14.24, -51.93),
    'Mexico': (23.63, -102.55), 'Argentina': (-38.42, -63.62),
    'South Africa': (-30.56, 22.94), 'Russia': (61.52, 105.32),
    'Luxembourg': (49.82, 6.13), 'New Zealand': (-40.90, 174.89),
    'United Arab Emirates': (23.42, 53.85), 'UAE': (23.42, 53.85),
    'Saudi Arabia': (23.89, 45.08), 'Hong Kong': (22.32, 114.17),
    'Turkey': (38.96, 35.24), 'Indonesia': (-0.79, 113.92),
    'Malaysia': (4.21, 108.04), 'Thailand': (15.87, 100.99),
    'Philippines': (12.88, 121.77), 'Vietnam': (14.06, 108.28),
    'Pakistan': (30.38, 69.35), 'Bangladesh': (23.68, 90.36),
    'Egypt': (26.82, 30.80), 'Nigeria': (9.08, 8.67),
    'Kenya': (-0.02, 37.91), 'Morocco': (31.79, -7.09),
    'Chile': (-35.68, -71.54), 'Colombia': (4.57, -74.30),
    'Peru': (-9.19, -75.01),
}

# ── Kontinent-Zuordnung ───────────────────────────────────────────────────────
CONTINENT = {
    'United States': 'North America', 'USA': 'North America',
    'Canada': 'North America', 'Mexico': 'North America',
    'Germany': 'Europe', 'France': 'Europe', 'United Kingdom': 'Europe',
    'UK': 'Europe', 'Netherlands': 'Europe', 'Switzerland': 'Europe',
    'Sweden': 'Europe', 'Denmark': 'Europe', 'Norway': 'Europe',
    'Finland': 'Europe', 'Ireland': 'Europe', 'Belgium': 'Europe',
    'Austria': 'Europe', 'Italy': 'Europe', 'Spain': 'Europe',
    'Portugal': 'Europe', 'Luxembourg': 'Europe', 'Turkey': 'Europe',
    'Poland': 'Europe', 'Czechia': 'Europe', 'Hungary': 'Europe',
    'Romania': 'Europe', 'Greece': 'Europe', 'Slovakia': 'Europe',
    'Croatia': 'Europe', 'Russia': 'Europe',
    'Japan': 'Asia', 'China': 'Asia', 'South Korea': 'Asia',
    'Taiwan': 'Asia', 'Singapore': 'Asia', 'India': 'Asia',
    'Israel': 'Asia', 'Hong Kong': 'Asia', 'UAE': 'Asia',
    'United Arab Emirates': 'Asia', 'Saudi Arabia': 'Asia',
    'Indonesia': 'Asia', 'Malaysia': 'Asia', 'Thailand': 'Asia',
    'Philippines': 'Asia', 'Vietnam': 'Asia', 'Pakistan': 'Asia',
    'Bangladesh': 'Asia', 'Turkey': 'Asia',
    'Australia': 'Oceania', 'New Zealand': 'Oceania',
    'Brazil': 'South America', 'Argentina': 'South America',
    'Chile': 'South America', 'Colombia': 'South America',
    'Peru': 'South America',
    'South Africa': 'Africa', 'Nigeria': 'Africa',
    'Kenya': 'Africa', 'Egypt': 'Africa', 'Morocco': 'Africa',
}


# ── Stadt+Land-Koordinaten (löst Namenskonflikte auf) ────────────────────────
# Key: (city, country) – hat Vorrang vor CITY_COORDS
CITY_COORDS_CC = {
    # Cambridge: UK vs. USA (Massachusetts)
    ('Cambridge', 'United Kingdom'): (52.205, 0.119),
    ('Cambridge', 'United States'):  (42.373, -71.110),
    # Waterloo: Kanada vs. Belgien
    ('Waterloo', 'Canada'):          (43.467, -80.524),
    ('Waterloo', 'Belgium'):         (50.715, 4.399),
    # Richmond: UK vs. USA (Virginia)
    ('Richmond', 'United Kingdom'):  (51.461, -0.306),
    ('Richmond', 'United States'):   (37.541, -77.434),
    # Wilmington: USA (Delaware) vs. UK
    ('Wilmington', 'United Kingdom'): (53.575, -2.127),
    ('Wilmington', 'United States'):  (39.744, -75.547),
    # Wellington: Neuseeland vs. Südafrika
    ('Wellington', 'New Zealand'):    (-41.286, 174.776),
    ('Wellington', 'South Africa'):   (-33.644, 19.017),
    # Hamilton: Kanada vs. Bermuda vs. Neuseeland
    ('Hamilton', 'Canada'):           (43.257, -79.869),
    ('Hamilton', 'New Zealand'):      (-37.783, 175.282),
    # Kingston: Jamaika vs. UK
    ('Kingston', 'Jamaica'):          (17.997, -76.793),
    ('Kingston', 'United Kingdom'):   (51.412, -0.300),
    # Melbourne: Australien vs. USA (Florida)
    ('Melbourne', 'Australia'):       (-37.814, 144.963),
    ('Melbourne', 'United States'):   (28.083, -80.608),
    # Portland: USA (Oregon)
    ('Portland', 'United States'):    (45.523, -122.676),
    # Frankfurt: Deutschland
    ('Frankfurt', 'Germany'):         (50.110, 8.682),
}

def _tr_continent(cont, lang='DE'):
    de = {'North America': 'Nordamerika', 'South America': 'Südamerika',
          'Europe': 'Europa', 'Asia': 'Asien',
          'Africa': 'Afrika', 'Oceania': 'Ozeanien', 'Unknown': 'Unbekannt'}
    en = {'North America': 'North America', 'South America': 'South America',
          'Europe': 'Europe', 'Asia': 'Asia',
          'Africa': 'Africa', 'Oceania': 'Oceania', 'Unknown': 'Unknown'}
    return (de if lang == 'DE' else en).get(cont, cont)


# US-Bundesstaaten als Fallback wenn Stadt nicht gefunden wird
# Koordinaten = ungefähres Bevölkerungszentrum (nicht Hauptstadt)
US_STATE_COORDS = {
    'AL': (32.806, -86.791), 'AK': (61.370, -152.404), 'AZ': (33.729, -111.431),
    'AR': (34.969, -92.373), 'CA': (36.778, -119.418), 'CO': (39.550, -105.782),
    'CT': (41.597, -72.755), 'DE': (39.318, -75.508), 'FL': (27.766, -81.686),
    'GA': (33.041, -83.643), 'HI': (21.095, -157.498), 'ID': (44.240, -114.479),
    'IL': (40.349, -88.986), 'IN': (39.849, -86.258), 'IA': (42.011, -93.210),
    'KS': (38.526, -96.727), 'KY': (37.668, -84.670), 'LA': (31.169, -91.867),
    'ME': (44.693, -69.381), 'MD': (39.063, -76.803), 'MA': (42.230, -71.530),
    'MI': (43.326, -84.536), 'MN': (45.694, -93.900), 'MS': (32.741, -89.678),
    'MO': (38.456, -92.288), 'MT': (46.921, -110.454), 'NE': (41.125, -98.268),
    'NV': (38.313, -117.055), 'NH': (43.452, -71.563), 'NJ': (40.298, -74.521),
    'NM': (34.840, -106.248), 'NY': (42.165, -74.948), 'NC': (35.630, -79.806),
    'ND': (47.528, -99.784), 'OH': (40.388, -82.764), 'OK': (35.565, -96.928),
    'OR': (44.572, -122.071), 'PA': (40.590, -77.209), 'RI': (41.680, -71.511),
    'SC': (33.856, -80.945), 'SD': (44.299, -99.438), 'TN': (35.747, -86.692),
    'TX': (31.054, -97.563), 'UT': (39.320, -111.093), 'VT': (44.045, -72.710),
    'VA': (37.769, -78.169), 'WA': (47.400, -121.490), 'WV': (38.491, -80.954),
    'WI': (44.268, -89.616), 'WY': (42.756, -107.302), 'DC': (38.895, -77.037),
    # Kanada Provinzen
    'ON': (51.253, -85.323), 'QC': (52.939, -73.549), 'BC': (53.726, -127.648),
    'AB': (55.001, -115.002), 'MB': (53.761, -98.814), 'SK': (52.939, -106.450),
    'NS': (44.682, -63.744), 'NB': (46.565, -66.461), 'NL': (53.135, -57.660),
    'PE': (46.510, -63.415),
    # Australien Bundesstaaten
    'NSW': (-31.840, 145.612), 'VIC': (-36.848, 144.281), 'QLD': (-20.918, 142.702),
    'WA': (-25.328, 122.298), 'SA': (-30.000, 136.209), 'TAS': (-41.454, 145.967),
}


def build_markers(geo_data, lang='DE'):
    coord_seen = {}
    markers = []
    for sym, info in sorted(geo_data.items(), key=lambda x: x[1]['share_pct']):
        country = info.get('country', '')
        city    = info.get('city', '')
        state   = info.get('state', '') or ''
        coords  = (CITY_COORDS_CC.get((city, country))
                   or CITY_COORDS.get(city)
                   or (US_STATE_COORDS.get(state) if country in ('United States', 'USA', 'Canada', 'Australia') else None)
                   or COUNTRY_COORDS.get(country))
        if not coords:
            continue
        # Versatz basierend auf Koordinaten (2 Dezimalstellen = ~1 km Raster)
        # Verhindert dass nahe Staedte (z.B. Santa Clara/Sunnyvale) faelschlicherweise
        # als Duplikat erkannt und ins Wasser verschoben werden.
        coord_key = f"{round(coords[0],2)}_{round(coords[1],2)}"
        idx = coord_seen.get(coord_key, 0)
        coord_seen[coord_key] = idx + 1
        if idx == 0:
            lat, lon = coords[0], coords[1]
        else:
            # Alternierend Ost/West versetzen, kleine Schritte (kein Richtung Wasser)
            step = 0.12 * ((idx + 1) // 2)
            lat = coords[0]
            lon = coords[1] + (step if idx % 2 == 1 else -step)
        share  = info['share_pct']
        cont   = CONTINENT.get(country, 'Unknown')
        color  = CONTINENT_COLORS.get(cont, '#aaaaaa')
        radius = max(8, min(50, math.sqrt(share) * 11))
        addr_parts = [p for p in [info.get('address1', ''), city,
                                   info.get('zip', ''), country] if p]
        addr_str = ', '.join(addr_parts) or country
        url = info.get('website', '') or ''
        if url and not url.startswith('http'):
            url = 'https://' + url
        no_web = 'Keine Website' if lang == 'DE' else 'No website'
        link_html = (f'<a href="{url}" target="_blank" style="color:#4a9fd4;">🌐 {url}</a>'
                     if url else f'<span style="color:#888;">{no_web}</span>')
        share_lbl = 'Anteil' if lang == 'DE' else 'Share'
        popup_html = (
            f'<b style="font-size:15px;">{sym}</b> &nbsp;'
            f'<span style="font-size:12px;color:#555;">{info["longname"]}</span><br>'
            f'<hr style="margin:6px 0;border-color:#ddd;">'
            f'<span style="font-size:12px;">📍 {addr_str}</span><br>'
            f'<span style="font-size:12px;">🌍 {_tr_continent(cont, lang)}</span><br>'
            f'<b style="font-size:13px;color:{color};">{share_lbl}: {share:.2f}%</b><br>'
            f'<div style="margin-top:6px;">{link_html}</div>'
        )
        markers.append({
            'sym': sym, 'name': info['longname'],
            'lat': lat, 'lon': lon,
            'r': radius, 'color': color,
            'share': share, 'cont': cont,
            'popup': popup_html,
        })
    return markers


def generate_map_html(geo_data, lang='DE'):
    markers = build_markers(geo_data, lang)

    # Legende
    cont_summary = {}
    for m in markers:
        cont_summary[m['cont']] = cont_summary.get(m['cont'], 0) + m['share']
    legend_items = [
        {'label': _tr_continent(c, lang),
         'color': CONTINENT_COLORS.get(c, '#aaa'),
         'pct': round(v, 1)}
        for c, v in sorted(cont_summary.items(), key=lambda x: -x[1])
    ]

    markers_json   = json.dumps(markers)
    legend_json    = json.dumps(legend_items)
    scroll_hint    = ('Scroll = Zoom  ·  Drag = Pan' if lang == 'DE'
                      else 'Scroll = Zoom  ·  Drag = Pan')
    legend_title   = 'Regionen' if lang == 'DE' else 'Regions'

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Stock Monitor – World Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ width: 100%; height: 100%; overflow: hidden; }}
  #map {{ width: 100%; height: 100%; }}
  #legend {{
    position: fixed; bottom: 30px; left: 20px; z-index: 1000;
    background: rgba(255,255,255,0.95); border: 1px solid #ccc;
    border-radius: 8px; padding: 12px 16px;
    font-family: Arial, sans-serif; font-size: 13px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15); min-width: 160px;
  }}
  .leg-title {{ font-weight: bold; margin-bottom: 6px; font-size: 13px; }}
  .leg-row {{ display: flex; align-items: center; gap: 8px; margin-top: 5px; }}
  .leg-dot  {{ width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }}
  #hint {{
    position: fixed; bottom: 30px; right: 20px; z-index: 1000;
    background: rgba(255,255,255,0.88); border: 1px solid #ccc;
    border-radius: 6px; padding: 6px 12px;
    font-family: Arial, sans-serif; font-size: 11px; color: #555;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  }}
  #cdn-warn {{
    display: none; position: fixed; top: 20px; left: 50%;
    transform: translateX(-50%); background: #c0392b; color: white;
    padding: 10px 20px; border-radius: 6px; z-index: 99999;
    font-family: Arial, sans-serif;
  }}
  /* Leaflet Popup Styling */
  .leaflet-popup-content {{ font-family: Arial, sans-serif; min-width: 200px; }}
  .leaflet-popup-content-wrapper {{ border-radius: 8px; }}
</style>
</head>
<body>
<div id="cdn-warn">⚠ Keine Internetverbindung – Karte kann nicht geladen werden.</div>
<div id="map"></div>
<div id="legend">
  <div class="leg-title">📊 {legend_title}</div>
</div>
<div id="hint">🖱 {scroll_hint}</div>

<script>
(function() {{
  if (typeof L === 'undefined') {{
    document.getElementById('cdn-warn').style.display = 'block';
    return;
  }}

  // ── Karte initialisieren ──────────────────────────────────────────────────
  var map = L.map('map', {{
    center: [20, 0],
    zoom: 3,
    minZoom: 3,
    maxZoom: 19,
    zoomControl: true,
    worldCopyJump: false
  }});

  // CartoDB Positron — noWrap verhindert Weltkarte-Wiederholung
  L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="https://carto.com/">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19,
    noWrap: true,
    bounds: [[-90, -180], [90, 180]]
  }}).addTo(map);

  // ── Marker ───────────────────────────────────────────────────────────────
  var markers = {markers_json};

  markers.forEach(function(m) {{
    var circle = L.circleMarker([m.lat, m.lon], {{
      radius: m.r,
      fillColor: m.color,
      color: 'white',
      weight: 1.5,
      opacity: 1,
      fillOpacity: 0.85
    }});

    // Tooltip (Hover)
    circle.bindTooltip(
      '<b>' + m.sym + '</b> – ' + m.name + '<br>' +
      '<b style="color:' + m.color + '">' + m.share.toFixed(2) + '%</b>',
      {{ direction: 'top', offset: [0, -m.r], className: 'stock-tooltip' }}
    );

    // Popup (Klick)
    circle.bindPopup(m.popup, {{ maxWidth: 320, className: 'stock-popup' }});

    circle.addTo(map);
  }});

  // ── Karte auf Marker zentrieren ───────────────────────────────────────────
  if (markers.length > 0) {{
    var lats = markers.map(function(m) {{ return m.lat; }});
    var lons = markers.map(function(m) {{ return m.lon; }});
    var bounds = L.latLngBounds(
      [Math.min.apply(null,lats) - 5, Math.min.apply(null,lons) - 5],
      [Math.max.apply(null,lats) + 5, Math.max.apply(null,lons) + 5]
    );
    map.fitBounds(bounds, {{ padding: [40, 40] }});
  }}

  // ── Legende ──────────────────────────────────────────────────────────────
  var legendData = {legend_json};
  var legEl = document.getElementById('legend');
  legendData.forEach(function(d) {{
    var row = document.createElement('div');
    row.className = 'leg-row';
    row.innerHTML = '<span class="leg-dot" style="background:' + d.color + '"></span>' +
                    '<span>' + d.label + ' &nbsp;<b>' + d.pct + '%</b></span>';
    legEl.appendChild(row);
  }});

}})();
</script>
</body>
</html>"""

    return html
