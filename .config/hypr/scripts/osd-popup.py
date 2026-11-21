#!/usr/bin/env python3
import ctypes, glob, json, os, socket, sys, time
ctypes.CDLL("libgtk-layer-shell.so")
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gdk, GLib, Gtk, GtkLayerShell

SOCK = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "mocha-osd.sock")
def send_msg(icon, val):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        s.sendto(json.dumps({"icon": icon, "val": val}).encode(), SOCK)
        return True
    except OSError:
        return False
    finally:
        s.close()

if len(sys.argv) >= 3 and send_msg(sys.argv[1], sys.argv[2]):
    sys.exit(0)

try:
    os.unlink(SOCK)
except OSError:
    pass
sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
sock.bind(SOCK)
sock.setblocking(False)

CSS = b'''window { background-color: #000000; border: 2px solid #ffffff; border-radius: 0; }
label { color: #ffffff; font-family: "JetBrains Mono", "MesloLGS Nerd Font", "MesloLGS Nerd Font Propo", "Font Awesome 6 Free", "FontAwesome", monospace; font-size: 16px; font-weight: 600; }
label.osd-val { font-size: 18px; font-weight: 700; }
label.big-icon { font-family: "MesloLGS Nerd Font Mono", "FontAwesome", monospace; font-size: 36px; font-weight: 400; }
label.sub-text { font-size: 15px; font-weight: 400; }
progressbar, progressbar trough { min-height: 12px; min-width: 240px; background-color: #000000; background-image: none; border: 2px solid #ffffff; border-radius: 0; padding: 0; margin: 0; }
progressbar progress { min-height: 12px; background-color: #ffffff; background-image: none; border: none; border-radius: 0; padding: 0; margin: 0; }'''

prov = Gtk.CssProvider()
prov.load_from_data(CSS)
Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), prov, Gtk.STYLE_PROVIDER_PRIORITY_USER)

win = Gtk.Window()
vis = win.get_screen().get_rgba_visual()
if vis: win.set_visual(vis)
GtkLayerShell.init_for_window(win)
GtkLayerShell.set_namespace(win, "mocha-osd")
GtkLayerShell.set_layer(win, GtkLayerShell.Layer.OVERLAY)
GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.BOTTOM, True)
GtkLayerShell.set_margin(win, GtkLayerShell.Edge.BOTTOM, 48)
GtkLayerShell.set_keyboard_mode(win, GtkLayerShell.KeyboardMode.NONE)

box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
lbl = Gtk.Label()
val_lbl = Gtk.Label()
sub = Gtk.Label()
bar = Gtk.ProgressBar()
bar.set_valign(Gtk.Align.CENTER)
lbl.set_halign(Gtk.Align.START)
lbl.set_xalign(0.0)
val_lbl.set_halign(Gtk.Align.END)
val_lbl.set_xalign(1.0)
val_lbl.get_style_context().add_class("osd-val")
sub.set_halign(Gtk.Align.CENTER)
sub.set_xalign(0.5)
sub.set_justify(Gtk.Justification.CENTER)
top_row.pack_start(lbl, True, True, 0)
top_row.pack_end(val_lbl, False, False, 0)
box.pack_start(top_row, False, False, 0)
box.pack_start(sub, False, False, 0)
box.pack_start(bar, False, False, 0)
win.add(box)

state = {"cur": 0.0, "target": 0.0, "hide_at": 0.0, "bar_mode": True}

