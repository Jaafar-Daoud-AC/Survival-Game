# srvivle

A 2D side-scrolling platformer I made with Python and pygame. You fight through five levels, beat a boss at the end of each one, and unlock a new ability every time. There's also a survival mode where you just hold out against waves for as long as you can.

![menu](screenshots/menu.jpg)

## Running it

You need Python 3 and pygame 2.

```
pip install -r requirements.txt
python servaivle.py
```

Run it from inside this folder, because the images and sounds are loaded relative to the script. The game saves your progress in a `save.json` next to it. If you delete that file you start over.

## Controls

| Key | What it does |
|---|---|
| Left / Right | move |
| Space | jump (press again in the air for a double jump, once you've unlocked it) |
| S | shoot, hold it for auto fire |
| Up / Down | run faster / slower |
| D | dash |
| A | triple shot |
| F | shield |
| E | nova |
| R | tank |
| P | pause |
| W | restart after dying |
| M | back to the menu from the death screen |
| F11 | fullscreen |

The letter keys are read by their position on the keyboard, so they work with an Arabic layout too.

## Abilities

You start with nothing but jumping and shooting. Each boss you beat gives you something:

| After | You get | Energy |
|---|---|---|
| Level 1 | double jump | free |
| Level 2 | dash, you can't be hurt while dashing and it hits enemies | 15 |
| Level 3 | triple shot | 20 |
| Level 4 | shield, blocks everything for 4 seconds | 30 |
| Level 5 | nova, a blast around you that also wipes enemy bullets | 45 |
| Level 5 | tank, a green tank drives forward and shoots everything | 100 |

Energy refills slowly by itself and faster when you hit enemies. Hearts and energy pickups are scattered around, and the flags are checkpoints.

## Levels

Five environments, each with its own enemies, hazards and boss.

| | |
|---|---|
| ![city](screenshots/level1_city.jpg) **1. The City** | ![forest](screenshots/level2_forest.jpg) **2. The Forest** |
| ![desert](screenshots/level3_desert.jpg) **3. The Desert** | ![castle](screenshots/level4_castle.jpg) **4. The Castle** |
| ![volcano](screenshots/level5_volcano.jpg) **5. The Volcano** | ![select](screenshots/select.jpg) level select |

Enemies are goblins, runners, brutes, archers, bats and tanks. Later levels have moving platforms, spikes and lava pits, so you'll need the double jump and the dash to get across some of the gaps.

## Bosses

Each boss has its own set of attacks (charges, ground slams, shockwaves you have to jump over, projectiles, falling fireballs, summoned minions) and gets nastier as its health drops. The health bar is split into three parts, which are the three phases.

| | |
|---|---|
| ![king](screenshots/boss1_goblin_king.jpg) **Goblin King** | ![warden](screenshots/boss2_forest_warden.jpg) **Forest Warden** |
| ![beast](screenshots/boss3_iron_beast.jpg) **Iron Beast** | ![knight](screenshots/boss4_dark_knight.jpg) **Dark Knight** |
| ![overlord](screenshots/boss5_overlord.jpg) **The Overlord** | |

When a boss fight starts the camera locks onto the arena and a wall closes behind you, so there's no running away. If you die you come back at the last checkpoint and the boss is reset.

## Survival mode

One arena, endless waves. Every wave is bigger than the last and a boss shows up every five waves. Enemies get tougher as the waves go up, and you get a small bonus for clearing each one. The game remembers your best wave and best score.

![survival](screenshots/survival.jpg)

## Files

- `servaivle.py` main loop, menus, camera, level loading, survival mode
- `PLAYER.py`, `ENEMY.py`, `BOSS.py` the characters
- `ABSOLUTE.py` the base class with the movement and collision code
- `SKILLS.py`, `BULLET.py`, `EFFECTS.py` abilities, projectiles, particles
- `PLATFORM.py` platforms, hazards, pickups, checkpoints
- `LEVELS.py` all the level data

If you want to change a level, everything is in `LEVELS.py`. Enemy stats are in `ENEMY.py` (the `tipos` dictionary) and boss stats are in `BOSS.py`.

## Notes

It's keyboard only for now. If you find a bug or get low FPS in the later levels, open an issue and tell me where it happened.
