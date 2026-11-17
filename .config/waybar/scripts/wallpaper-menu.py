#!/usr/bin/env python3
import hashlib, os, pathlib, shutil, subprocess, sys
os.environ["GDK_BACKEND"] = "wayland"
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import cairo
from PIL import Image, ImageOps

if subprocess.run(["pgrep", "-f", "wallpaper-menu.py"], capture_output=True).stdout.count(bytes([10])) > 1:
    subprocess.run(["pkill", "-f", "wallpaper-menu.py"])
    sys.exit(0)

home = pathlib.Path.home()
wdir = home / "wallpapers"
cdir = home / ".cache/mocha-wallpapers-diag"
target = home / "Pictures/wallpaper.png"
hc = home / ".config/hypr/hyprpaper.conf"
wdir.mkdir(exist_ok=True)
cdir.mkdir(parents=True, exist_ok=True)

exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
walls = sorted([w for w in wdir.iterdir() if w.is_file() and w.suffix.lower() in exts], key=lambda w: w.name.lower())

if not walls:
    subprocess.run(["notify-send", "-a", "Wallpapers", "No Wallpapers Found", "Add images to ~/wallpapers"])
    sys.exit(0)

pixbufs = []
for w in walls:
    st = w.stat()
    key = hashlib.md5(f"{w}:{st.st_mtime_ns}:{st.st_size}:diag".encode()).hexdigest()
    tf = cdir / f"{key}.png"
    if not tf.exists():
        with Image.open(w) as im:
            card = ImageOps.fit(im.convert("RGB"), (360, 480), Image.Resampling.LANCZOS)
            card.save(tf, "PNG")
    pixbufs.append(GdkPixbuf.Pixbuf.new_from_file(str(tf)))

def lerp(a, b, t):
    return a + (b - a) * t

class WallpaperCarousel(Gtk.Window):
    def __init__(self):
        super().__init__(title="mocha-wallpaper")
        self.set_decorated(False)
        self.set_app_paintable(True)
        visual = self.get_screen().get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.idx = 0
        self.anim_offset = 0.0
        self.open_t = 0.0
        self.hitboxes = []
        self.da = Gtk.DrawingArea()
        self.da.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.da.connect("draw", self.on_draw)
        self.da.connect("button-press-event", self.on_click)
        self.add(self.da)
        self.connect("key-press-event", self.on_key)
        self.connect("destroy", Gtk.main_quit)
        GLib.timeout_add(16, self.on_tick)

    def on_tick(self):
        dirty = False
        if self.open_t < 1.0:
            self.open_t = min(1.0, self.open_t + 0.14)
            dirty = True
        if abs(self.anim_offset) > 0.002:
            self.anim_offset *= 0.72
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
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(chosen, target)
        hc.write_text(chr(10).join(["splash = false", "wallpaper {", "    monitor =", "    path = ~/Pictures/wallpaper.png", "    fit_mode = cover", "}", ""]))
        if subprocess.run(["pgrep", "-x", "hyprpaper"], stdout=subprocess.DEVNULL).returncode == 0:
            subprocess.run(["hyprctl", "hyprpaper", "wallpaper", f",{target}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["hyprpaper"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        subprocess.run(["notify-send", "-a", "Wallpapers", "Wallpaper Applied", chosen.stem])
        Gtk.main_quit()

    def on_key(self, widget, event):
        kv = event.keyval
        if kv in (Gdk.KEY_Escape, Gdk.KEY_q, Gdk.KEY_Q):
            Gtk.main_quit()
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
        Gtk.main_quit()

    def slot_geom(self, pos):
        anchors = [
            (-3.0, -580.0, 120.0, 240.0, 26.0, 0.75),
            (-2.0, -455.0, 155.0, 305.0, 34.0, 0.55),
            (-1.0, -265.0, 200.0, 385.0, 42.0, 0.30),
            ( 0.0,    0.0, 290.0, 470.0, 52.0, 0.00),
            ( 1.0,  265.0, 200.0, 385.0, 42.0, 0.30),
            ( 2.0,  455.0, 155.0, 305.0, 34.0, 0.55),
            ( 3.0,  580.0, 120.0, 240.0, 26.0, 0.75),
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
        ease = 1.0 - (1.0 - self.open_t) ** 3
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.55 * ease)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        cx, cy = w / 2.0, h / 2.0 - 12
        cr.translate(cx, cy)
        sc = 0.88 + 0.12 * ease
        cr.scale(sc, sc)
        cr.translate(-cx, -cy)
        self.hitboxes = []
        render_slots = sorted([-3, -2, -1, 0, 1, 2, 3], key=lambda s: -abs(s + self.anim_offset))

        for slot in render_slots:
            pos = slot + self.anim_offset
            if abs(pos) > 2.6:
                continue
            dx, cw, ch, slant, dim = self.slot_geom(pos)
            wi = (self.idx + slot) % len(walls)
            pb = pixbufs[wi]
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

            iw, ih = pb.get_width(), pb.get_height()
            tw = cw + slant
            scale = max(tw / iw, ch / ih)
            sw, sh = iw * scale, ih * scale
            ox = x + (tw - sw) / 2.0
            oy = y + (ch - sh) / 2.0
            cr.translate(ox, oy)
            cr.scale(scale, scale)
            Gdk.cairo_set_source_pixbuf(cr, pb, 0, 0)
            cr.paint()
            if dim > 0.01:
                cr.set_source_rgba(0.0, 0.0, 0.0, dim)
                cr.paint()
            cr.restore()

            cr.save()
            cr.move_to(x + slant, y)
            cr.line_to(x + cw + slant, y)
            cr.line_to(x + cw, y + ch)
            cr.line_to(x, y + ch)
            cr.close_path()
            focus = max(0.0, 1.0 - abs(pos))
            shade = lerp(0.35, 1.0, focus)
            cr.set_source_rgba(shade, shade, shade, 1.0)
            cr.set_line_width(lerp(1.5, 2.5, focus))
            cr.stroke()
            cr.restore()

        label = f"{walls[self.idx].stem}   ({self.idx + 1}/{len(walls)})"
        cr.select_font_face("JetBrains Mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(14)
        ext = cr.text_extents(label)
        bx = cx - ext.width / 2.0 - 16
        by = cy + 470 / 2.0 + 22
        bw = ext.width + 32
        bh = 32
        cr.set_source_rgba(0.0, 0.0, 0.0, 1.0)
        cr.rectangle(bx, by, bw, bh)
        cr.fill()
        cr.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        cr.set_line_width(2.0)
        cr.rectangle(bx, by, bw, bh)
        cr.stroke()
        cr.move_to(cx - ext.width / 2.0, by + 21)
        cr.show_text(label)

win = WallpaperCarousel()
win.show_all()
Gtk.main()
