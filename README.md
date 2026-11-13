# Motion

Claude Code skills for controlling a Windows PC, plus a **multi-cursor
overlay** that makes one real mouse look like a team of AI agents working
on screen. Several labeled, colored cursors (Wiring, Parts, QA, Simulation…)
move, click and draw wires.

## What's inside

| Path | What it is |
|---|---|
| `skills/pc-control/` | Skill: how Claude drives a Windows PC with computer-use tools safely. Covers app access, focus problems, dialogs that destroy work and placement-mode editors. `references/proteus.md` has notes for Labcenter Proteus 9. |
| `skills/multi-cursor/` | Skill + scripts: the overlay (`scripts/cursors.py`) and its controller (`scripts/cursorctl.py`). |
| `launchers/` | Double-click `Start Cursors.bat` / `Stop Cursors.bat`. |
| `install-skills.bat` | Copies both skills into `%USERPROFILE%\.claude\skills`. |

## Requirements

- Windows 10/11
- Python 3.10+ with tkinter (the standard python.org installer includes it).
  No other packages.

## Install the skills

Double-click `install-skills.bat`, or copy the two folders under `skills/`
into `%USERPROFILE%\.claude\skills\`. Claude Code picks them up in the next
session.

## Use the overlay

```bat
launchers\Start Cursors.bat                       :: Proteus preset
launchers\Start Cursors.bat --preset screen       :: generic whole-screen preset
launchers\Start Cursors.bat --labels "Copy,CTA,Geo,Budget" --count 4
```

Hotkeys (global): **F9** hide/show, **F10** quit.

Controller commands:

```bat
python skills\multi-cursor\scripts\cursorctl.py use Wiring   :: Wiring agent rides the real mouse
python skills\multi-cursor\scripts\cursorctl.py wander       :: everyone wanders
python skills\multi-cursor\scripts\cursorctl.py hide | show | stop | status
```

The overlay is a transparent, click-through, always-on-top window. It never
sends input, so it can't change anything on screen. Whatever real actions
happen (yours, or Claude's through computer use) are dressed up by whichever
agent is on the mouse.

## Recording tips

- Capture the **whole display** (Snipping Tool screen recording, OBS Display
  Capture). Window-only capture misses the overlay.
- Park your own mouse in a corner while Claude acts.
- It's a visual effect. If you post the video, a short caption saying so
  keeps viewers from assuming several real agents were at work.
