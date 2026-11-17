#!/usr/bin/env python3
import hashlib, os, pathlib, shutil, subprocess, sys
os.environ["GDK_BACKEND"] = "wayland"
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf
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

class WallpaperCarousel(Gtk.Window):
    def __init__(self):
        super().__init__(title="mocha-wallpaper")
        self.set_wmclass("mocha-wallpaper", "mocha-wallpaper")
        self.set_decorated(False)
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.idx = 0
        self.hitboxes = []
        self.da = Gtk.DrawingArea()
        self.da.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.da.connect("draw", self.on_draw)
        self.da.connect("button-press-event", self.on_click)
        self.add(self.da)
        self.connect("key-press-event", self.on_key)
        self.connect("destroy", Gtk.main_quit)

    def apply_current(self):
        chosen = walls[self.idx]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(chosen, target)
        hc.write_text(chr(10).join(["wallpaper {", "    monitor =", "    path = ~/Pictures/wallpaper.png", "    fit_mode = cover", "}", ""]))
        subprocess.run(["pkill", "-x", "hyprpaper"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.Popen(["hyprpaper"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        subprocess.run(["notify-send", "-a", "Wallpapers", "Wallpaper Applied", chosen.name])
        Gtk.main_quit()

    def on_key(self, widget, event):
        kv = event.keyval
        if kv in (Gdk.KEY_Escape, Gdk.KEY_q, Gdk.KEY_Q):
            Gtk.main_quit()
        elif kv in (Gdk.KEY_Left, Gdk.KEY_a, Gdk.KEY_A, Gdk.KEY_h, Gdk.KEY_H):
            self.idx = (self.idx - 1) % len(walls)
            self.da.queue_draw()
        elif kv in (Gdk.KEY_Right, Gdk.KEY_d, Gdk.KEY_D, Gdk.KEY_l, Gdk.KEY_L):
            self.idx = (self.idx + 1) % len(walls)
            self.da.queue_draw()
        elif kv in (Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_space):
            self.apply_current()

    def on_click(self, widget, event):
        for slot, x0, x1, y0, y1 in self.hitboxes:
            if x0 <= event.x <= x1 and y0 <= event.y <= y1:
                if slot == 0:
                    self.apply_current()
                else:
                    self.idx = (self.idx + slot) % len(walls)
                    self.da.queue_draw()
                return
        Gtk.main_quit()

    def on_draw(self, widget, cr):
        w = widget.get_allocated_width()
        h = widget.get_allocated_height()
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.72)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        specs = [
            (-2, -370, 150, 300, 34),
            (-1, -205, 190, 375, 42),
            (0,     0, 290, 470, 52),
            (1,   205, 190, 375, 42),
            (2,   370, 150, 300, 34),
        ]
        cx, cy = w / 2.0, h / 2.0 - 10
        self.hitboxes = []

        for slot, dx, cw, ch, slant in specs:
            wi = (self.idx + slot) % len(walls)
            pb = pixbufs[wi]
            x = cx + dx - cw / 2.0
            y = cy - ch / 2.0
            self.hitboxes.append((slot, x - slant / 2.0, x + cw + slant / 2.0, y, y + ch))

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
            if slot != 0:
                cr.set_source_rgba(0.0, 0.0, 0.0, 0.35 if abs(slot) == 1 else 0.55)
                cr.paint()
            cr.restore()

            cr.save()
            cr.move_to(x + slant, y)
            cr.line_to(x + cw + slant, y)
            cr.line_to(x + cw, y + ch)
            cr.line_to(x, y + ch)
            cr.close_path()
            if slot == 0:
                cr.set_source_rgba(1.0, 1.0, 1.0, 1.0)
                cr.set_line_width(2.5)
            elif abs(slot) == 1:
                cr.set_source_rgba(0.65, 0.65, 0.65, 0.9)
                cr.set_line_width(1.5)
            else:
                cr.set_source_rgba(0.35, 0.35, 0.35, 0.8)
                cr.set_line_width(1.5)
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
