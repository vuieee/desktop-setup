#!/usr/bin/env python3
import ast, math, operator as op, os, pathlib, subprocess, gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk

OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.FloorDiv: op.floordiv, ast.Mod: op.mod, ast.Pow: op.pow, ast.USub: op.neg, ast.UAdd: op.pos}

def safe_eval(expr):
    s = expr.replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**").strip()
    def _ev(n):
        if isinstance(n, ast.Expression): return _ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)): return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in OPS: return OPS[type(n.op)](_ev(n.left), _ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in OPS: return OPS[type(n.op)](_ev(n.operand))
        raise ValueError()
    return _ev(ast.parse(s, mode="eval"))

def fmt(v):
    if isinstance(v, float):
        return str(int(v)) if v.is_integer() else f"{v:.10g}"
    return str(v)

h = pathlib.Path.home()
ws = (h/".config/waybar/style.css").read_text() if (h/".config/waybar/style.css").exists() else ""
nat = (h/".local/share/mocha-theme-bak/native").exists()
dark = not any(x in ws for x in ("background-color: #ffffff;", "rgba(255, 255, 255, 0.72)", "background-color: #f8fafc;", "rgba(248, 250, 252, 0.78)"))
if nat:
    bg, fg, bd, bw, sub, hov, acc = ("#1e222d", "#f1f5f9", "#94a3b8", "1px", "#384152", "#2d3343", "#38bdf8") if dark else ("#f8fafc", "#0f172a", "#64748b", "1px", "#e2e8f0", "#cbd5e1", "#0284c7")
else:
    bg, fg, bd, bw, sub, hov, acc = ("#000000", "#ffffff", "#ffffff", "2px", "#141414", "#ffffff", "#ffffff") if dark else ("#ffffff", "#000000", "#000000", "2px", "#ebebeb", "#000000", "#000000")
inv_fg = bg if not nat else fg

css = f"""window {{ background-color: {bg}; color: {fg}; border: {bw} solid {bd}; }}
label.expr {{ font-family: "JetBrains Mono", monospace; font-size: 13px; color: {bd}; }}
label.disp {{ font-family: "JetBrains Mono", monospace; font-size: 28px; font-weight: bold; color: {fg}; }}
button {{ font-family: "JetBrains Mono", monospace; font-size: 16px; color: {fg}; background: {bg}; background-image: none; border: 1px solid {bd}; border-radius: 0; box-shadow: none; outline: none; transition: background-color 140ms ease, color 140ms ease; }}
button.op {{ background: {sub}; }}
button.eq {{ background: {acc}; color: {bg}; font-weight: bold; }}
button:hover {{ background: {hov}; color: {inv_fg}; }}
button:hover label {{ color: {inv_fg}; background: transparent; }}""".encode()

prov = Gtk.CssProvider()
prov.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), prov, Gtk.STYLE_PROVIDER_PRIORITY_USER)

win = Gtk.Window(title="Calculator")
win.set_wmclass("mocha-calc", "mocha-calc")
win.set_default_size(320, 460)
win.set_resizable(False)
win.connect("destroy", Gtk.main_quit)

root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
root.set_margin_top(14); root.set_margin_bottom(14); root.set_margin_left(14); root.set_margin_right(14)
win.add(root)

expr_lbl = Gtk.Label(label=" ")
expr_lbl.get_style_context().add_class("expr")
expr_lbl.set_xalign(1.0); expr_lbl.set_ellipsize(3)
root.pack_start(expr_lbl, False, False, 0)

disp_lbl = Gtk.Label(label="0")
disp_lbl.get_style_context().add_class("disp")
disp_lbl.set_xalign(1.0); disp_lbl.set_ellipsize(3)
root.pack_start(disp_lbl, False, False, 2)

st = {"buf": "", "just_eval": False}

def copy_res():
    txt = disp_lbl.get_text()
    cp = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE, start_new_session=True)
    cp.stdin.write(txt.encode()); cp.stdin.close()
    subprocess.Popen(["notify-send", "-a", "Calculator", "Copied", txt], start_new_session=True)

def press(k):
    if k == "Copy":
        copy_res(); return
    if k == "C":
        st["buf"] = ""; st["just_eval"] = False
        expr_lbl.set_text(" "); disp_lbl.set_text("0"); return
    if k == "⌫":
        if st["just_eval"]:
            st["buf"] = ""; st["just_eval"] = False
        else:
            st["buf"] = st["buf"][:-1]
        disp_lbl.set_text(st["buf"] or "0"); return
    if k == "=":
        if not st["buf"]: return
        try:
            res = fmt(safe_eval(st["buf"]))
            expr_lbl.set_text(st["buf"] + " =")
            disp_lbl.set_text(res)
            st["buf"] = res; st["just_eval"] = True
        except Exception:
            expr_lbl.set_text(st["buf"])
            disp_lbl.set_text("Error")
            st["buf"] = ""; st["just_eval"] = False
        return
    if st["just_eval"] and k in "0123456789.":
        st["buf"] = ""
    st["just_eval"] = False
    st["buf"] += k
    disp_lbl.set_text(st["buf"])

grid = Gtk.Grid(row_spacing=6, column_spacing=6, row_homogeneous=True, column_homogeneous=True)
root.pack_start(grid, True, True, 0)

rows = [
    [("C", "op"), ("(", "op"), (")", "op"), ("⌫", "op")],
    [("7", ""), ("8", ""), ("9", ""), ("÷", "op")],
    [("4", ""), ("5", ""), ("6", ""), ("×", "op")],
    [("1", ""), ("2", ""), ("3", ""), ("−", "op")],
    [("0", ""), (".", ""), ("Copy", "op"), ("+", "op")],
    [("=", "eq")],
]

for r, row in enumerate(rows):
    for c, (txt, cls) in enumerate(row):
        btn = Gtk.Button(label=txt)
        btn.set_can_focus(False)
        if cls: btn.get_style_context().add_class(cls)
        btn.connect("clicked", lambda _b, x=txt: press(x))
        grid.attach(btn, c, r, 4 if txt == "=" else 1, 1)

def on_key(_w, ev):
    name = Gdk.keyval_name(ev.keyval) or ""
    if name == "Escape": Gtk.main_quit(); return True
    if (ev.state & Gdk.ModifierType.CONTROL_MASK) and name.lower() == "c": copy_res(); return True
    if name in ("Return", "KP_Enter", "equal"): press("="); return True
    if name == "BackSpace": press("⌫"); return True
    if name in ("Delete", "c", "C"): press("C"); return True
    km = {"plus": "+", "KP_Add": "+", "minus": "−", "KP_Subtract": "−", "asterisk": "×", "KP_Multiply": "×", "slash": "÷", "KP_Divide": "÷", "parenleft": "(", "parenright": ")", "period": ".", "KP_Decimal": ".", "asciicircum": "^"}
    if name in km: press(km[name]); return True
    if len(name) == 1 and name.isdigit(): press(name); return True
    if name.startswith("KP_") and len(name) == 4 and name[-1].isdigit(): press(name[-1]); return True
    return False

win.connect("key-press-event", on_key)
win.show_all()
Gtk.main()