def apply_data(icon, val):
    lbl.set_text(icon)
    state["hide_at"] = time.monotonic() + 1.3
    try:
        pct = int(val)
        state["bar_mode"] = True
        win.set_size_request(-1, -1)
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.set_spacing(10)
        box.set_margin_top(12); box.set_margin_bottom(14)
        box.set_margin_left(16); box.set_margin_right(16)
        lbl.set_halign(Gtk.Align.START)
        lbl.set_xalign(0.0)
        lbl.get_style_context().remove_class("big-icon")
        sub.get_style_context().remove_class("sub-text")
        val_lbl.set_text(str(pct))
        box.show()
        top_row.show()
        lbl.show()
        val_lbl.show()
        sub.hide()
        bar.show()
        state["target"] = max(0.0, min(1.0, pct / 100.0))
        if not win.get_visible():
            state["cur"] = state["target"]
            bar.set_fraction(state["cur"])
            win.show()
        win.resize(1, 1)
    except ValueError:
        state["bar_mode"] = False
        win.set_size_request(140, 140)
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.set_spacing(10)
        box.set_margin_top(24); box.set_margin_bottom(20)
        box.set_margin_left(0); box.set_margin_right(0)
        lbl.set_halign(Gtk.Align.CENTER)
        lbl.set_xalign(0.5)
        lbl.get_style_context().add_class("big-icon")
        sub.get_style_context().add_class("sub-text")
        sub.set_text(str(val))
        box.show()
        top_row.show()
        lbl.show()
        val_lbl.hide()
        bar.hide()
        sub.show()
        win.show()
        win.resize(140, 140)

def on_sock(_fd, _cond):
    try:
        data = json.loads(sock.recv(1024).decode())
        apply_data(data["icon"], data["val"])
    except Exception:
        pass
    return True

last_t = {"v": time.monotonic()}
def tick():
    now = time.monotonic()
    dt = min(now - last_t["v"], 0.05)
    last_t["v"] = now
    if win.get_visible():
        if state["bar_mode"]:
            d = state["target"] - state["cur"]
            alpha = 1.0 - (2.718281828 ** (-24.0 * dt))
            state["cur"] = state["target"] if abs(d) < 0.003 else state["cur"] + d * alpha
            bar.set_fraction(state["cur"])
        if now > state["hide_at"]:
            win.hide()
    return True

GLib.io_add_watch(sock.fileno(), GLib.IO_IN, on_sock)
GLib.timeout_add(16, tick)
if len(sys.argv) >= 3 and send_msg(sys.argv[1], sys.argv[2]):
    sys.exit(0)

try:
    os.unlink(SOCK)
except OSError:
    pass
sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
sock.bind(SOCK)
sock.setblocking(False)

CSS = b'''window { background-color: #000000; border: 2px solid #ffffff; border-radius: 0; }
label { color: #ffffff; font-family: "JetBrains Mono", "MesloLGS Nerd Font", "MesloLGS Nerd Font Propo", "Font Awesome 6 Free", "FontAwesome", monospace; font-size: 16px; font-weight: 600; }
label.osd-val { font-size: 18px; font-weight: 700; }
label.big-icon { font-family: "MesloLGS Nerd Font Mono", "FontAwesome", monospace; font-size: 36px; font-weight: 400; }
label.sub-text { font-size: 15px; font-weight: 400; }
progressbar, progressbar trough { min-height: 12px; min-width: 240px; background-color: #000000; background-image: none; border: 2px solid #ffffff; border-radius: 0; padding: 0; margin: 0; }
progressbar progress { min-height: 12px; background-color: #ffffff; background-image: none; border: none; border-radius: 0; padding: 0; margin: 0; }'''

prov = Gtk.CssProvider()
prov.load_from_data(CSS)
Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), prov, Gtk.STYLE_PROVIDER_PRIORITY_USER)

win = Gtk.Window()
vis = win.get_screen().get_rgba_visual()
if vis: win.set_visual(vis)
GtkLayerShell.init_for_window(win)
GtkLayerShell.set_namespace(win, "mocha-osd")
GtkLayerShell.set_layer(win, GtkLayerShell.Layer.OVERLAY)
GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.BOTTOM, True)
GtkLayerShell.set_margin(win, GtkLayerShell.Edge.BOTTOM, 48)
GtkLayerShell.set_keyboard_mode(win, GtkLayerShell.KeyboardMode.NONE)

