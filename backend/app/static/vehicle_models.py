import os

# =============================================================================
# STATIC PATH SETUP
# =============================================================================


VEHICLE_IMAGES_DIR = os.path.join( "Vehicle_Images")
TEST_PROGRAMS_DIR = os.path.join("Test_Programs")


# =============================================================================
# CATEGORY NORMALIZATION
# =============================================================================

ALLOWED_CATEGORIES = ["MOTOR CYCLE", "Scooter", "3-Wheeler"]

CATEGORY_MAP = {
    "MOTOR CYCLE": ["motorcycle", "motor cycle", "bike", "mc", "motor  cycle"],
    "Scooter": ["scooter", "scooters", "ev", "electric scooter", "electric", "e-scooter"],
    "3-Wheeler": ["3-wheeler", "3 wheeler", "three wheeler", "3w"],
}

def normalize_category(raw):
    if not raw:
        return "MOTOR CYCLE"

    cleaned = raw.strip().lower()

    for category, synonyms in CATEGORY_MAP.items():
        for s in synonyms:
            if cleaned == s.lower():
                return category

    if "3" in cleaned:
        return "3-Wheeler"
    if "scoot" in cleaned or "ev" in cleaned:
        return "Scooter"

    return "MOTOR CYCLE"


# =============================================================================
# VEHICLE MASTER DATA
# =============================================================================

