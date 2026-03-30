# nirix_desktop/models.py
"""
Created on Tue Dec  9 09:21:17 2025

@author: Sri.Sakthivel
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple
import os

from . import config as app_config


@dataclass
class User:
    user_id: int
    name: str
    emp_id: str
    email: str
    theme: str = "light"


@dataclass
class TestRowModel:
    module: str
    func: str
    requires_mac: bool = False


# Vehicle images and models (same as original final_raspberry-pi.py code)

ASSETS_FOLDER = app_config.ASSETS_FOLDER

VEHICLE_IMAGES = {
    "TVS Apache 160 4V ABS": os.path.join(ASSETS_FOLDER, "TVS_Apache_160_4V_ABS.png"),
    "TVS Apache RR 310": os.path.join(ASSETS_FOLDER, "TVS_Apache_RR_310.png"),
    "TVS Apache RTR 160 2V": os.path.join(ASSETS_FOLDER, "TVS_Apache_RTR_160_2V.png"),
    "TVS Apache RTR 180 2V RM": os.path.join(ASSETS_FOLDER, "TVS_Apache_RTR_180_2V.png"),
    "TVS Apache RTR 200 4V RM": os.path.join(ASSETS_FOLDER, "TVS_Apache_RTR_200_4V.png"),
    "TVS Apache RTX": os.path.join(ASSETS_FOLDER, "TVS_Apache_RTX.png"),
    "TVS Raider 125": os.path.join(ASSETS_FOLDER, "TVS_Raider_125.png"),
    "TVS Raider IGO": os.path.join(ASSETS_FOLDER, "TVS_Raider_IGO.png"),
    "TVS Ronin": os.path.join(ASSETS_FOLDER, "TVS_Ronin.png"),
    "TVS Jupiter Old": os.path.join(ASSETS_FOLDER, "TVS_Jupiter_Old.png"),
    "TVS Jupiter New": os.path.join(ASSETS_FOLDER, "TVS_Jupiter_New.png"),
    "TVS Ntorq 125": os.path.join(ASSETS_FOLDER, "TVS_Ntorq_125.png"),
    "TVS Ntorq 150": os.path.join(ASSETS_FOLDER, "TVS_Ntorq_150.png"),
    "TVS Scooty Pep Plus": os.path.join(ASSETS_FOLDER, "TVS_Scooty_Pep_Plus.png"),
    "TVS Zest": os.path.join(ASSETS_FOLDER, "TVS_Zest.png"),
    "TVS iQube ST": os.path.join(ASSETS_FOLDER, "TVS_iQube_ST.png"),
    "TVS iQube S": os.path.join(ASSETS_FOLDER, "TVS_iQube_S.png"),
    "TVS Radeon": os.path.join(ASSETS_FOLDER, "TVS_Radeon.png"),
    "TVS Sport": os.path.join(ASSETS_FOLDER, "TVS_Sport.png"),
    "TVS Sport Kick Start": os.path.join(ASSETS_FOLDER, "TVS_Sport_Kick_Start.png"),
    "TVS Star City Plus": os.path.join(ASSETS_FOLDER, "TVS_Star_City_Plus.png"),
    "TVS XL 100": os.path.join(ASSETS_FOLDER, "TVS_XL_100.png"),
    "TVS XL 100 HD": os.path.join(ASSETS_FOLDER, "TVS_XL_100_HD.png"),
    "TVS KING GS+": os.path.join(ASSETS_FOLDER, "TVS_KING_GS+.png"),
    "TVS KING ZS+": os.path.join(ASSETS_FOLDER, "TVS_KING_ZS+.png"),
    "TVS KING LS+": os.path.join(ASSETS_FOLDER, "TVS_KING_LS+.png"),
    "TVS KING GD": os.path.join(ASSETS_FOLDER, "TVS_KING_GD.png"),
    "TVS KING ZD": os.path.join(ASSETS_FOLDER, "TVS_KING_ZD.png"),
    "TVS KING ZK PF": os.path.join(ASSETS_FOLDER, "TVS_KING_ZK_PF.png"),
    "TVS KING ZK LT": os.path.join(ASSETS_FOLDER, "TVS_KING_ZK_LT.png"),
    "TVS KING E": os.path.join(ASSETS_FOLDER, "TVS_KING_E.png"),
    "TVS 3W LARGE": os.path.join(ASSETS_FOLDER, "TVS_3W_LARGE.png"),
    "TVS KING 3W LARGE": os.path.join(ASSETS_FOLDER, "TVS_KING_3W_LARGE.png"),
}

VEHICLE_MODELS: List[Tuple[str, str, str, str]] = [
    ("TVS Apache 160 4V ABS", "Dual Channel - 4V - EMS - ABS (Cont)", "MD637CE5XXXXXXXXX", "MOTOR CYCLE"),
    ("TVS Apache RR 310", "Apache - EMS, ABS(BOSCH)", "MD634CE4XXXXXXXXXX", "MOTOR CYCLE"),
    ("TVS Apache RTR 160 2V", "Single CH - 2V - EMS,ABS(BOSCH) ", "MD634CE4XXXXXXXXX", "MOTOR CYCLE"),
    ("TVS Apache RTR 180 2V RM", "RM - EMS,ABS(BOSCH) ", "MD634CE4XXXXXXXXX", "MOTOR CYCLE"),
    ("TVS Apache RTR 200 4V RM", "EMS", "MD637XXXXXXXXXXXX", "MOTOR CYCLE"),
    ("TVS Apache RTX", "EMS, ABS, ICU(VISTEON) ", "MD637BT1XXXXXXXXX", "MOTOR CYCLE"),
    ("TVS Raider 125", "EMS, ICU", "MD625CK2XXXXXXXXX", "MOTOR CYCLE"),
    ("TVS Raider IGO", "EMS, SEDAMAC", "MD625CK2XXXXXXXXX", "MOTOR CYCLE"),
    ("TVS Ronin", "EMS, ABS, ICU, ISG", "MD637CE5XXXXXXXXX", "MOTOR CYCLE"),
    ("TVS Radeon", "EMS", "MD625CKXXXXXXXXXXX", "MOTOR CYCLE"),
    ("TVS Sport", "EMS", "MD625CK2XXXXXXXXXX", "MOTOR CYCLE"),
    ("TVS Sport Kick Start", "EMS - KEIHIN", "MD625CK2XXXXXXXXXX", "MOTOR CYCLE"),
    ("TVS Star City Plus", "EMS", "MD625AK2XXXXXXXXXX", "MOTOR CYCLE"),
    ("TVS XL 100", "EMS", "MD637BT1XXXXXXXXXX", "MOTOR CYCLE"),
    ("TVS XL 100 HD", "EMS", "MD637BT1XXXXXXXXXX", "MOTOR CYCLE"),
    ("TVS Jupiter Old", "EMS - CONTINENTAL", "MD637BT1XXXXXXXXXX", "SCOOTER"),
    ("TVS Jupiter New", "EMS, ISG & ICU", "MD637BT1XXXXXXXXXX", "SCOOTER"),
    ("TVS Ntorq 125", "EMS", "MD637XXXXXXXXXXXXX", "SCOOTER"),
    ("TVS Ntorq 150", "", "MD637XXXXXXXXXXXXX", "SCOOTER"),
    ("TVS Scooty Pep Plus", "EMS", "MD637XXXXXXXXXXXXX", "SCOOTER"),
    ("TVS Zest", "EMS", "MD637XXXXXXXXXXXXX", "SCOOTER"),
    ("TVS iQube ST", "EMS", "MD62912XXXXXXXXXX", "SCOOTER"),
    ("TVS iQube S", "EMS", "MD62912XXXXXXXXXX", "SCOOTER"),
    ("TVS KING GS+", "PASSENGER - AC Pet", "MD6M14PFXXXXXXXXX", "3-WHEELER"),
    ("TVS KING ZS+", "PASSENGER - AC CNG", "MD6M14CFXXXXXXXXX", "3-WHEELER"),
    ("TVS KING LS+", "PASSENGER - AC LPG", "MD6M14LFXXXXXXXXX", "3-WHEELER"),
    ("TVS KING GD", "PASSENGER - LC Pet", "MD6M1LPFXXXXXXXXX", "3-WHEELER"),
    ("TVS KING ZD", "PASSENGER - LC CNG", "MD6M1LCFXXXXXXXXXX", "3-WHEELER"),
    ("TVS KING ZK PF", "CARGO PF", "MD6N1LCFXXXXXXXXXX", "3-WHEELER"),
    ("TVS KING ZK LT", "CARGO LT", "MD6N1LCFXXXXXXXXXX", "3-WHEELER"),
    ("TVS KING E", "PASSENGER - EV", "MD6EVM1DXXXXXXXXXX", "3-WHEELER"),
    ("TVS 3W LARGE", "CARGO - LC CNG", "MD6N1LCGXXXXXXXXXX", "3-WHEELER"),
    ("TVS KING 3W LARGE", "CARGO - EV", "MD6EVNICXXXXXXXXXX", "3-WHEELER"),
]