box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
lbl = Gtk.Label()
val_lbl = Gtk.Label()
sub = Gtk.Label()
bar = Gtk.ProgressBar()
bar.set_valign(Gtk.Align.CENTER)
lbl.set_halign(Gtk.Align.START)
lbl.set_xalign(0.0)
val_lbl.set_halign(Gtk.Align.END)
val_lbl.set_xalign(1.0)
val_lbl.get_style_context().add_class("osd-val")
sub.set_halign(Gtk.Align.CENTER)
sub.set_xalign(0.5)
sub.set_justify(Gtk.Justification.CENTER)
top_row.pack_start(lbl, True, True, 0)
top_row.pack_end(val_lbl, False, False, 0)
box.pack_start(top_row, False, False, 0)
box.pack_start(sub, False, False, 0)
box.pack_start(bar, False, False, 0)
win.add(box)

state = {"cur": 0.0, "target": 0.0, "hide_at": 0.0, "bar_mode": True}

def apply_data(icon, val):
    lbl.set_text(icon)
    state["hide_at"] = time.monotonic() + 1.3
    try:
        pct = int(val)
        state["bar_mode"] = True
        win.set_size_request(-1, -1)
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.set_spacing(10)
        box.set_margin_top(12); box.set_margin_bottom(14)
        box.set_margin_left(16); box.set_margin_right(16)
        lbl.set_halign(Gtk.Align.START)
        lbl.set_xalign(0.0)
        lbl.get_style_context().remove_class("big-icon")
        sub.get_style_context().remove_class("sub-text")
        val_lbl.set_text(str(pct))
        box.show()
        top_row.show()
        lbl.show()
        val_lbl.show()
        sub.hide()
        bar.show()
        state["target"] = max(0.0, min(1.0, pct / 100.0))
        if not win.get_visible():
            state["cur"] = state["target"]
            bar.set_fraction(state["cur"])
            win.show()
        win.resize(1, 1)
    except ValueError:
        state["bar_mode"] = False
        win.set_size_request(140, 140)
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.set_spacing(10)
        box.set_margin_top(24); box.set_margin_bottom(20)
        box.set_margin_left(0); box.set_margin_right(0)
        lbl.set_halign(Gtk.Align.CENTER)
        lbl.set_xalign(0.5)
        lbl.get_style_context().add_class("big-icon")
        sub.get_style_context().add_class("sub-text")
        sub.set_text(str(val))
        box.show()
        top_row.show()
        lbl.show()
        val_lbl.hide()
        bar.hide()
        sub.show()
        win.show()
        win.resize(140, 140)

def on_sock(_fd, _cond):
    try:
        data = json.loads(sock.recv(1024).decode())
        apply_data(data["icon"], data["val"])
    except Exception:
        pass
    return True

last_us = [None]
def on_tick(widget, clock):
    now = clock.get_frame_time()
    dt = 0.016 if last_us[0] is None else min((now - last_us[0]) / 1000000.0, 0.05)
    last_us[0] = now
    if widget.get_visible():
        if state["bar_mode"]:
            d = state["target"] - state["cur"]
            alpha = 1.0 - (2.718281828 ** (-24.0 * dt))
            state["cur"] = state["target"] if abs(d) < 0.003 else state["cur"] + d * alpha
            bar.set_fraction(state["cur"])
        if time.monotonic() > state["hide_at"]:
            widget.hide()
    return True

GLib.io_add_watch(sock.fileno(), GLib.IO_IN, on_sock)
win.add_tick_callback(on_tick)
if len(sys.argv) >= 3:
    apply_data(sys.argv[1], sys.argv[2])

def get_caps():
    paths = glob.glob("/sys/class/leds/*capslock*/brightness")
    if not paths: return None
    try:
        with open(paths[0]) as f: return f.read().strip()
    except Exception:
        return None
caps_state = {"last": get_caps()}
def poll_caps():
    cur = get_caps()
    if cur is not None and caps_state["last"] is not None and cur != caps_state["last"]:
        caps_state["last"] = cur
        if cur == "1": apply_data(chr(0xf023), "Caps On")
        else: apply_data(chr(0xf09c), "Caps Off")
    return True
GLib.timeout_add(100, poll_caps)
Gtk.main()
