import json, os, re, subprocess, sys, tempfile, urllib.request
from PySide6 import QtWidgets

DEFAULT_INSTALLER_REGEX = re.compile(r"SAC-Setup-v(?P<ver>\d+\.\d+\.\d+)\.exe$", re.I)

def _parse_version(v: str):
    v = v.strip().lstrip("vV")
    return tuple(int(x) for x in v.split("."))

def _is_newer(new: str, old: str) -> bool:
    try:
        return _parse_version(new) > _parse_version(old)
    except Exception:
        return False

def _github_latest_release(repo: str) -> dict:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(url, headers={"User-Agent": "SAC-Updater"})
    with urllib.request.urlopen(req, timeout=12) as resp:
        return json.loads(resp.read().decode("utf-8"))

def _find_installer_asset(release_json: dict, installer_regex: re.Pattern | None):
    assets = release_json.get("assets", []) or []
    if installer_regex:
        for a in assets:
            name = a.get("name", "")
            if installer_regex.match(name) and name.lower().endswith(".exe"):
                return name, a.get("browser_download_url")
    # fallback: pak eerste .exe
    for a in assets:
        name = a.get("name", "")
        if name.lower().endswith(".exe"):
            return name, a.get("browser_download_url")
    return None, None

def _download(url: str, out_path: str, parent=None) -> bool:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "SAC-Updater"}), timeout=60) as r, open(out_path, "wb") as f:
            while True:
                chunk = r.read(64 * 1024)
                if not chunk:
                    break
                f.write(chunk)
        return True
    except Exception as e:
        QtWidgets.QMessageBox.warning(parent, "Download mislukt", f"Kon update niet downloaden:\n{e}")
        return False

def _run_installer(installer_path: str) -> bool:
    try:
        # Wil je stil upgraden? Voeg /VERYSILENT /SUPPRESSMSGBOXES toe.
        subprocess.Popen([installer_path, "/NORESTART"], close_fds=True)
        return True
    except Exception:
        return False

def check_for_updates(parent, current_version: str, repo: str, *, silent: bool = False,
                      installer_regex: re.Pattern | None = DEFAULT_INSTALLER_REGEX):
    """
    parent: je hoofdvenster (bv. root)
    current_version: string zoals '1.2.3'
    repo: 'Gebruiker/RepoNaam' (GitHub)
    silent: True => alleen melden bij update; False => ook 'up-to-date' tonen
    installer_regex: optioneel; matcht de .exe assetnaam op GitHub Releases
    """
    try:
        latest = _github_latest_release(repo)
    except Exception as e:
        if not silent:
            QtWidgets.QMessageBox.information(parent, "Update", f"Kon niet naar updates kijken:\n{e}")
        return

    tag = latest.get("tag_name") or ""
    if not tag:
        if not silent:
            QtWidgets.QMessageBox.information(parent, "Update", "Geen geldige release gevonden.")
        return

    if _is_newer(tag, current_version):
        name, url = _find_installer_asset(latest, installer_regex)
        if not url:
            QtWidgets.QMessageBox.information(parent, "Update", f"Nieuwe versie {tag} gevonden, maar geen installer asset.")
            return
        yn = QtWidgets.QMessageBox.question(
            parent,
            "Update beschikbaar",
            f"Versie {tag} is beschikbaar (huidig {current_version}).\nNu downloaden en installeren?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if yn == QtWidgets.QMessageBox.Yes:
            out = os.path.join(tempfile.gettempdir(), name)
            if _download(url, out, parent) and _run_installer(out):
                QtWidgets.QMessageBox.information(parent, "Update", "Installer gestart. App sluit nu.")
                QtWidgets.QApplication.quit()
    else:
        if not silent:
            QtWidgets.QMessageBox.information(parent, "Update", f"Je bent up-to-date ({current_version}).")
