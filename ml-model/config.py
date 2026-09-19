from pathlib import Path


LATITUDE = 51.9167
LONGITUDE = 70.3167

TIMEZONE = "Asia/Almaty"



START_DATE = "2010-01-01"
END_DATE = "2025-12-31"




ERA5_MODEL = "era5"

ERA5_LAND_MODEL = "era5_land"




TRAIN_END_YEAR = 2021

VALIDATION_END_YEAR = 2023

TEST_START_YEAR = 2024




BASE_DIR = Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR / "models"

CACHE_DIR = BASE_DIR / ".cache"


MODEL_DIR.mkdir(
    exist_ok=True
)

CACHE_DIR.mkdir(
    exist_ok=True
)