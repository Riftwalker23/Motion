"""
Multi-cursor overlay: draws several labelled "agent" cursors that move,
click and drag wires across the screen. It's purely visual. The window is
transparent and click-through, so it never touches the app underneath.

One agent can be put onto the REAL mouse pointer (via the control file), so
real actions look like that agent did them while the rest keep wandering.

Hotkeys (global):  F9 = hide/show   F10 = quit

Usage:
    pythonw cursors.py                         # 8 agents, whole-screen preset
    pythonw cursors.py --preset proteus        # zones tuned for Proteus
    pythonw cursors.py --labels "Wiring,Parts,QA" --count 3

Control: use cursorctl.py, or write one line into control.txt next to this
script:
    <Label>     that agent rides the real mouse pointer
    @wander     everybody wanders (no one on the real mouse)
    @hide / @show / @quit
"""
import argparse
import ctypes
import math
import os
import random
import time
import tkinter as tk

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
CONTROL_FILE = os.path.join(HERE, "control.txt")
PID_FILE = os.path.join(HERE, "overlay.pid")
KEY = "#0a0b0c"  # colour treated as fully transparent

PALETTE = ["#2e9e5b", "#c8963e", "#3b4a63", "#7b4fd6",
           "#d6457d", "#2f7fd8", "#d9534f", "#3aa6a0"]

PRESETS = {
    # area = where agents wander (fractions of the screen)
    # extras = {label: (probability, zone-or-point)} special haunts
    "screen": {
        "labels": ["Planner", "Builder", "QA", "Research",
                   "Design", "Debug", "Writer", "Ops"],
        "area": (0.05, 0.08, 0.95, 0.90),
        "extras": {},
    },
    "proteus": {
        "labels": ["Wiring", "Parts", "QA", "Simulation",
                   "Timing", "Display", "Power", "Debug"],
        "area": (0.15, 0.10, 0.97, 0.92),
        "extras": {
            "Parts": (0.4, (0.015, 0.27, 0.12, 0.68)),   # device list
            "Simulation": (0.15, (0.009, 0.954)),        # play button
        },
    },
}

VK_F9, VK_F10, VK_LBUTTON = 0x78, 0x79, 0x01


class _POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def real_mouse():
    p = _POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(p))
    return p.x, p.y


def ease(t):
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def rounded_rect(cv, x0, y0, x1, y1, r, **kw):
    pts = [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r, x1, y1 - r, x1, y1,
           x1 - r, y1, x0 + r, y1, x0, y1, x0, y1 - r, x0, y0 + r, x0, y0]
    return cv.create_polygon(pts, smooth=True, **kw)


class Overlay:
    def __init__(self, labels, preset):
        self.area = preset["area"]
        self.extras = preset["extras"]
        self.root = tk.Tk()
        self.W = self.root.winfo_screenwidth()
        self.H = self.root.winfo_screenheight()
        self.s = max(1.0, self.H / 1080)

        self.root.overrideredirect(True)
        self.root.geometry(f"{self.W}x{self.H}+0+0")
        self.root.configure(bg=KEY)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", KEY)
        self.cv = tk.Canvas(self.root, width=self.W, height=self.H,
                            bg=KEY, highlightthickness=0, bd=0)
        self.cv.pack()
        self.root.update_idletasks()
        self._make_click_through()

        self.effects = []
        self.hidden = False
        self.keys_down = set()
        self.active = ""
        self.control_seen = None
        self.control_timer = 0.0
        self.mouse_was_down = False
        self.agents = [Agent(self, i, lab, PALETTE[i % len(PALETTE)])
                       for i, lab in enumerate(labels)]

        # fresh start: forget any stale command, remember our pid
        self._write_control("@wander")
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        self.last = time.perf_counter()
        self.root.after(16, self.tick)

    def _write_control(self, text):
        try:
            with open(CONTROL_FILE, "w", encoding="utf-8") as f:
                f.write(text)
        except OSError:
            pass

    def _make_click_through(self):
        u = ctypes.windll.user32
        hwnd = u.GetParent(self.root.winfo_id()) or self.root.winfo_id()
        style = u.GetWindowLongW(hwnd, -20)
        # LAYERED | TRANSPARENT | TOOLWINDOW | TOPMOST | NOACTIVATE
        style |= 0x80000 | 0x20 | 0x80 | 0x8 | 0x08000000
        u.SetWindowLongW(hwnd, -20, style)

    def rand_in(self, box):
        x0, y0, x1, y1 = box
        return (random.uniform(x0, x1) * self.W, random.uniform(y0, y1) * self.H)

    def clamp(self, x, y):
        x0, y0, x1, y1 = self.area
        return (min(max(x, x0 * self.W), x1 * self.W),
                min(max(y, y0 * self.H), y1 * self.H))

    def _pressed(self, vk):
        down = bool(ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000)
        was = vk in self.keys_down
        (self.keys_down.add if down else self.keys_down.discard)(vk)
        return down and not was

    def set_hidden(self, hidden):
        self.hidden = hidden
        self.cv.itemconfigure("all", state="hidden" if hidden else "normal")

    def quit(self):
        try:
            os.remove(PID_FILE)
        except OSError:
            pass
        self.root.destroy()

    def read_control(self):
        try:
            with open(CONTROL_FILE, encoding="utf-8") as f:
                text = f.read().strip()
        except OSError:
            return True
        if text == self.control_seen:
            return True
        self.control_seen = text
        cmd = text.lower()
        if cmd == "@quit":
            self.quit()
            return False
        if cmd == "@hide":
            self.set_hidden(True)
        elif cmd == "@show":
            self.set_hidden(False)
        elif cmd in ("", "@wander"):
            self.active = ""
        else:
            self.active = text
        return True

    def tick(self):
        now = time.perf_counter()
        dt = min(now - self.last, 0.05)
        self.last = now

        if self._pressed(VK_F10):
            self.quit()
            return
        if self._pressed(VK_F9):
            self.set_hidden(not self.hidden)

        self.control_timer -= dt
        if self.control_timer <= 0:
            self.control_timer = 0.15
            if not self.read_control():
                return

        if not self.hidden:
            down = bool(ctypes.windll.user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000)
            if down and not self.mouse_was_down and self.active:
                for a in self.agents:
                    if a.label.lower() == self.active.lower():
                        mx, my = real_mouse()
                        self.ripple(mx, my, a.color)
            self.mouse_was_down = down
            for a in self.agents:
                a.update(dt)
            self.effects = [e for e in self.effects if e(dt)]
            self.root.attributes("-topmost", True)
        self.root.after(16, self.tick)

    def ripple(self, x, y, color):
        s = self.s
        oid = self.cv.create_oval(x, y, x, y, outline=color, width=2 * s)
        st = {"t": 0.0}

        def step(dt):
            st["t"] += dt / 0.4
            if st["t"] >= 1:
                self.cv.delete(oid)
                return False
            r = (4 + 16 * ease(st["t"])) * s
            self.cv.coords(oid, x - r, y - r, x + r, y + r)
            return True
        self.effects.append(step)

    def later_delete(self, ids, delay):
        st = {"t": 0.0}

        def step(dt):
            st["t"] += dt
            if st["t"] >= delay:
                for i in ids:
                    self.cv.delete(i)
                return False
            return True
        self.effects.append(step)


