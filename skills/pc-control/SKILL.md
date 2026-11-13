---
name: pc-control
description: How to drive the user's Windows PC with the computer-use tools (screenshots, clicks, typing in desktop apps) safely and efficiently. Use this whenever the user asks you to do something in a desktop app on their PC: "open Proteus and…", "click…", "do this on my PC", "control my screen", "modify the open circuit/file in <app>", or shares a video of a task and wants it done on their PC. Also use it before combining computer use with the multi-cursor overlay. Covers app access, focus problems, dialogs that can destroy work, editors with placement modes (Proteus, CAD, design tools), and Windows-specific gotchas learned on this machine.
---

# PC control (Windows)

You are operating a real person's computer. Every click lands on their actual
files and their actual apps. The goal is to get the task done with as few
surprises as possible, so the rules below are mostly about avoiding the
mistakes that are easy to make and hard to undo.

## 1. Before touching anything

1. **Load the tools in one go**: `ToolSearch` with query `computer-use`,
   `max_results: 30`.
2. **Find out what the user actually wants changed.** "Modify the open circuit"
   with no change named is not enough to start editing. Look first, then ask
   one concrete question. Looking is free; guessing edits is not.
3. **Check whether the app is already running** before launching it:
   ```bash
   tasklist //FI "IMAGENAME eq PDS.exe"
   ```
   On this PC, `open_application` on an app that is already running can start
   a **second instance** (this happened with Proteus). If the app is running,
   don't call `open_application`. Request access, take a screenshot, and if
   the window isn't in front, click its taskbar icon.
4. **`request_access`** with the exact Start-menu names (e.g. `"Proteus 9
   Demonstration"`). Ask for only what the task needs. If the user denies an
   app, respect it. Don't route around the denial, for example by grabbing
   the screen with a script.
5. **Figure out which file is open, or which one they mean.** If you're unsure,
   check modification times (`ls -lt`). The file saved most recently is
   usually the one they're working on. Say which one you picked.

## 2. Seeing the screen cheaply

- Use `screenshot` with `scale: 0.6` for orientation. Click coordinates are
  **always in the full-resolution frame** (the tool reports it, e.g.
  1456x819), never in the scaled image's pixels. Convert: full = scaled / 0.6.
- Use `zoom` on a region to read small text, toolbar icons and pin numbers
  before you click them.
- To confirm an icon before clicking, **hover it and read the tooltip** (a
  `mouse_move` followed by a `zoom` of the status bar or tooltip area). This is
  how to tell "Run simulation" from "New project" when the icons are 16px.
- Batch predictable steps with `computer_batch` and end the batch with a
  screenshot. Coordinates in a batch refer to the screenshot taken *before*
  the batch.
- **Reading a project file directly is often faster than panning around a
  canvas.** Many project formats are zips (a Proteus `.pdsprj` is a zip with
  `ROOT.DSN` inside). Copy the file to the scratchpad first and inspect the
  copy, never the original.

## 3. Clicks that can destroy work

These are the ones that actually went wrong in past sessions:

| Situation | What to do |
|---|---|
| "Save changes to current project?" appears and you didn't intend to close or replace anything | Click **Cancel**. Never Yes/No on a guess. Yes overwrites the file; No throws away unsaved work. |
| You want to close an extra window | Make sure you're closing *that* window. The title bar must show it (e.g. "Untitled - Home Page"). If there's any doubt, leave it open and tell the user. |
| Clicking a toolbar near the top-left corner | Zoom first. New, Open and Save sit next to the mode tools in many apps. |
| Editor has a *placement* mode (Proteus "Component Mode", CAD draw tools) | Switch to **Selection mode** before clicking the canvas. In placement mode, a click drops a new part. |
| Clicking on a canvas | Prefer single clicks. A drag moves parts, and a double-click opens an edit dialog. Close any dialog with **Cancel/Escape** unless you meant to change it. |
| Saving | Only when the user asked. Use Save As to a new name if the change was experimental. |
| Running or simulating | Only when asked. Some apps (Proteus demo) stop or limit simulation anyway. |

If something unexpected pops up, stop, take a screenshot and read it before
your next click. A batch keeps clicking blindly through a dialog, so keep
batches short around risky steps.

## 4. Focus problems

- `key` and `type` fail with *"Claude's own window still has keyboard
  focus"* until you click inside the target app. Click a **harmless** spot
  first, such as the title bar, a status bar or an empty panel. Never pick a
  canvas spot that could place or select something.
- Menus stay open after a failed key press. Close them by clicking the
  title bar, not the canvas.
- Elevated windows (UAC, Task Manager, installers) can't be controlled.
  Ask the user to handle them.

## 5. Interruptions

If the user interrupts or says stop, stop. Don't finish the batch "quickly".
Report the exact state you left things in: what's open, whether anything was
saved, and any dialog still showing.

## 6. Hard limits (same as everywhere)

No typing passwords, card numbers or IDs. No purchases, trades or money
moves. No accepting terms or OAuth for the user. No clicking links in emails
or chat apps (open them in a browser tool after checking the URL). Browsers
are read-only through computer use, so drive web pages with the browser tools
instead. Ask before sending, posting, deleting or submitting anything.

## App notes

- **Proteus (Labcenter)**: read `references/proteus.md` before working in it.

## Pairing with the multi-cursor overlay

If the user wants the work split across several named agents with their own
cursors, also use the `multi-cursor` skill. The agent you choose for each step
drives the real mouse pointer.
