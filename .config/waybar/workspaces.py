import json
import pathlib
#!/usr/bin/env python3
import glob, json, os, select, socket, subprocess, sys, time

PERSISTENT = 5
FRAME = 0.016
VIS_SPEED = 0.22
HL_SPEED = 0.30
COUNT_EVENTS = {"openwindow", "closewindow", "movewindow", "movewindowv2", "createworkspacev2", "destroyworkspacev2"}

def event_socket_path():
    base = os.path.join(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"), "hypr")
    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    if sig:
        return os.path.join(base, sig, ".socket2.sock")
    dirs = sorted(glob.glob(os.path.join(base, "*")), key=os.path.getmtime)
    if not dirs:
        sys.exit(1)
    return os.path.join(dirs[-1], ".socket2.sock")

def hctl(*args):
    try:
        out = subprocess.run(["hyprctl", "-j", *args], capture_output=True, text=True, timeout=2).stdout
        return json.loads(out) if out.strip() else None
    except Exception:
        return None

def fetch_counts():
    workspaces = hctl("workspaces") or []
    return {w["id"] for w in workspaces if w.get("id", 0) > 0 and w.get("windows", 0) > 0}

def fetch_active():
    a = (hctl("activeworkspace") or {}).get("id")
    return a if isinstance(a, int) and a > 0 else None

def approach(cur, target, speed):
    d = target - cur
    if abs(d) < 0.01:
        return target
    step = d * speed
    if abs(step) < 0.01:
        step = 0.01 if d > 0 else -0.01
    return cur + step

class Strip:
    def __init__(self):
        self.counts = set()
        self.active = None
        self.vis = {}
        self.hl = {}
        self.started = False

    def target_ids(self):
        ids = set(range(1, PERSISTENT + 1)) | self.counts
        if self.active:
            ids.add(self.active)
        return ids

    def sync(self):
        for i in self.target_ids():
            if i not in self.vis:
                first = not self.started
                self.vis[i] = 1.0 if first else 0.0
                self.hl[i] = 1.0 if (first and i == self.active) else 0.0
        self.started = True

    def animating(self):
        ids = self.target_ids()
        for i in self.vis:
            if self.vis[i] != (1.0 if i in ids else 0.0):
                return True
            if self.hl.get(i, 0.0) != (1.0 if i == self.active else 0.0):
                return True
        return False

    def tick(self):
        ids = self.target_ids()
        for i in list(self.vis):
            tv = 1.0 if i in ids else 0.0
            th = 1.0 if i == self.active else 0.0
            self.vis[i] = approach(self.vis[i], tv, VIS_SPEED)
            self.hl[i] = approach(self.hl.get(i, 0.0), th, HL_SPEED)
            if tv == 0.0 and self.vis[i] <= 0.0 and self.hl[i] <= 0.0:
                del self.vis[i]
                self.hl.pop(i, None)

    def render(self):
        parts = []
        for i in sorted(self.vis):
            v = self.vis[i]
            h = self.hl.get(i, 0.0)
            if v <= 0.0 and h <= 0.0:
                continue
            st = (pathlib.Path.home()/".config/waybar/style.css").read_text()
            lt = "rgba(255, 255, 255, 0.72)" in st or "background: #ffffff;" in st.split("}")[0]
            gray = int(95 + 160 * h) if lt else int(160 * (1.0 - h))
            fg = f"#{gray:02x}{gray:02x}{gray:02x}"
            pill = "#000000" if lt else "#ffffff"
            alpha = max(1, min(100, int(v * 100)))
            attrs = f'foreground="{fg}" alpha="{alpha}%"'
            if h > 0.01:
                bg_alpha = max(1, min(100, int(h * v * 100)))
                attrs += f' background="{pill}" bgalpha="{bg_alpha}%"'
            parts.append(f"<span {attrs}> {i} </span>")
        vert=json.loads((pathlib.Path.home()/".config/waybar/config.jsonc").read_text()).get("position") in ("left","right")
        return chr(10).join(parts) if vert else "".join(parts)

def main():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(event_socket_path())
    except OSError:
        sys.exit(1)

    strip = Strip()
    strip.counts = fetch_counts()
    strip.active = fetch_active()
    strip.sync()

    last_out = None
    buf = b""
    need_counts_at = None
    last_tick = time.monotonic()

    def emit():
        nonlocal last_out
        out = strip.render()
        if out != last_out:
            print(json.dumps({"text": out, "tooltip": False}), flush=True)
            last_out = out

    emit()
    while True:
        now = time.monotonic()
        anim = strip.animating()
        if anim:
            timeout = max(0.0, FRAME - (now - last_tick))
        elif need_counts_at is not None:
            timeout = max(0.0, need_counts_at - now)
        else:
            timeout = 5.0

        ready, _, _ = select.select([sock], [], [], timeout)
        now = time.monotonic()

        if ready:
            data = sock.recv(65536)
            if not data:
                break
            buf += data
            *lines, buf = buf.split(bytes((10,)))
            for raw in lines:
                name, _, arg = raw.decode(errors="ignore").partition(">>")
                if name == "workspacev2":
                    try:
                        wid = int(arg.split(",")[0])
                    except ValueError:
                        continue
                    if wid > 0:
                        strip.active = wid
                elif name == "focusedmonv2":
                    try:
                        wid = int(arg.split(",")[0][-1])
                    except ValueError:
                        continue
                    if wid > 0:
                        strip.active = wid
                elif name == "destroyworkspacev2":
                    try:
                        wid = int(arg.split(",")[0])
                        strip.counts.discard(wid)
                    except ValueError:
                        pass
                    need_counts_at = now + 0.015
                elif name in COUNT_EVENTS:
                    need_counts_at = now + 0.015
            strip.sync()

        if need_counts_at is not None and now >= need_counts_at:
            strip.counts = fetch_counts()
            need_counts_at = None
            strip.sync()
        elif not ready and not anim and need_counts_at is None:
            strip.counts = fetch_counts()
            active = fetch_active()
            if active:
                strip.active = active
            strip.sync()

        now = time.monotonic()
        if now - last_tick >= FRAME:
            strip.tick()
            last_tick = now
        emit()

if __name__ == "__main__":
    main()
