---
name: multi-cursor
description: Make one real mouse pointer look like a team of AI agents working on screen. It shows several labeled, colored cursors (e.g. Wiring, Parts, QA, Simulation), and the agent you pick rides the real pointer while the others wander, click and draw wires. Use this whenever the user wants "multiple cursors", "agents working on my screen", a staged or "acting" demo for a screen recording, the multi-agent cursor effect from a video, or wants Claude's computer-use actions to look like several agents doing them, even if they only say "launch the cursors" or "make it look like the video".
---

# Multi-cursor overlay

`scripts/cursors.py` is a transparent, click-through, always-on-top window
that draws labeled agent cursors. It never sends input itself, so it can't
change anything on screen. The *real* work (if any) is done by you with the
computer-use tools, and the overlay just dresses it up. One agent can be
attached to the real mouse pointer, so each real click looks like that
agent made it (with a ripple in its color).

Everything goes through `scripts/cursorctl.py` (run it with `python`, paths
relative to this skill folder):

| Command | Effect |
|---|---|
| `start --preset proteus` | Launch with Proteus zones and labels (Wiring, Parts, QA, Simulation, Timing, Display, Power, Debug) |
| `start` | Launch with a generic whole-screen preset (Planner, Builder, QA, Research, Design, Debug, Writer, Ops) |
| `start --labels "Copy,CTA,Geo,Budget" --count 4` | Custom agent names |
| `use <Label>` | That agent glides onto the real pointer and follows it |
| `wander` | Release it. Everyone wanders again |
| `hide` / `show` | Toggle visibility (F9 does the same for the user) |
| `stop` | Quit the overlay (F10 does the same for the user) |
| `status` | Is it running, and which agent is active |

## Two ways to use it

### A. Pure acting (no real actions)

The user just wants the look for a recording. Run `start` with a fitting
preset or labels, tell them about F9/F10, and you're done. The agents wander
on their own.

### B. One real cursor playing many agents

Use this when the user wants the cursors to "control" an app. Follow the
`pc-control` skill for everything about safe clicking. This section only
adds the choreography:

1. `start` the overlay (pick labels that match the app and task).
2. Break the work into short **segments**, each owned by one agent whose name
   fits what happens: `Parts` browses the library, `Wiring` traces or draws
   connections, `QA` selects and inspects parts, `Display` zooms on outputs,
   `Simulation` uses the run controls, and so on.
3. For each segment: `python cursorctl.py use <Label>`, then one
   `computer_batch` for that segment.
4. Inside a batch, make the movement read as human:
   - Move in several hops (`mouse_move` → `wait 0.3–0.7s` → `mouse_move`)
     instead of teleporting straight to the target. The overlay eases toward
     the pointer, so hops look like smooth gliding.
   - Wait ~0.3s after the final hop before clicking, so the agent has arrived
     when the ripple fires.
   - Hover over things (pins, list items, parts) as "reading" moments. It's
     harmless and looks deliberate.
5. Switch agents every 3–8 actions so viewers see different agents taking
   turns. While one agent is on the real mouse, the others keep busy by
   themselves.
6. When finished, `wander` (keeps the look going) or `stop`.

Keep the real actions harmless unless the user asked for real changes.
Hovering, selecting, zooming and opening a dialog then pressing **Cancel**
all look busy without altering their work. Real edits, saving and running
simulations need the user's request, exactly as in `pc-control`.

## Things worth knowing

- Recording must capture the **whole display** (Snipping Tool screen
  recording, OBS Display Capture). Window-only capture, such as Xbox Game Bar,
  misses the overlay because it's a separate window.
- The real system pointer is still visible under the active agent's arrow.
  Suggest the user move their own mouse into a corner while you act, and not
  touch it during your batches.
- Computer-use screenshots don't show the overlay. It's a separate,
  un-granted window, so it's either masked or invisible to you. Don't ask for
  access to Python just to see it. Trust `status`, and ask the user how it
  looks.
- The preset `area` and `extras` (special haunts like the device list or the
  play button) are at the top of `cursors.py`. Add a new preset there when an
  app's layout differs a lot (a new key in `PRESETS`).
- Being honest about it: this is a visual effect. If the user is posting the
  video, mention once that viewers might take it as several real agents and a
  short caption avoids that. Don't lecture.
