# Motion

Claude Code skills for controlling the mouse on a Windows PC, with **multiple
labeled agent cursors**. Claude splits a task across named agents (Wiring,
Parts, QA, Simulation…). Each agent has its own colored cursor on screen, and
the agent doing the current step drives the real mouse pointer.

## Skills

| Skill | What it does |
|---|---|
| `skills/pc-control/` | How Claude drives a Windows PC with computer-use tools safely. Covers app access, keyboard focus, dialogs that can destroy work, and editors with placement modes. `references/proteus.md` has notes for Labcenter Proteus 9. |
| `skills/multi-cursor/` | Multi-agent cursor control. `scripts/cursors.py` draws the agent cursors, and `scripts/cursorctl.py` hands the real pointer from one agent to the next. |

Also included: `launchers/Start Cursors.bat`, `launchers/Stop Cursors.bat`,
and `install-skills.bat`.

## Requirements

- Windows 10/11
- Python 3.10+ with tkinter (included in the python.org installer). No other
  packages.
- Claude Code with computer use enabled

## Install

Double-click `install-skills.bat`, or copy the two folders under `skills/`
into `%USERPROFILE%\.claude\skills\`. Claude Code loads them in the next
session. Then ask Claude things like *"use the cursors to inspect the open
Proteus circuit"*.

## How multi-cursor control works

Windows has one real mouse pointer, so agents take turns driving it:

```bat
python skills\multi-cursor\scripts\cursorctl.py start --preset proteus
python skills\multi-cursor\scripts\cursorctl.py use Parts     :: Parts drives the pointer
python skills\multi-cursor\scripts\cursorctl.py use Wiring    :: hand off to Wiring
python skills\multi-cursor\scripts\cursorctl.py wander        :: release the pointer
python skills\multi-cursor\scripts\cursorctl.py stop
```

| Command | Effect |
|---|---|
| `start [--preset proteus\|screen] [--labels "A,B,C"] [--count N]` | Open the overlay with a preset or custom agents |
| `use <Label>` | That agent takes the real pointer. Its moves and clicks (with a ripple in its color) are Claude's real computer-use actions |
| `wander` | No agent is driving |
| `hide` / `show` / `stop` / `status` | Overlay control |

Hotkeys (global): **F9** hide/show, **F10** close.

The overlay window is transparent and click-through, so it never blocks or
sends input to the app underneath. All real actions come from Claude's
computer-use calls, following the safety rules in `pc-control`.