class Agent:
    def __init__(self, ov, idx, label, color):
        self.ov, self.cv, self.s = ov, ov.cv, ov.s
        self.label, self.color = label, color
        self.tag = f"agent{idx}"
        s = self.s

        self.x = random.uniform(0.3, 0.8) * ov.W   # fly in from below
        self.y = ov.H + 40 * s
        arrow = [(0, 0), (0, 18), (4.6, 13.8), (7.8, 20.6), (10.8, 19.2),
                 (7.8, 12.6), (13.4, 12.6)]
        pts = []
        for px, py in arrow:
            pts += [self.x + px * s * 1.15, self.y + py * s * 1.15]
        self.cv.create_polygon(pts, fill=color, outline="white",
                               width=1.6 * s, tags=self.tag)
        tid = self.cv.create_text(self.x + 15 * s, self.y + 25 * s, text=label,
                                  anchor="nw", fill="white",
                                  font=("Segoe UI Semibold", -int(12 * s)),
                                  tags=self.tag)
        bx0, by0, bx1, by1 = self.cv.bbox(tid)
        rid = rounded_rect(self.cv, bx0 - 6 * s, by0 - 2.5 * s, bx1 + 6 * s,
                           by1 + 2.5 * s, 6 * s, fill=color, outline="",
                           tags=self.tag)
        self.cv.tag_raise(tid, rid)

        self.wait = idx * random.uniform(0.25, 0.45)
        self.mode = "wait"
        self.wire = None
        self.queue = []

    def move_to(self, x, y, speed=1.0):
        self.sx, self.sy = self.x, self.y
        self.tx, self.ty = x, y
        dist = math.hypot(x - self.x, y - self.y)
        bend = random.uniform(-0.25, 0.25) * dist
        mx, my = (self.sx + x) / 2, (self.sy + y) / 2
        nx, ny = -(y - self.sy), x - self.sx
        n = math.hypot(nx, ny) or 1
        self.cx, self.cy = mx + nx / n * bend, my + ny / n * bend
        self.dur = max(0.25, (0.35 + dist / (1100 * self.s)) / speed)
        self.t = 0.0
        self.mode = "move"

    def set_pos(self, x, y):
        self.cv.move(self.tag, x - self.x, y - self.y)
        self.x, self.y = x, y

    def pick_target(self):
        ov = self.ov
        extra = ov.extras.get(self.label)
        if extra and random.random() < extra[0]:
            zone = extra[1]
            pt = ov.rand_in(zone) if len(zone) == 4 else (zone[0] * ov.W, zone[1] * ov.H)
            return pt, "click"
        if random.random() < 0.65 and self.mode != "wait":
            target = ov.clamp(self.x + random.uniform(-260, 260) * self.s,
                              self.y + random.uniform(-180, 180) * self.s)
        else:
            target = ov.rand_in(ov.area)
        action = random.choices(["click", "wire", "dwell", "scan"],
                                [0.38, 0.27, 0.2, 0.15])[0]
        if self.label.lower() == "wiring" and random.random() < 0.5:
            action = "wire"
        return target, action

    def start_wire(self):
        s = self.s
        x1, y1 = self.ov.clamp(self.x + random.choice([-1, 1]) * random.uniform(60, 240) * s,
                               self.y + random.choice([-1, 1]) * random.uniform(40, 170) * s)
        self.ov.ripple(self.x, self.y, self.color)
        dot = self.cv.create_oval(self.x - 3 * s, self.y - 3 * s, self.x + 3 * s,
                                  self.y + 3 * s, fill=self.color, outline="")
        line = self.cv.create_line(self.x, self.y, self.x, self.y,
                                   fill=self.color, width=2.6 * s)
        self.cv.tag_raise(self.tag)
        self.wire = {"line": line, "dot": dot, "pts": [self.x, self.y]}
        self.queue = [(x1, self.y), (x1, y1)]  # L-shaped run like a real net
        self.next_waypoint()

    def next_waypoint(self):
        if self.queue:
            x, y = self.queue.pop(0)
            self.move_to(x, y, speed=0.55)
            self.mode = "wiring"
            return
        s, w = self.s, self.wire
        end = self.cv.create_oval(self.x - 3 * s, self.y - 3 * s, self.x + 3 * s,
                                  self.y + 3 * s, fill=self.color, outline="")
        self.ov.ripple(self.x, self.y, self.color)
        self.ov.later_delete([w["line"], w["dot"], end], random.uniform(1.8, 3.6))
        self.wire = None
        self.begin_dwell(random.uniform(0.2, 0.6))

    def begin_dwell(self, secs):
        self.mode = "dwell"
        self.wait = secs

    def update(self, dt):
        # --- riding the real mouse -------------------------------------------
        if self.ov.active and self.ov.active.lower() == self.label.lower():
            if self.wire:
                self.ov.later_delete([self.wire["line"], self.wire["dot"]], 0)
                self.wire, self.queue = None, []
            mx, my = real_mouse()
            # always glide: real pointer jumps (scripted moves) still look smooth
            k = min(1.0, dt * 16)
            self.set_pos(self.x + (mx - self.x) * k, self.y + (my - self.y) * k)
            self.mode = "follow"
            return
        if self.mode == "follow":
            self.begin_dwell(random.uniform(0.2, 0.6))

        # --- wandering ------------------------------------------------------
        if self.mode in ("wait", "dwell"):
            self.wait -= dt
            if self.mode == "dwell":
                self.set_pos(self.x + random.uniform(-0.4, 0.4) * self.s,
                             self.y + random.uniform(-0.4, 0.4) * self.s)
            if self.wait <= 0:
                (tx, ty), self.action = self.pick_target()
                self.move_to(tx, ty)
            return

        self.t += dt / self.dur
        t = min(self.t, 1.0)
        e = ease(t)
        if self.mode == "wiring":
            x = self.sx + (self.tx - self.sx) * e
            y = self.sy + (self.ty - self.sy) * e
        else:
            u = 1 - e
            x = u * u * self.sx + 2 * u * e * self.cx + e * e * self.tx
            y = u * u * self.sy + 2 * u * e * self.cy + e * e * self.ty
        self.set_pos(x, y)
        if self.wire:
            self.cv.coords(self.wire["line"], *(self.wire["pts"] + [x, y]))

        if t >= 1.0:
            if self.mode == "wiring":
                self.wire["pts"] += [self.x, self.y]
                self.next_waypoint()
                return
            a = self.action
            if a == "click":
                self.ov.ripple(self.x, self.y, self.color)
                if random.random() < 0.3:
                    self.ov.ripple(self.x, self.y, self.color)
                self.begin_dwell(random.uniform(0.35, 1.2))
            elif a == "wire":
                self.start_wire()
            elif a == "scan":
                self.action = "dwell"
                x, y = self.ov.clamp(self.x + random.uniform(-70, 70) * self.s,
                                     self.y + random.uniform(-40, 40) * self.s)
                self.move_to(x, y, speed=1.6)
            else:
                self.begin_dwell(random.uniform(0.5, 1.6))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preset", choices=sorted(PRESETS), default="screen")
    ap.add_argument("--labels", help='comma-separated agent names, e.g. "Wiring,Parts,QA"')
    ap.add_argument("--count", type=int, help="number of agents (1-16)")
    ap.add_argument("count_pos", nargs="?", type=int, help=argparse.SUPPRESS)
    args = ap.parse_args()

    preset = PRESETS[args.preset]
    labels = ([x.strip() for x in args.labels.split(",") if x.strip()]
              if args.labels else list(preset["labels"]))
    n = args.count or args.count_pos or len(labels)
    n = max(1, min(16, n))
    labels = [labels[i % len(labels)] + ("" if i < len(labels) else f" {i // len(labels) + 1}")
              for i in range(n)]
    Overlay(labels, preset).root.mainloop()


if __name__ == "__main__":
    main()
