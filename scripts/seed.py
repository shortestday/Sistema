"""Seed writable app state once. Existing user settings are never replaced."""
import argparse
from pathlib import Path


def create_once(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(content)
        path.chmod(0o600)
    except FileExistsError:
        pass


def create_once_or_empty(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return
    path.write_text(content, encoding="utf-8")
    path.chmod(0o600)


def seed(home, defaults, agents, study):
    create_once(home / ".config/DankMaterialShell/settings.json", defaults.read_text())
    create_once_or_empty(home / ".config/niri/dms/binds.kdl", "binds {\n}\n")
    create_once(home / ".pi/agent/AGENTS.md", agents.read_text())
    root = home / "Estudio"
    create_once(root / "AGENTS.md", study.read_text())
    for course in ["AI-Security", "PortSwigger", "Algebra-ML"]:
        folder = root / course
        create_once(folder / "PROGRESO.md", "# Progreso\n\n## Ultimo tema\n\n## Siguiente paso\n\n## Dudas\n")
        (folder / "ejercicios").mkdir(parents=True, exist_ok=True)
        (folder / "evidencias").mkdir(exist_ok=True)
    # Profile separation, no proxy enabled until the corresponding proxy is running.
    lab = home / ".mozilla/firefox-lab"
    create_once(lab / "user.js", '\n'.join([
        'user_pref("browser.shell.checkDefaultBrowser", false);',
        'user_pref("browser.startup.homepage", "about:blank");',
        'user_pref("browser.newtabpage.enabled", false);',
        'user_pref("signon.rememberSignons", false);',
        'user_pref("identity.fxaccounts.enabled", false);',
    ]) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for name in ["home", "defaults", "agents", "study"]:
        p.add_argument("--" + name, type=Path, required=True)
    seed(**vars(p.parse_args()))
