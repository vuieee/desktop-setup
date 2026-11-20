#!/usr/bin/env python3
import hashlib, os, pathlib, shutil, subprocess, sys
os.environ["GDK_BACKEND"] = "wayland"
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gtk, Gdk, GLib, GtkLayerShell
import cairo

if subprocess.run(["pgrep", "-f", "wallpaper-menu.py"], capture_output=True).stdout.count(bytes([10])) > 1:
    subprocess.run(["pkill", "-f", "wallpaper-menu.py"])
    sys.exit(0)

home = pathlib.Path.home()
sub = "Candy" if (home / ".local/share/mocha-theme-bak/native").exists() else "Mono"
wdir = home / "Pictures/Wallpapers" / sub
cdir = home / ".cache/mocha-wallpapers-diag"
hc = home / ".config/hypr/hyprpaper.conf"
wdir.mkdir(parents=True, exist_ok=True)
cdir.mkdir(parents=True, exist_ok=True)

exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
walls = sorted([w for w in wdir.iterdir() if w.is_file() and w.suffix.lower() in exts], key=lambda w: w.name.lower())

if not walls:
    subprocess.run(["notify-send", "-a", "Wallpapers", "No Wallpapers Found", f"Add images to ~/Pictures/Wallpapers/{sub}"])
    sys.exit(0)

surfs = [None] * len(walls)
def get_surfs(i):
    if surfs[i] is not None:
        return surfs[i]
    w = walls[i]
    st = w.stat()
    key = hashlib.md5(f"{w}:{st.st_mtime_ns}:{st.st_size}:v2".encode()).hexdigest()
    tf = cdir / f"{key}_C.png"
    if not tf.exists():
        from PIL import Image, ImageOps
        with Image.open(w) as im:
            card = ImageOps.fit(im.convert("RGB"), (360, 480), Image.Resampling.LANCZOS)
            card.save(tf, "PNG")
    surfs[i] = cairo.ImageSurface.create_from_png(str(tf))
    return surfs[i]

def lerp(a, b, t):
    return a + (b - a) * t

