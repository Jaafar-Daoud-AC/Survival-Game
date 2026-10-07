````markdown
# Survival Game

A 2D side-scrolling platformer developed with Python and Pygame.

The game features five levels, unique environments, enemies, boss battles, unlockable abilities, checkpoints, and a separate Survival Mode where the player fights through endless waves of enemies.

## 🎮 Features

- 2D side-scrolling platformer gameplay
- Five unique levels
- A unique boss at the end of each level
- Unlockable abilities as the player progresses
- Multiple enemy types
- Environmental hazards
- Checkpoints
- Health and energy system
- Level selection
- Three-phase boss battles
- Separate Survival Mode
- Persistent save data
- Keyboard-based controls
- Fullscreen support

## 🕹️ Gameplay

The player starts with basic movement, jumping, and shooting abilities.

After defeating each boss, a new ability becomes available, allowing the player to progress through more challenging environments and combat situations.

### Abilities

| Unlock | Ability | Energy |
|---|---|---:|
| After Level 1 | Double Jump | Free |
| After Level 2 | Dash | 15 |
| After Level 3 | Triple Shot | 20 |
| After Level 4 | Shield | 30 |
| After Level 5 | Nova | 45 |
| After Level 5 | Tank | 100 |

Energy regenerates automatically and can also be restored faster by hitting enemies.

Health and energy pickups are distributed throughout the levels, while flags act as checkpoints.

## 🌍 Levels

The game contains five different environments, each with its own enemies, hazards, and boss.

### Level 1 — The City

![The City](screenshots/level1_city.jpg)

### Level 2 — The Forest

![The Forest](screenshots/level2_forest.jpg)

### Level 3 — The Desert

![The Desert](screenshots/level3_desert.jpg)

### Level 4 — The Castle

![The Castle](screenshots/level4_castle.jpg)

### Level 5 — The Volcano

![The Volcano](screenshots/level5_volcano.jpg)

### Level Select

![Level Select](screenshots/select.jpg)

Later levels introduce additional challenges such as moving platforms, spikes, and lava pits.

## 👾 Enemies

The game includes multiple enemy types, including:

- Goblins
- Runners
- Brutes
- Archers
- Bats
- Tanks

Enemy difficulty increases throughout the later levels.

## 👹 Boss Battles

Each level ends with a unique boss battle.

Bosses have different attack patterns, including:

- Charges
- Ground slams
- Shockwaves
- Projectiles
- Falling fireballs
- Summoned enemies

Each boss has three combat phases, becoming more aggressive as its health decreases.

### Bosses

| Level | Boss |
|---|---|
| Level 1 | Goblin King |
| Level 2 | Forest Warden |
| Level 3 | Iron Beast |
| Level 4 | Dark Knight |
| Level 5 | The Overlord |

### Boss Screenshots

![Goblin King](screenshots/boss1_goblin_king.JPG)

![Forest Warden](screenshots/boss2_forest_warden.jpg)

![Iron Beast](screenshots/boss3_iron_beast.jpg)

![Dark Knight](screenshots/boss4_dark_knight.jpg)

![The Overlord](screenshots/boss5_overlord.jpg)

When a boss fight begins, the camera locks onto the arena and the player cannot escape the battle.

If the player dies, they return to the last checkpoint and the boss fight is reset.

## ♾️ Survival Mode

Survival Mode takes place in a single arena with endless waves of enemies.

- Each wave becomes more difficult
- Enemy numbers increase over time
- A boss appears every five waves
- Players receive a bonus for clearing waves
- Best wave is saved
- Best score is saved

![Survival Mode](screenshots/survival.jpg)

## 🎮 Controls

| Key | Action |
|---|---|
| Left / Right | Move |
| Space | Jump |
| S | Shoot |
| Up / Down | Increase / decrease movement speed |
| D | Dash |
| A | Triple Shot |
| F | Shield |
| E | Nova |
| R | Tank |
| P | Pause |
| W | Restart after dying |
| M | Return to menu |
| F11 | Toggle fullscreen |

The letter-based controls are read by keyboard position, allowing them to work with an Arabic keyboard layout as well.

## ⚙️ Requirements

- Python 3
- Pygame 2

## ▶️ How to Run

Install the required dependencies:

```bash
pip install -r requirements.txt
````

Run the game:

```bash
python servaivle.py
```

Run the game from inside the project directory because the game loads its images and sounds using relative paths.

## 💾 Save System

The game saves progress in:

```text
save.json
```

The save file is stored next to the main game script.

Deleting `save.json` will reset the saved progress.

## 📁 Project Structure

```text
Survival-Game/
├── servaivle.py
├── PLAYER.py
├── ENEMY.py
├── BOSS.py
├── ABSOLUTE.py
├── SKILLS.py
├── BULLET.py
├── EFFECTS.py
├── PLATFORM.py
├── LEVELS.py
├── requirements.txt
├── save.json
├── README.md
└── screenshots/
    ├── menu.jpg
    ├── level1_city.jpg
    ├── level2_forest.jpg
    ├── level3_desert.jpg
    ├── level4_castle.jpg
    ├── level5_volcano.jpg
    ├── select.jpg
    ├── boss1_goblin_king.jpg
    ├── boss2_forest_warden.jpg
    ├── boss3_iron_beast.jpg
    ├── boss4_dark_knight.jpg
    ├── boss5_overlord.jpg
    └── survival.jpg
```

## 🧩 Main Components

| File           | Purpose                                                         |
| -------------- | --------------------------------------------------------------- |
| `servaivle.py` | Main game loop, menus, camera, level loading, and Survival Mode |
| `PLAYER.py`    | Player character                                                |
| `ENEMY.py`     | Enemy characters and enemy behavior                             |
| `BOSS.py`      | Boss characters and boss behavior                               |
| `ABSOLUTE.py`  | Base movement and collision system                              |
| `SKILLS.py`    | Player abilities                                                |
| `BULLET.py`    | Projectiles                                                     |
| `EFFECTS.py`   | Visual effects and particles                                    |
| `PLATFORM.py`  | Platforms, hazards, pickups, and checkpoints                    |
| `LEVELS.py`    | Level data                                                      |

Level configuration is handled in `LEVELS.py`.

Enemy statistics are defined in `ENEMY.py`, while boss statistics are defined in `BOSS.py`.

## 📌 Project Status

**🚧 In Progress**

The project is currently under development, with additional improvements and content planned.

## 💻 Technologies

* Python
* Pygame

## 👤 Author

**Jaafar Daoud**

Applied Communications Engineer

GitHub: [Jaafar-Daoud-AC](https://github.com/Jaafar-Daoud-AC)

```
```
