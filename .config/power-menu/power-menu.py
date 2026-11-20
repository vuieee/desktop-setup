#!/usr/bin/env python3
"""Power menu overlay: tall connected rectangles split by white lines.

The hovered rectangle grows taller than its neighbours (HyDE style).
Click an option, or press: l = lock, r = reboot, f = fast reboot, s = shutdown.
Esc closes it. Running the script again while it is open closes it (toggle).
Needs a Hyprland window rule for class "power-menu" (float, full size, blur).
"""
import os
import signal
import subprocess
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

PIDFILE = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "power-menu.pid")

# Toggle: if another copy is already open, close it and exit.
try:
    with open(PIDFILE) as f:
        old = int(f.read().strip())
    if old != os.getpid():
        with open(f"/proc/{old}/cmdline", "rb") as c:
            if b"power-menu" in c.read():
                os.kill(old, signal.SIGTERM)
                sys.exit(0)
except (FileNotFoundError, ValueError, ProcessLookupError, PermissionError):
    pass
with open(PIDFILE, "w") as f:
    f.write(str(os.getpid()))

ITEMS = [
    ("", "Lock", ["python3", "/home/mocha/.config/power-menu/fake-lock.py"], "l"),
    ("", "Reboot", ["systemctl", "reboot"], "r"),
    ("", "Fast reboot", ["systemctl", "soft-reboot"], "f"),
    ("", "Shutdown", ["systemctl", "poweroff"], "s"),
]

CSS = b"""
window {
  background-color: rgba(0, 0, 0, 0.35);
}
button {
  color: #f1f5f9;
  background-color: #1e222d;
  background-image: none;
  border: none;
  border-top: 1px solid #64748b;
  border-bottom: 1px solid #64748b;
  border-right: 1px solid #64748b;
  border-radius: 0;
  box-shadow: none;
  outline-style: none;
  margin: 44px 0px;
  transition: all 320ms cubic-bezier(0.22, 1, 0.36, 1);
}
button:first-child {
  border-left: 1px solid #64748b;
  border-top-left-radius: 6px;
  border-bottom-left-radius: 6px;
}
button:last-child {
  border-top-right-radius: 6px;
  border-bottom-right-radius: 6px;
}
button.pre {
  margin: 150px 0px;
  opacity: 0;
}
button label.text {
  font-family: "JetBrains Mono", monospace;
  font-size: 18px;
}
button label.icon {
  font-family: "MesloLGS Nerd Font", "FontAwesome";
  font-size: 56px;
}
button:hover {
  color: #f1f5f9;
  background-color: #384152;
  border-left: 1px solid #64748b;
  border-radius: 6px;
  margin: 0px;
}
button:active {
  background-color: #b0b0b0;
}
"""


def run(cmd):
    subprocess.Popen(cmd, start_new_session=True)
    Gtk.main_quit()


def on_key(_widget, event):
    name = Gdk.keyval_name(event.keyval) or ""
    if name == "Escape":
        Gtk.main_quit()
        return True
    for _icon, _label, cmd, key in ITEMS:
        if name.lower() == key:
            run(cmd)
            return True
    return False


def main():
    GLib.set_prgname("power-menu")
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, Gtk.main_quit)

    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
    )

    display = Gdk.Display.get_default()
    monitor = display.get_primary_monitor() or display.get_monitor(0)
    geo = monitor.get_geometry()

    win = Gtk.Window()
    win.set_title("power-menu")
    win.set_decorated(False)
    win.set_app_paintable(True)
    win.set_default_size(geo.width, geo.height)
    visual = screen.get_rgba_visual()
    if visual is not None:
        win.set_visual(visual)
    win.connect("destroy", Gtk.main_quit)
    win.connect("key-press-event", on_key)

    # Connected strip. Each cell is full height; resting cells get a vertical
    # margin from the CSS, so the hovered one (margin 0) grows taller.
    menu = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    menu.set_homogeneous(True)
    menu.set_halign(Gtk.Align.CENTER)
    menu.set_valign(Gtk.Align.CENTER)

    cell_w = int(geo.width * 0.15)
    cell_h = int(geo.height * 0.6)
    buttons = []
    for icon_char, text, cmd, _key in ITEMS:
        button = Gtk.Button()
        button.get_style_context().add_class("pre")
        buttons.append(button)
        button.set_can_focus(False)
        button.set_size_request(cell_w, cell_h)
        overlay = Gtk.Overlay()
        nat = os.path.exists(os.path.expanduser("~/.local/share/mocha-theme-bak/native"))
        lt = "#f8fafc" in CSS.decode() or "#f1f5f9" in CSS.decode()
        icols = {"Lock": "#0284c7" if lt else "#38bdf8", "Reboot": "#ca8a04" if lt else "#facc15", "Fast reboot": "#ea580c" if lt else "#fb923c", "Shutdown": "#dc2626" if lt else "#f87171"}
        icon = Gtk.Label()
        if nat and text in icols: icon.set_markup(f"<span foreground=\x27{icols[text]}\x27>{icon_char}</span>")
        else: icon.set_text(icon_char)
        icon.get_style_context().add_class("icon")
        icon.set_halign(Gtk.Align.CENTER)
        icon.set_valign(Gtk.Align.CENTER)
        overlay.add(icon)
        label = Gtk.Label(label=text)
        label.get_style_context().add_class("text")
        label.set_halign(Gtk.Align.CENTER)
        label.set_valign(Gtk.Align.END)
        label.set_margin_bottom(28)
        overlay.add_overlay(label)
        button.add(overlay)
        button.connect("clicked", lambda _b, c=cmd: run(c))
        menu.pack_start(button, True, True, 0)

    win.add(menu)
    win.set_opacity(0.0)
    win.show_all()

    # Pop-up: cells rise from thin slivers to full height, one after another,
    # while the whole overlay fades in.
    def reveal(btn):
        btn.get_style_context().remove_class("pre")
        return False

    for i, btn in enumerate(buttons):
        GLib.timeout_add(60 + i * 60, reveal, btn)

    def fade():
        o = min(win.get_opacity() + 0.1, 1.0)
        win.set_opacity(o)
        return o < 1.0

    GLib.timeout_add(16, fade)
    Gtk.main()


try:
    main()
finally:
    try:
        os.remove(PIDFILE)
    except OSError:
        pass
