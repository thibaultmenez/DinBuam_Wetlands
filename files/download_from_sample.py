import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



import geopandas as gpd
from shapely.geometry import mapping
from pygeodes import Config, Geodes
from pygeodes.utils.datetime_utils import complete_datetime_from_str
from pygeodes.utils.profile import DownloadQueue

# --- 1) Charger shapefile AOI ---
aoi_file = "ROI_Huay_Pano_Khan_4pygeodes.shp"
gdf = gpd.read_file(aoi_file)
gdf = gdf.to_crs(epsg=4326)

# --- 2) Union des geometries [optionnel]
geom = gdf.geometry.union_all()
aoi_geojson = mapping(geom)

# --- 2) Configurer pyGeodes ---
conf = Config.from_file("config.json")  # clé API + download_dir
geodes = Geodes(conf=conf)

# --- 3) Construire la requête de recherche ---
query = {
    "dataset": {"in": ['THEIA_REFLECTANCE_SENTINEL2_L2A']},  # niveau L2A et L1C
    # Filtre date : par exemple 2025-01-01 → 2025-03-31
    "start_datetime": {"gte": complete_datetime_from_str("2021-01-01")},
    "end_datetime": {"lte": complete_datetime_from_str("2021-12-31")},
}

print("Recherche des produits Sentinel-2...")

items, df = geodes.search_items(
    query=query,
    intersects=aoi_geojson  # intersection avec la zone d’intérêt
)

print(f"{len(items)} produits trouvés")

if len(items) == 0:
    print("Aucun résultat — vérifie l’AOI ou les dates !")
    exit(0)

# --- 4) Télécharger les produits ---
if len(items) > 0:
    print("Téléchargement des produits...")
    queue = DownloadQueue(items)
    queue.run()  # démarre le téléchargement
    print("Téléchargement terminé ✔")
else:
    print("Aucun item à télécharger après filtrage 😕")

