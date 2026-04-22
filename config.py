# config.py
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
IMG = ASSETS / "images"
SND = ASSETS / "sounds"

IMG.mkdir(parents=True, exist_ok=True)
SND.mkdir(parents=True, exist_ok=True)

WIDTH = 1280
HEIGHT = 720
GROUND_Y = HEIGHT - 80
FPS = 60

TITLE = "Galactic Guardian - Hanh Trinh Khong Gian"

LEVEL_NAMES = [
    "Man 1 - Vanh Dai Sao Choi",
    "Man 2 - Hanh Tinh Lua Ignis",
    "Man 3 - Tinh Van Bang Gia Glacia",
    "Man 4 - Loi Thien Ha Dien Tu",
    "Man 5 - Ky Quan Bong Toi"
]

BOSS_INFO = {
    1: {
        "name": "Comet Warden",
        "title": "Nguoi Gac Sao Choi",
        "dialogue": [
            "Nguoi dam xam pham vanh dai sao choi?",
            "Ta la Comet Warden, ke bao ve dai ngan ha nay!",
            "Hay the hien suc manh cua nguoi!"
        ],
        "color": "CYAN",
        "hp": 6,
        "image": "boss_phase1.png"
    },
    2: {
        "name": "Inferno Dragon",
        "title": "Rong Lua Ignis",
        "dialogue": [
            "GRAAA! Nguoi den tu dau, chien binh?",
            "Hanh tinh Ignis la lanh dia cua ta!",
            "Hay chuan bi chay ruoi trong dung nham!"
        ],
        "color": "ORANGE",
        "hp": 6,
        "image": "boss_phase2.png"
    },
    3: {
        "name": "Frost Queen",
        "title": "Nu Hoang Bang Gia",
        "dialogue": [
            "Nguoi da lac vao tinh van Glacia...",
            "Noi day dong bang moi sinh linh!",
            "Hay chung to trai tim nguoi co du am ap?"
        ],
        "color": "BLUE",
        "hp": 6,
        "image": "boss_phase3.png"
    },
    4: {
        "name": "Nebula Specter",
        "title": "Ma Quai Tinh Van",
        "dialogue": [
            "Hahaha... Nguoi nghi minh co the vao loi thien ha?",
            "Nang luong dien tu se nghien nat nguoi!",
            "Hay tan bien cung tinh van!"
        ],
        "color": "PURPLE",
        "hp": 6,
        "image": "boss_phase4.png"
    },
    5: {
        "name": "Void Emperor",
        "title": "Hoang De Bong Toi",
        "dialogue": [
            "Nguoi da den duoc day... That an tuong!",
            "Nhung day la ky quan cuoi cung cua vu tru!",
            "Hay chien dau voi ta, neu nguoi dam!"
        ],
        "color": "RED",
        "hp": 6,
        "image": "boss_phase5.png"
    }
}

ENEMY_IMAGES = {
    "basic": "enemy_basic.png",
    "fast": "enemy_fast.png",
    "mage": "enemy_mage.png",
    "shield": "enemy_tank.png",
    "heavy": "enemy_heavy.png"
}

COLORS = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "RED": (255, 50, 50),
    "GREEN": (50, 255, 50),
    "BLUE": (50, 150, 255),
    "YELLOW": (255, 255, 50),
    "PURPLE": (150, 50, 255),
    "ORANGE": (255, 150, 50),
    "GRAY": (100, 100, 100),
    "DARK_GRAY": (50, 50, 50),
    "CYAN": (0, 255, 255),
    "BROWN": (139, 69, 19),
    "PINK": (255, 100, 150),
    "GOLD": (255, 215, 0),
    "SILVER": (192, 192, 192),
    "MAGENTA": (255, 0, 255),
}