class WallpaperCarousel(Gtk.Window):
    def __init__(self):
        super().__init__(title="mocha-wallpaper")
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_namespace(self, "mocha-wallpaper")
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.EXCLUSIVE)
        GtkLayerShell.set_exclusive_zone(self, -1)
        for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM, GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
            GtkLayerShell.set_anchor(self, edge, True)
        self.set_decorated(False)
        self.set_app_paintable(True)
        visual = self.get_screen().get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.idx = 0
        if hc.exists():
            cur_n = next((l.split("=",1)[1].strip().rsplit("/",1)[-1] for l in hc.read_text().splitlines() if l.strip().startswith("path =")), "")
            self.idx = next((i for i,w in enumerate(walls) if w.name == cur_n), 0)
        self.anim_offset = 0.0
        self.open_t = 0.0
        self.closing = False
        self.hitboxes = []
        self.da = Gtk.DrawingArea()
        self.da.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.da.connect("draw", self.on_draw)
        self.da.connect("button-press-event", self.on_click)
        self.add(self.da)
        self.connect("key-press-event", self.on_key)
        self.connect("destroy", Gtk.main_quit)
        GLib.timeout_add(8, self.on_tick)

    def start_close(self):
        Gtk.main_quit()

    def on_tick(self):
        dirty = False
        if self.open_t < 1.0:
            self.open_t = min(1.0, self.open_t + 0.065)
            dirty = True
        if abs(self.anim_offset) > 0.002:
            self.anim_offset *= 0.84
            if abs(self.anim_offset) <= 0.002:
                self.anim_offset = 0.0
            dirty = True
        if dirty:
            self.da.queue_draw()
        return True

    def step(self, delta):
        self.idx = (self.idx + delta) % len(walls)
        self.anim_offset += delta
        self.da.queue_draw()

    def apply_current(self):
        chosen = walls[self.idx]
        hc.write_text(chr(10).join(["splash = false", "wallpaper {", "    monitor =", f"    path = ~/Pictures/Wallpapers/{sub}/{chosen.name}", "    fit_mode = cover", "}", ""]))
        if subprocess.run(["pgrep", "-x", "hyprpaper"], stdout=subprocess.DEVNULL).returncode == 0:
            subprocess.run(["hyprctl", "hyprpaper", "wallpaper", f",{chosen}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["hyprpaper"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        subprocess.run(["notify-send", "-a", "Wallpapers", "Wallpaper Applied", chosen.stem])
        Gtk.main_quit()

    def on_key(self, widget, event):
        kv = event.keyval
        if kv in (Gdk.KEY_Escape, Gdk.KEY_q, Gdk.KEY_Q):
            self.start_close()
        elif kv in (Gdk.KEY_Left, Gdk.KEY_a, Gdk.KEY_A, Gdk.KEY_h, Gdk.KEY_H):
            self.step(-1)
        elif kv in (Gdk.KEY_Right, Gdk.KEY_d, Gdk.KEY_D, Gdk.KEY_l, Gdk.KEY_L):
            self.step(1)
        elif kv in (Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_space):
            self.apply_current()

    def on_click(self, widget, event):
        for slot, x0, x1, y0, y1 in self.hitboxes:
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                if slot == 0:
                    self.apply_current()
                else:
                    self.step(slot)
                return
        self.start_close()

    def slot_geom(self, pos):
        anchors = [
            (-3.0, -475.0, 95.0,  190.0, 20.0, 0.96),
            (-2.0, -455.0, 155.0, 305.0, 34.0, 0.55),
            (-1.0, -265.0, 200.0, 385.0, 42.0, 0.30),
            ( 0.0,    0.0, 290.0, 470.0, 52.0, 0.00),
            ( 1.0,  265.0, 200.0, 385.0, 42.0, 0.30),
            ( 2.0,  455.0, 155.0, 305.0, 34.0, 0.55),
            ( 3.0,  475.0, 95.0,  190.0, 20.0, 0.96),
        ]
        if pos <= anchors[0][0]:
            return anchors[0][1:]
        if pos >= anchors[-1][0]:
            return anchors[-1][1:]
        for i in range(len(anchors) - 1):
            p0 = anchors[i][0]
            p1 = anchors[i + 1][0]
            if p0 <= pos <= p1:
                t = (pos - p0) / (p1 - p0)
                return tuple(lerp(anchors[i][j], anchors[i + 1][j], t) for j in range(1, 6))
        return anchors[3][1:]

    def on_draw(self, widget, cr):
        w = widget.get_allocated_width()
        h = widget.get_allocated_height()
        ease = 1.0 - (1.0 - self.open_t) ** 5
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.55 * ease)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        cx, cy = w / 2.0, h / 2.0 - 12
        cr.translate(cx, cy + (1.0 - ease) * 28.0)
        sc = 0.80 + 0.20 * ease
        cr.scale(sc, sc)
        cr.translate(-cx, -cy)
        self.hitboxes = []
        render_slots = sorted([-3, -2, -1, 0, 1, 2, 3], key=lambda s: -abs(s + self.anim_offset))

        for slot in render_slots:
            pos = slot + self.anim_offset
            if abs(pos) > 2.85:
                continue
            dx, cw, ch, slant, dim = self.slot_geom(pos)
            wi = (self.idx + slot) % len(walls)
            surf = get_surfs(wi)
            x = cx + dx - cw / 2.0
            y = cy - ch / 2.0
            if abs(slot) <= 2:
                self.hitboxes.append((slot, x, x + cw + slant, y, y + ch))

            cr.save()
            cr.move_to(x + slant, y)
            cr.line_to(x + cw + slant, y)
            cr.line_to(x + cw, y + ch)
            cr.line_to(x, y + ch)
            cr.close_path()
            cr.clip()

            iw, ih = 360.0, 480.0
            tw = cw + slant
            scale = max(tw / iw, ch / ih)
            sw, sh = iw * scale, ih * scale
            ox = x + (tw - sw) / 2.0
            oy = y + (ch - sh) / 2.0
            cr.translate(ox, oy)
            cr.scale(scale, scale)
            cr.set_source_surface(surf, 0, 0)
            cr.get_source().set_filter(cairo.FILTER_FAST)
            cr.paint_with_alpha(ease)
            if dim > 0.01:
                cr.set_source_rgba(0.0, 0.0, 0.0, dim * ease)
                cr.paint()
            cr.restore()

            cr.save()
            cr.move_to(x + slant, y)
            cr.line_to(x + cw + slant, y)
            cr.line_to(x + cw, y + ch)
            cr.line_to(x, y + ch)
            cr.close_path()
            nat = (home / ".local/share/mocha-theme-bak/native").exists()
            focus = max(0.0, 1.0 - abs(pos))
            if nat:
                cr.set_source_rgba(lerp(0.28, 0.58, focus), lerp(0.33, 0.64, focus), lerp(0.41, 0.72, focus), ease)
                cr.set_line_width(lerp(1.0, 1.5, focus))
            else:
                shade = lerp(0.08, 1.0, focus)
                cr.set_source_rgba(shade, shade, shade, ease)
                cr.set_line_width(lerp(1.5, 2.5, focus))
            cr.stroke()
            cr.restore()

        nat = (home / ".local/share/mocha-theme-bak/native").exists()
        st_txt = (home / ".config/waybar/style.css").read_text()
        lt = any(x in st_txt for x in ("#ffffff", "#f8fafc"))
        rd_on = "rounding       = 6," in (home / ".config/hypr/hyprland.lua").read_text()
        rad = 6.0 if (nat and rd_on) else 0.0
        label = f"{walls[self.idx].stem}   ({self.idx + 1}/{len(walls)})"
        cr.select_font_face("JetBrains Mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(14)
        ext = cr.text_extents(label)
        bx = cx - ext.width / 2.0 - 16
        by = cy + 470 / 2.0 + 22
        bw = ext.width + 32
        bh = 32
        def rrect(x0, y0, w0, h0, r0):
            if r0 <= 0:
                cr.rectangle(x0, y0, w0, h0)
                return
            import math
            cr.new_sub_path()
            cr.arc(x0 + w0 - r0, y0 + r0, r0, -math.pi/2, 0)
            cr.arc(x0 + w0 - r0, y0 + h0 - r0, r0, 0, math.pi/2)
            cr.arc(x0 + r0, y0 + h0 - r0, r0, math.pi/2, math.pi)
            cr.arc(x0 + r0, y0 + r0, r0, math.pi, 3*math.pi/2)
            cr.close_path()
        bg_c = ((0.973, 0.980, 0.988) if lt else (0.118, 0.133, 0.176)) if nat else ((1.0, 1.0, 1.0) if lt else (0.0, 0.0, 0.0))
        bd_c = ((0.392, 0.455, 0.545) if lt else (0.580, 0.639, 0.722)) if nat else ((0.0, 0.0, 0.0) if lt else (1.0, 1.0, 1.0))
        fg_c = ((0.059, 0.090, 0.165) if lt else (0.945, 0.961, 0.976)) if nat else ((0.0, 0.0, 0.0) if lt else (1.0, 1.0, 1.0))
        cr.set_source_rgba(*bg_c, 1.0)
        rrect(bx, by, bw, bh, rad)
        cr.fill()
        cr.set_source_rgba(*bd_c, 1.0)
        cr.set_line_width(1.0 if nat else 2.0)
        rrect(bx, by, bw, bh, rad)
        cr.stroke()
        cr.set_source_rgba(*fg_c, 1.0)
        cr.move_to(cx - ext.width / 2.0, by + 21)
        cr.show_text(label)

win = WallpaperCarousel()
for off in (0, -1, 1):
    get_surfs((win.idx + off) % len(walls))
pending = [i for i in range(len(walls)) if surfs[i] is None]
def warm_next():
    if win.open_t < 1.0:
        return True
    if pending:
        get_surfs(pending.pop(0))
        win.da.queue_draw()
        return True
    return False
GLib.timeout_add(20, warm_next)
win.show_all()
Gtk.main()
