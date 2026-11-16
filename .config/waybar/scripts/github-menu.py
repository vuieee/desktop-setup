#!/usr/bin/env python3
import os, pathlib, subprocess
nl = chr(10)
home = pathlib.Path.home()
rc = home/".config/rofi/minimal.rasi"
def rofi(prompt, items, w=360, lines=8):
    inp = nl.join(items)
    cmd = ["rofi","-dmenu","-i","-p",prompt,"-theme",str(rc),"-theme-str",f"window {{ width: {w}px; }} listview {{ lines: {lines}; padding: 0px; spacing: 0px; }}"]
    if not items: cmd = ["rofi","-dmenu","-p",prompt,"-theme",str(rc),"-theme-str",f"window {{ width: {w}px; }} mainbox {{ children: [inputbar]; }}"]
    return subprocess.run(cmd,input=inp,text=True,capture_output=True).stdout.strip()
def notify(msg):
    subprocess.Popen(["notify-send","GitHub",msg],stdout=-3,stderr=-3)
def find_repos():
    skip = {".cache",".local",".cargo",".rustup",".npm",".mozilla",".spicetify","node_modules",".git"}
    repos = []
    for r, dirs, _ in os.walk(home):
        dirs[:] = [d for d in dirs if d not in skip and (r != str(home) or not d.startswith("."))]
        p = pathlib.Path(r)
        if (p/".git").exists(): repos.append(p); dirs.clear()
        elif len(p.relative_to(home).parts) >= 3: dirs.clear()
    return sorted(repos)
def git(repo, *args):
    return subprocess.run(["git","-C",str(repo),*args],text=True,capture_output=True)
while True:
    repos = find_repos()
    rows = []
    for rp in repos:
        st = git(rp,"status","--porcelain").stdout.splitlines()
        br = git(rp,"branch","--show-current").stdout.strip() or "detached"
        tag = f"{len(st)}*" if st else "ok"
        rows.append(f"{chr(0xf09b)}  {rp.name:<18} [{br}] {tag:>4}")
    rows += [f"{chr(0xf019)}  Clone Repository...", f"{chr(0xf067)}  Init New Repository..."]
    pick = rofi("repos", rows, 440, min(len(rows), 10))
    if not pick: break
    if "Clone Repository" in pick:
        url = rofi("clone url", [], 480, 1)
        if url:
            dst = home/"Projects"; dst.mkdir(exist_ok=True)
            res = subprocess.run(["git","-C",str(dst),"clone",url],text=True,capture_output=True)
            notify(res.stdout.strip() or res.stderr.strip() or "Cloned")
        continue
    if "Init New Repository" in pick:
        name = rofi("folder name", [], 360, 1)
        if name:
            nd = home/"Projects"/name; nd.mkdir(parents=True,exist_ok=True)
            git(nd,"init"); notify(f"Initialized {nd}")
        continue
    repo = next(rp for rp in repos if f"  {rp.name:<18}" in pick)
    while True:
        st = git(repo,"status","--porcelain").stdout.splitlines()
        br = git(repo,"branch","--show-current").stdout.strip()
        acts = [f"{chr(0xf093)}  Commit & Push ({len(st)} changes)",f"{chr(0xf019)}  Pull Latest",f"{chr(0xf0f6)}  Changed Files ({len(st)})",f"{chr(0xf126)}  Switch / New Branch ({br})",f"{chr(0xf121)}  Open in VS Code",f"{chr(0xf08e)}  Open on GitHub Web"]
        act = rofi(repo.name, acts, 420, 6)
        if not act: break
        if "Commit & Push" in act:
            msg = rofi("commit msg", [], 460, 1)
            if msg:
                git(repo,"add","-A"); c = git(repo,"commit","-m",msg); ps = git(repo,"push")
                notify((ps.stdout + ps.stderr + c.stdout + c.stderr).strip()[:180] or "Pushed!")
        elif "Pull Latest" in act:
            pl = git(repo,"pull"); notify((pl.stdout + pl.stderr).strip()[:180] or "Up to date")
        elif "Changed Files" in act:
            if not st: notify("Working tree clean")
            else: rofi("changes", st, 460, min(len(st), 10))
        elif "Branch" in act:
            brs = [b.strip() for b in git(repo,"branch","--format=%(refname:short)").stdout.splitlines()]
            nb = rofi("branch (or type new)", brs, 360, min(len(brs)+1, 8))
            if nb:
                res = git(repo,"checkout",nb) if nb in brs else git(repo,"checkout","-b",nb)
                notify((res.stdout + res.stderr).strip()[:160] or f"On {nb}")
        elif "VS Code" in act:
            subprocess.Popen(["code",str(repo)],start_new_session=True); break
        elif "GitHub Web" in act:
            u = git(repo,"remote","get-url","origin").stdout.strip().replace("git@"+"github"+".com:","https://"+"github"+".com/").removesuffix(".git")
            if u: subprocess.Popen(["xdg-open",u],start_new_session=True)