VEHICLES = {

    # ---------------- MOTORCYCLES ----------------

    "TVS_APACHE_160_4V_ABS": {
        "name": "TVS Apache 160 4V ABS",
        "category": normalize_category("MOTOR CYCLE"),
        "description": "Dual Channel - 4V - EMS - ABS (Cont)",
        "vin_pattern": r"MD637CE5XXXXXXXXX",
        "image": "TVS_Apache_160_4V_ABS.png",
        "test_folder": "TVS_Apache_160_4V_ABS",
    },

    "TVS_APACHE_RR_310": {
        "name": "TVS Apache RR 310",
        "category": normalize_category("MOTOR CYCLE"),
        "description": "Apache - EMS, ABS (BOSCH)",
        "vin_pattern": r"MD634CE4XXXXXXXXXX",
        "image": "TVS_Apache_RR_310.png",
        "test_folder": "TVS_Apache_RR_310",
    },

    "TVS_APACHE_RTR_160_2V": {
        "name": "TVS Apache RTR 160 2V",
        "category": normalize_category("MOTOR CYCLE"),
        "description": "Single CH - 2V - EMS, ABS (BOSCH)",
        "vin_pattern": r"MD634CE4XXXXXXXXXX",
        "image": "TVS_Apache_RTR_160_2V.png",
        "test_folder": "TVS_Apache_RTR_160_2V",
    },

    "TVS_APACHE_RTR_180_2V": {
        "name": "TVS Apache RTR 180 2V RM",
        "category": normalize_category("MOTOR CYCLE"),
        "description": "RM - EMS, ABS (BOSCH)",
        "vin_pattern": r"MD634CE4XXXXXXXXX",
        "image": "TVS_Apache_RTR_180_2V.png",
        "test_folder": "TVS_Apache_RTR_180_2V",
    },

    "TVS_APACHE_RTR_200_4V": {
        "name": "TVS Apache RTR 200 4V",
        "category": normalize_category("MOTOR CYCLE"),
        "description": "EMS",
        "vin_pattern": r"MD637XXXXXXXXXXXX",
        "image": "TVS_Apache_RTR_200_4V.png",
        "test_folder": "TVS_Apache_RTR_200_4V",
    },

    "TVS_APACHE_RTX_310": {
        "name": "TVS Apache RTX 310",
        "category": normalize_category("MOTOR CYCLE"),
        "description": "MS, ABS, ICU (VISTEON)",
        "vin_pattern": r"MD637BT1XXXXXXXXX",
        "image": "TVS_Apache_RTX.png",
        "test_folder": "TVS_Apache_RTX",
    },

    "TVS_RAIDER_125": {
        "name": "TVS Raider 125",
        "category": normalize_category("MOTOR CYCLE"),
        "description": "EMS, ICU",
        "vin_pattern": r"MD625CK2XXXXXXXXX",
        "image": "TVS_Raider_125.png",
        "test_folder": "TVS_Raider_125",
    },

    "TVS_RAIDER_IGO": {
        "name": "TVS Raider IGO",
        "category": normalize_category("MOTOR CYCLE"),
        "description": "EMS, SEDAMAC",
        "vin_pattern": r"MD625CK2XXXXXXXXX",
        "image": "TVS_Raider_IGO.png",
        "test_folder": "TVS_Raider_IGO",
    },

    "TVS_RONIN": {
        "name": "TVS Ronin",
        "category": normalize_category("MOTOR CYCLE"),
        "description": "EMS, ABS, ICU, ISG",
        "vin_pattern": r"MD637CE5XXXXXXXXX",
        "image": "TVS_Ronin.png",
        "test_folder": "TVS_Ronin",
    },

    "TVS_RADEON": {
        "name": "TVS Radeon",
        "category": normalize_category("MOTOR CYCLE"),
        "description": "EMS",
        "vin_pattern": r"MD625CKXXXXXXXXXX",
        "image": "TVS_Radeon.png",
        "test_folder": "TVS_Radeon",
    },

    "TVS_SPORT": {
        "name": "TVS Sport",
        "category": normalize_category("MOTOR CYCLE"),
        "description": "EMS",
        "vin_pattern": r"MD625CK2XXXXXXXXXX",
        "image": "TVS_Sport.png",
        "test_folder": "TVS_Sport",
    },

    "TVS_SPORT_KICK_START": {
        "name": "TVS Sport Kick Start",
        "category": normalize_category("MOTOR CYCLE"),
        "description": "EMS - KEIHIN",
        "vin_pattern": r"MD625CK2XXXXXXXXXX",
        "image": "TVS_Sport_Kick_Start.png",
        "test_folder": "TVS_Sport_Kick_Start",
    },

    "TVS_STAR_CITY_PLUS": {
        "name": "TVS Star City Plus",
        "category": normalize_category("MOTOR CYCLE"),
        "description": "EMS",
        "vin_pattern": r"MD625AK2XXXXXXXXXX",
        "image": "TVS_Star_City_Plus.png",
        "test_folder": "TVS_Star_City_Plus",
    },

    "TVS_XL_100": {
        "name": "TVS XL 100",
        "category": normalize_category("MOTOR CYCLE"),
        "description": "EMS",
        "vin_pattern": r"MD637BT1XXXXXXXXXX",
        "image": "TVS_XL_100.png",
        "test_folder": "TVS_XL_100",
    },

    "TVS_XL_100_HD": {
        "name": "TVS XL 100 HD",
        "category": normalize_category("MOTOR CYCLE"),
        "description": "EMS",
        "vin_pattern": r"MD637BT1XXXXXXXXXX",
        "image": "TVS_XL_100_HD.png",
        "test_folder": "TVS_XL_100_HD",
    },

    # ---------------- SCOOTERS ----------------

    "TVS_JUPITER_OLD": {
        "name": "TVS Jupiter Old",
        "category": normalize_category("Scooter"),
        "description": "EMS - CONTINENTAL",
        "vin_pattern": r"MD637BT1XXXXXXXXXX",
        "image": "TVS_Jupiter_Old.png",
        "test_folder": "TVS_Jupiter_Old",
    },

    "TVS_JUPITER_NEW": {
        "name": "TVS Jupiter New",
        "category": normalize_category("Scooter"),
        "description": "EMS, ISG & ICU",
        "vin_pattern": r"MD637BT1XXXXXXXXXX",
        "image": "TVS_Jupiter_New.png",
        "test_folder": "TVS_Jupiter_New",
    },

    "TVS_NTORQ_125": {
        "name": "TVS Ntorq 125",
        "category": normalize_category("Scooter"),
        "description": "EMS",
        "vin_pattern": r"MD637XXXXXXXXXXXX",
        "image": "TVS_Ntorq_125.png",
        "test_folder": "TVS_Ntorq_125",
    },

    "TVS_NTORQ_150": {
        "name": "TVS Ntorq 150",
        "category": normalize_category("Scooter"),
        "description": "EMS",
        "vin_pattern": r"MD637XXXXXXXXXXXX",
        "image": "TVS_Ntorq_150.png",
        "test_folder": "TVS_Ntorq_150",
    },

    "TVS_SCOOTY_PEP_PLUS": {
        "name": "TVS Scooty Pep Plus",
        "category": normalize_category("Scooter"),
        "description": "EMS",
        "vin_pattern": r"MD637XXXXXXXXXXXX",
        "image": "TVS_Scooty_Pep_Plus.png",
        "test_folder": "TVS_Scooty_Pep_Plus",
    },

    "TVS_IQUBE_S": {
        "name": "TVS iQube S",
        "category": normalize_category("Scooter"),
        "description": "EMS",
        "vin_pattern": r"MD62912XXXXXXXXXX",
        "image": "TVS_iQube_S.png",
        "test_folder": "TVS_iQube_S",
    },

    "TVS_IQUBE_ST": {
        "name": "TVS iQube ST",
        "category": normalize_category("Scooter"),
        "description": "Premium electric scooter with smart connectivity",
        "vin_pattern": r"MD6EVNICXXXXXXXXXX",
        "image": "TVS_iQube_ST.png",
        "test_folder": "TVS_iQube_ST",
    },

    "TVS_ZEST": {
        "name": "TVS Zest",
        "category": normalize_category("Scooter"),
        "description": "EMS",
        "vin_pattern": r"MD637XXXXXXXXXXXX",
        "image": "TVS_Zest.png",
        "test_folder": "TVS_Zest",
    },

    # ---------------- 3-WHEELERS ----------------

    "TVS_KING_GS_PLUS": {
        "name": "TVS KING GS+",
        "category": normalize_category("3-Wheeler"),
        "description": "Passenger - AC Petrol",
        "vin_pattern": r"MD6M14PFXXXXXXXXX",
        "image": "TVS_KING_GS+.png",
        "test_folder": "TVS_KING_GS+",
    },

    "TVS_KING_ZS_PLUS": {
        "name": "TVS KING ZS+",
        "category": normalize_category("3-Wheeler"),
        "description": "Passenger - AC CNG",
        "vin_pattern": r"MD6M14CFXXXXXXXXX",
        "image": "TVS_KING_ZS+.png",
        "test_folder": "TVS_KING_ZS+",
    },

    "TVS_KING_LS_PLUS": {
        "name": "TVS KING LS+",
        "category": normalize_category("3-Wheeler"),
        "description": "Passenger - AC LPG",
        "vin_pattern": r"MD6M14LFXXXXXXXXX",
        "image": "TVS_KING_LS+.png",
        "test_folder": "TVS_KING_LS+",
    },

    "TVS_KING_GD": {
        "name": "TVS KING GD",
        "category": normalize_category("3-Wheeler"),
        "description": "Passenger - LC Petrol",
        "vin_pattern": r"MD6M1LPFXXXXXXXXX",
        "image": "TVS_KING_GD.png",
        "test_folder": "TVS_KING_GD",
    },

    "TVS_KING_ZD": {
        "name": "TVS KING ZD",
        "category": normalize_category("3-Wheeler"),
        "description": "Passenger - LC CNG",
        "vin_pattern": r"MD6M1LCFXXXXXXXXXX",
        "image": "TVS_KING_ZD.png",
        "test_folder": "TVS_KING_ZD",
    },

    "TVS_KING_ZK_PF": {
        "name": "TVS KING ZK PF",
        "category": normalize_category("3-Wheeler"),
        "description": "Cargo - PF",
        "vin_pattern": r"MD6N1LCFXXXXXXXXXX",
        "image": "TVS_KING_ZK_PF.png",
        "test_folder": "TVS_KING_ZK_PF",
    },

    "TVS_KING_ZK_LT": {
        "name": "TVS KING ZK LT",
        "category": normalize_category("3-Wheeler"),
        "description": "Cargo - LT",
        "vin_pattern": r"MD6N1LCFXXXXXXXXXX",
        "image": "TVS_KING_ZK_LT.png",
        "test_folder": "TVS_KING_ZK_LT",
    },

    "TVS_KING_E": {
        "name": "TVS KING E",
        "category": normalize_category("3-Wheeler"),
        "description": "Passenger - EV",
        "vin_pattern": r"MD6EVM1DXXXXXXXXXX",
        "image": "TVS_KING_E.png",
        "test_folder": "TVS_KING_E",
    },

    "TVS_3W_LARGE": {
        "name": "TVS 3W LARGE",
        "category": normalize_category("3-Wheeler"),
        "description": "Cargo - LC CNG",
        "vin_pattern": r"MD6N1LCGXXXXXXXXXX",
        "image": "TVS_3W_LARGE.png",
        "test_folder": "TVS_3W_LARGE",
    },

    "TVS_KING_3W_LARGE": {
        "name": "TVS KING 3W LARGE",
        "category": normalize_category("3-Wheeler"),
        "description": "Cargo - EV",
        "vin_pattern": r"MD6EVNICXXXXXXXXXX",
        "image": "TVS_KING_3W_LARGE.png",
        "test_folder": "TVS_KING_3W_LARGE",
    },
}

# NOTE:
# Insert the full VEHICLES mapping we generated earlier.
# (Not reproduced here for brevity, but you should paste the full mapping.)

# =============================================================================
# HELPERS
# =============================================================================

def get_image_url(image_filename):
    """
    Return the URL for a vehicle image:
    /static/Vehicle_Images/<image_filename>
    """
    return f"/Vehicle_Images/{image_filename}"


def get_test_program_path(folder_name):
    """
    Absolute path to Test_Programs/<folder>
    """
    return os.path.join(TEST_PROGRAMS_DIR, folder_name)


def find_vehicle_by_name(name: str):
    """Fuzzy match for vehicle names."""
    if not name:
        return None

    key = name.upper().replace(" ", "_").replace("-", "_")
    if key in VEHICLES:
        return VEHICLES[key]

    cleaned = "".join(c if c.isalnum() else "_" for c in key)
    cleaned = "_".join(filter(None, cleaned.split("_")))

    return VEHICLES.get(cleaned)
