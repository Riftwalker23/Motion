"""
Control the multi-cursor overlay.

    python cursorctl.py start [--preset proteus] [--labels "A,B"] [--count N]
    python cursorctl.py use Wiring      # Wiring agent rides the real mouse
    python cursorctl.py wander          # nobody on the real mouse
    python cursorctl.py hide | show
    python cursorctl.py stop
    python cursorctl.py status
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "cursors.py")
CONTROL = os.path.join(HERE, "control.txt")
PID_FILE = os.path.join(HERE, "overlay.pid")


def write(cmd):
    with open(CONTROL, "w", encoding="utf-8") as f:
        f.write(cmd)


def running_pid():
    try:
        pid = int(open(PID_FILE).read().strip())
    except (OSError, ValueError):
        return None
    out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                         capture_output=True, text=True).stdout
    return pid if str(pid) in out else None


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    cmd, rest = argv[0].lower(), argv[1:]

    if cmd == "start":
        pid = running_pid()
        if pid:
            print(f"already running (pid {pid})")
            return 0
        exe = sys.executable
        pyw = os.path.join(os.path.dirname(exe), "pythonw.exe")
        exe = pyw if os.path.exists(pyw) else exe
        flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | NEW_PROCESS_GROUP
        subprocess.Popen([exe, SCRIPT, *rest], creationflags=flags,
                         close_fds=True, cwd=HERE)
        for _ in range(30):
            time.sleep(0.1)
            pid = running_pid()
            if pid:
                print(f"started (pid {pid})")
                return 0
        print("started, but no pid file yet. Run 'status' in a second")
        return 0

    if cmd == "status":
        pid = running_pid()
        cur = open(CONTROL, encoding="utf-8").read().strip() if os.path.exists(CONTROL) else ""
        print(f"running (pid {pid}), control='{cur}'" if pid else "not running")
        return 0

    if cmd == "use":
        if not rest:
            print("usage: cursorctl.py use <Label>")
            return 1
        write(" ".join(rest))
    elif cmd in ("wander", "hide", "show"):
        write("@" + cmd)
    elif cmd in ("stop", "quit"):
        write("@quit")
    else:
        # bare label shortcut: cursorctl.py Wiring
        write(" ".join(argv))
    if not running_pid() and cmd not in ("stop", "quit"):
        print("note: overlay is not running. Use 'start' first")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
