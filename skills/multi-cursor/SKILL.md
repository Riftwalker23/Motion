---
name: multi-cursor
description: Control the user's mouse as a team of labeled agents. Each part of a task (Wiring, Parts, QA, Simulation, Display…) gets its own colored, named cursor on screen, and the agent doing the current step drives the real mouse pointer. Use this whenever the user wants "multiple cursors", "agents working on my screen", multi-agent mouse control, "all the cursors working on my <app>", or wants Claude's computer-use actions split across named agents, even if they only say "launch the cursors" or "use the cursors to control <app>".
---

# Multi-cursor control

This skill splits computer-use work across named agents and shows each one as
its own labeled cursor. `scripts/cursors.py` draws the cursors in a
transparent, click-through, always-on-top window. `scripts/cursorctl.py`
decides which agent is driving.

How it works: Windows has one real mouse pointer, so agents **take turns**
driving it. The agent you select with `use <Label>` locks onto the real
pointer, so every move and click you make with the computer-use tools appears
as that agent (with a click ripple in its color). The other agents stay
visible and active around the work area until it's their turn. The overlay
itself never sends input, so all real actions come from your computer-use calls.

Everything goes through `scripts/cursorctl.py` (run it with `python`, paths
relative to this skill folder):

| Command | Effect |
|---|---|
| `start --preset proteus` | Launch with Proteus zones and agents (Wiring, Parts, QA, Simulation, Timing, Display, Power, Debug) |
| `start` | Launch with the general whole-screen preset (Planner, Builder, QA, Research, Design, Debug, Writer, Ops) |
| `start --labels "Copy,CTA,Geo,Budget" --count 4` | Custom agents for the task at hand |
| `use <Label>` | That agent takes the real pointer |
| `wander` | Release the pointer. No agent is driving |
| `hide` / `show` | Toggle the cursors (F9 does the same for the user) |
| `stop` | Close the overlay (F10 does the same for the user) |
| `status` | Is it running, and which agent is driving |

## Workflow

Follow the `pc-control` skill for everything about safe clicking (access,
focus, dialogs, placement modes). This skill adds how to split the work:

1. **Pick agents that match the task.** Use a preset when one fits the app,
   otherwise `--labels` with roles drawn from the task itself (e.g. for a
   spreadsheet: `Data,Formulas,Charts,QA`).
2. **`start`** the overlay, then confirm with `status`.
3. **Break the task into segments**, each owned by the agent whose role fits:
   `Parts` works in the component library, `Wiring` traces or draws
   connections, `QA` selects and inspects, `Display` handles outputs and
   views, `Simulation` uses run controls, and so on.
4. For each segment: `python cursorctl.py use <Label>`, then one
   `computer_batch` with that segment's actions.
5. **Move in hops, not jumps.** Use `mouse_move` → `wait 0.3–0.7s` →
   `mouse_move`. The agent cursor eases toward the pointer, and hops keep it
   on the pointer, so what's on screen matches where the click lands.
   Wait about 0.3s after the last hop before clicking.
6. Hand off between agents whenever the kind of work changes. The user can
   see at a glance which agent is responsible for what's happening.
7. When done: `wander` to free the pointer, or `stop` to close the overlay.

Each agent's actions are real actions on the user's PC. Edits, saving,
running and anything destructive need the user's request, exactly as in
`pc-control`. Hovering, selecting, zooming, and opening a dialog then
pressing **Cancel** are safe ways to inspect.

## Notes

- Computer-use screenshots don't show the overlay. It's a separate,
  un-granted window, so it's masked or invisible to you. Don't ask for access
  to Python just to see it. Rely on `status`, and ask the user if something
  looks wrong.
- The user's own mouse moves the same pointer. Ask them not to touch it while
  an agent is driving.
- Presets (wander `area` plus per-agent `extras` such as the device list or
  the play button) are at the top of `cursors.py`. Add a new key to `PRESETS`
  when an app's layout differs a lot.
