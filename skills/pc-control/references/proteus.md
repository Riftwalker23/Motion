# Proteus 9 (Labcenter) notes for this PC

Install: `C:\Program Files\Labcenter Electronics\Proteus 9 Demonstration\BIN\PDS.exe`
Start-menu name for `request_access`: **Proteus 9 Demonstration**
Process name: `PDS.exe`. Check `tasklist //FI "IMAGENAME eq PDS.exe"` before launching.

The user's projects usually live in `%USERPROFILE%\Downloads\*.pdsprj`
(e.g. `Smart_Parking_System.pdsprj`, a 74-series digital parking counter:
74LS193 counter, 74LS85 comparator, 74LS283 adder, 74HC157 mux, 7447 →
7-segment, 555 debouncers, "FULL" red LED).

## It's the Demonstration edition

- It may refuse or quickly stop simulating designs that aren't Labcenter
  samples, and saving can be restricted. If a simulation stops by itself,
  this is the likely cause. Tell the user instead of retrying.
- The "You have been evaluating Proteus for N days" banner is normal.

## Screen layout (maximised, 1456x819 screenshot frame)

| Thing | Approx. location |
|---|---|
| Mode toolbar (left column) | x≈9. **Selection mode** is the top arrow (≈9,67), **Component mode** is just below it |
| Device list ("Devices" panel) | x 20–185, y 210–570 |
| Overview mini-map | top-left, ≈(105,130) |
| Simulation controls | bottom-left: Play ≈(13,780), Step ≈(27,780), Pause ≈(41,780), Stop ≈(54,780) |
| Status bar text | y≈781, x 160+. Shows the tooltip of whatever you hover |
| New / Open / Save icons | top toolbar, x≈13–55, y≈48. **Easy to hit by mistake** |

Positions shift if panels are resized. Always confirm with a zoom or a
hover-tooltip before clicking a small icon.

## Safe ways to interact

- Enter **Selection mode** first. In Component mode a canvas click places
  the highlighted device (the pink outline you see following the mouse is a
  part waiting to be placed).
- Hovering a pin or part is harmless and shows its name in the status bar.
- A single click selects (red highlight). A double-click opens *Edit Component*,
  so close it with **Cancel** unless the user asked for a value change.
- Zoom: the **mouse wheel does not reliably zoom around the pointer** here.
  It tends to land on empty sheet. Use **View → Zoom To View Entire Sheet**
  (menu item ≈(100,185) once the View menu at ≈(50,19) is open) to recover,
  and **View → Zoom To Area** for a precise zoom. F6/F7/F8 work only once
  Proteus has keyboard focus.
- If Proteus isn't in front, don't relaunch it. Ask the user to click it on
  the taskbar (taskbar clicks need a "File Explorer" grant, which they may
  decline).
- Don't drag on the canvas unless you mean to move parts or draw a wire.

## Dialogs

- "Save changes to current project?" → **Cancel** unless the user asked to
  close or replace the project. (The X at the far top-right, ≈1442,6, closes
  the whole Proteus window, not a tab.)
