from pathlib import Path
from typing import Literal, TypedDict


MotionName = Literal["straight", "sine", "zigzag"]


class EnemyWaveConfig(TypedDict):
    name: str
    frames: list[str]
    count: int
    health: int
    score: int
    speed: float
    motion: MotionName
    shootCooldownMs: int

BASE_DIR = Path(__file__).resolve().parent
RESOURCE_DIR = BASE_DIR / "resources"

WINDOW_WIDTH = 512
WINDOW_HEIGHT = 768
FPS = 60
GAME_TITLE = "空战小游戏"
START_MESSAGE = "按 Space 开始游戏"
CONTROL_TIP = "方向键: 移动  Space: 发射导弹"
WIN_MESSAGE = "胜利!"
GAME_OVER_MESSAGE = "游戏结束"
RESTART_MESSAGE = "按 Space 重新开始"
HUD_TEXT = "生命: {health}  分数: {score}  Boss 生命: {bossHealth}"
UI_FONT_NAMES = [
    "microsoftyahei",
    "simhei",
    "simsun",
    "nsimsun",
    "dengxian",
    "fangsong",
    "kaiti",
    "notosanscjk",
    "sourcehansanssc",
]

BACKGROUND_FILES = [
    "background_01.png",
    "background_02.png",
    "background_03.png",
    "background_04.png",
    "background_05.png",
    "background_06.png",
    "background_07.png",
]
BACKGROUND_SCROLL_SPEED = 90.0
BACKGROUND_SWITCH_SECONDS = 10.0

PLAYER_HEALTH = 5
PLAYER_SPEED = 360.0
PLAYER_INVINCIBLE_MS = 900
PLAYER_MISSILE_COOLDOWN_MS = 240
PLAYER_MISSILE_SPEED = -560.0
PLAYER_MISSILE_DAMAGE = 1
PLAYER_MISSILE_FILE = "myPlane_missile_01_01.png"

ENEMY_SPAWN_INTERVAL_MS = 900
ENEMY_WAVE_DELAY_MS = 1200
ENEMY_MISSILE_SPEED = 230.0
ENEMY_MISSILE_FILE = "enemyPlane_missile_0100.png"

BOSS_HEALTH = 30
BOSS_SCORE = 2000
BOSS_SPEED = 120.0
BOSS_MISSILE_SPEED = 260.0
BOSS_MISSILE_COOLDOWN_MS = 1500
BOSS_TARGET_TOP = 42
BOSS_WIDTH = 280

STATE_START = "start"
STATE_PLAYING = "playing"
STATE_WIN = "win"
STATE_GAME_OVER = "gameOver"

ENEMY_WAVES: list[EnemyWaveConfig] = [
    {
        "name": "Scout",
        "frames": [
            "enemyPlane_01_01.png",
            "enemyPlane_01_02.png",
            "enemyPlane_01_03.png",
            "enemyPlane_01_04.png",
        ],
        "count": 8,
        "health": 2,
        "score": 100,
        "speed": 115.0,
        "motion": "straight",
        "shootCooldownMs": 2600,
    },
    {
        "name": "Raider",
        "frames": [
            "enemyPlane_02_01.png",
            "enemyPlane_02_02.png",
            "enemyPlane_02_03.png",
            "enemyPlane_02_04.png",
        ],
        "count": 5,
        "health": 4,
        "score": 180,
        "speed": 95.0,
        "motion": "sine",
        "shootCooldownMs": 2400,
    },
    {
        "name": "Cruiser",
        "frames": [
            "enemyPlane_03_01.png",
            "enemyPlane_03_02.png",
            "enemyPlane_03_03.png",
            "enemyPlane_03_04.png",
        ],
        "count": 4,
        "health": 6,
        "score": 280,
        "speed": 85.0,
        "motion": "zigzag",
        "shootCooldownMs": 2200,
    },
]

WHITE = (245, 245, 245)
YELLOW = (255, 222, 89)
RED = (240, 74, 74)
DARK_OVERLAY = (0, 0, 0, 150)