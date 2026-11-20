#!/usr/bin/env python3
import datetime, signal, gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gdk, GLib, Gtk, GtkLayerShell
CSS = b"window { background-color: rgba(0, 0, 0, 0.35); } #clock { color: #f1f5f9; font-family: 'JetBrains Mono'; font-size: 72px; font-weight: bold; } #date { color: #dddddd; font-family: 'JetBrains Mono'; font-size: 18px; margin-top: 8px; }"
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, Gtk.main_quit)
screen = Gdk.Screen.get_default()
prov = Gtk.CssProvider()
prov.load_from_data(CSS)
Gtk.StyleContext.add_provider_for_screen(screen, prov, Gtk.STYLE_PROVIDER_PRIORITY_USER)
win = Gtk.Window()
vis = screen.get_rgba_visual()
if vis: win.set_visual(vis)
GtkLayerShell.init_for_window(win)
GtkLayerShell.set_namespace(win, "mocha-fakelock")
GtkLayerShell.set_layer(win, GtkLayerShell.Layer.OVERLAY)
GtkLayerShell.set_keyboard_mode(win, GtkLayerShell.KeyboardMode.EXCLUSIVE)
GtkLayerShell.set_exclusive_zone(win, -1)
for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM, GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT): GtkLayerShell.set_anchor(win, edge, True)
box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
box.set_halign(Gtk.Align.CENTER)
box.set_valign(Gtk.Align.CENTER)
clk = Gtk.Label()
clk.set_name("clock")
dt = Gtk.Label()
dt.set_name("date")
box.pack_start(clk, False, False, 0)
box.pack_start(dt, False, False, 0)
win.add(box)
def tick():
    now = datetime.datetime.now()
    clk.set_text(now.strftime("%I:%M %p"))
    dt.set_text(now.strftime("%A, %B %d"))
    return True
def on_key(_w, ev):
    if Gdk.keyval_name(ev.keyval) in ("Return", "KP_Enter", "space"):
        Gtk.main_quit()
        return True
    return False
win.connect("key-press-event", on_key)
tick()
GLib.timeout_add(1000, tick)
win.show_all()
Gtk.main()
