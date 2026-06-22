#!/usr/bin/env python3
"""
Téléchargeur de vidéos/audio avec yt-dlp.
Gère : restriction d'âge, DB cookies verrouillée, n-challenge YouTube.
"""

import yt_dlp
import os
import sys
import platform

MOTS_AGE = ("sign in to confirm", "age-restricted", "inappropriate")
MOTS_COOKIE_DB = (
    "could not copy",
    "cookie database",
    "could not find",
    "failed to decrypt with dpapi",
)
MOTS_FORMAT = (
    "requested format is not available",
    "no formats available",
    "no video formats found",
    "only images are available",
)

NAVIGATEURS = {
    "1": ("chrome",   "Google Chrome"),
    "2": ("firefox",  "Mozilla Firefox"),
    "3": ("brave",    "Brave"),
    "4": ("edge",     "Microsoft Edge"),
    "5": ("opera",    "Opera"),
    "6": ("chromium", "Chromium"),
    "7": ("safari",   "Safari (macOS uniquement)"),
}

EXTENSIONS_COOKIES = {
    "Chrome / Brave / Edge": "Get cookies.txt LOCALLY  →  https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc",
    "Firefox":               "cookies.txt             →  https://addons.mozilla.org/fr/firefox/addon/cookies-txt/",
}

# Chaque stratégie : (label, extractor_args, format_video, format_audio)
# tv_embedded et mweb contournent souvent la restriction d'âge sans cookies.
STRATEGIES = [
    (
        "tv_embedded (bypass âge)",
        {"youtube": {"player_client": ["tv_embedded"]}},
        "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4][vcodec^=avc1]/best[ext=mp4]",
        "bestaudio[ext=m4a]/bestaudio",
    ),
    (
        "mweb (bypass âge)",
        {"youtube": {"player_client": ["mweb"]}},
        "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4][vcodec^=avc1]/best[ext=mp4]",
        "bestaudio[ext=m4a]/bestaudio",
    ),
    (
        "client web (défaut)",
        {},
        "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4][vcodec^=avc1]/best[ext=mp4]",
        "bestaudio[ext=m4a]/bestaudio",
    ),
    (
        "client Android",
        {"youtube": {"player_client": ["android"]}},
        "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4][vcodec^=avc1]/best[ext=mp4]",
        "bestaudio[ext=m4a]/bestaudio",
    ),
    (
        "client iOS",
        {"youtube": {"player_client": ["ios"]}},
        "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4][vcodec^=avc1]/best[ext=mp4]",
        "bestaudio[ext=m4a]/bestaudio",
    ),
    (
        "format de secours",
        {"youtube": {"player_client": ["tv_embedded", "android", "ios"]}},
        "best[ext=mp4]/best",
        "bestaudio[ext=m4a]/bestaudio",
    ),
]


# --- Détection d'erreurs ---

def est_erreur_age(e) -> bool:
    return any(m in str(e).lower() for m in MOTS_AGE)

def est_erreur_cookie_db(e) -> bool:
    return any(m in str(e).lower() for m in MOTS_COOKIE_DB)

def est_erreur_format(e) -> bool:
    return any(m in str(e).lower() for m in MOTS_FORMAT)


# --- Menus ---

def afficher_menu():
    print("\n" + "─" * 50)
    print("  Téléchargeur yt-dlp")
    print("─" * 50)
    print("  [1]  Télécharger la vidéo (meilleure qualité)")
    print("  [2]  Télécharger l'audio uniquement (MP3)")
    print("  [3]  Afficher les formats disponibles")
    print("  [4]  Quitter")
    print("─" * 50)


def menu_choisir_cookies(titre: str) -> dict | None:
    print(f"\n  {titre}")
    print("─" * 50)
    print("  Depuis votre navigateur :")
    for k, (_, nom) in NAVIGATEURS.items():
        print(f"    [{k}] {nom}")
    print()
    print("  [F] Choisir un fichier cookies.txt")
    print("  [H] Comment exporter mes cookies ?")
    print("  [Q] Annuler")

    while True:
        choix = input("\n  Votre choix : ").strip().upper()

        if choix in NAVIGATEURS:
            nav, nom = NAVIGATEURS[choix]
            print(f"  Cookies depuis : {nom}")
            return {"cookiesfrombrowser": (nav,)}

        elif choix == "F":
            chemin = input("  Chemin du fichier cookies.txt : ").strip().strip('"').strip("'")
            if not chemin:
                print("  Chemin vide, réessayez.")
                continue
            if not os.path.isfile(chemin):
                print(f"  Fichier introuvable : {chemin}")
                continue
            print(f"  Fichier chargé : {chemin}")
            return {"cookiefile": chemin}

        elif choix == "H":
            afficher_aide_cookies()

        elif choix == "Q":
            return None

        else:
            print("  Choix invalide.")


def afficher_aide_cookies():
    print("\n  Exporter vos cookies YouTube en .txt")
    print("─" * 50)
    for nav, url in EXTENSIONS_COOKIES.items():
        print(f"  • {nav}")
        print(f"    {url}\n")
    print("  1. Installer l'extension ci-dessus")
    print("  2. Se connecter à YouTube dans ce navigateur")
    print("  3. Ouvrir l'extension → cliquer Export")
    print("  4. Revenir ici et choisir [F] avec ce fichier")
    input("\n  Appuyez sur Entrée pour continuer…")


def afficher_aide_erreur_cookie_db(nav_bloque: str):
    print(f"\n  Base de données cookies inaccessible")
    print("─" * 50)
    print(f"  {nav_bloque} est ouvert et verrouille sa base SQLite.")
    print()
    print("  Solutions :")
    print(f"  1. Fermer {nav_bloque} complètement puis réessayer")
    print("  2. Utiliser Firefox (ne verrouille pas sa DB)")
    print("  3. Exporter un fichier cookies.txt [H pour l'aide]")


def nom_navigateur_depuis_opts(opts: dict) -> str:
    nav = opts.get("cookiesfrombrowser")
    if nav:
        nav_id = nav[0] if isinstance(nav, tuple) else nav
        for _, (slug, nom) in NAVIGATEURS.items():
            if slug == nav_id:
                return nom
        return nav_id.capitalize()
    return "le navigateur"


# --- Utilitaires ---

def valider_url(url: str) -> bool:
    return url.startswith(("http://", "https://")) and "." in url


def hook_progression(d: dict):
    if d["status"] == "downloading":
        pct     = d.get("_percent_str", "?%").strip()
        vitesse = d.get("_speed_str",   "?").strip()
        eta     = d.get("_eta_str",     "?").strip()
        print(f"\r  {pct}  {vitesse}  ETA {eta}   ", end="", flush=True)
    elif d["status"] == "finished":
        print(f"\n  Terminé → {d['filename']}")
    elif d["status"] == "error":
        print("\n  Erreur lors du téléchargement.")


def opts_base(dossier: str = ".") -> dict:
    return {
        "outtmpl":        os.path.join(dossier, "%(title)s.%(ext)s"),
        "quiet":          False,
        "no_warnings":    True,
        "progress_hooks": [hook_progression],
        "compat_opts":    {"no-certifi"},
        "js_runtimes":    {"node": {}},
    }


# --- Téléchargement ---

def telecharger_avec_fallback(url: str, mode: str, opts_cookies: dict,
                               dossier: str = ".") -> None:
    derniere_erreur = None

    for label, extractor_args, fmt_video, fmt_audio in STRATEGIES:
        print(f"  Tentative : {label}…")

        opts = opts_base(dossier)
        opts.update(opts_cookies)

        if extractor_args:
            opts["extractor_args"] = extractor_args

        if mode == "video":
            opts["format"]              = fmt_video
            opts["merge_output_format"] = "mp4"
        else:
            opts["format"] = fmt_audio
            opts["postprocessors"] = [{
                "key":              "FFmpegExtractAudio",
                "preferredcodec":   "mp3",
                "preferredquality": "192",
            }]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            return

        except yt_dlp.utils.DownloadError as e:
            derniere_erreur = e
            if est_erreur_format(e):
                print("  Format indisponible avec ce client, essai suivant…")
                continue
            else:
                raise

    raise yt_dlp.utils.DownloadError(
        f"Aucun format disponible après toutes les tentatives.\n"
        f"  Dernière erreur : {derniere_erreur}\n\n"
        f"  Installez Node.js pour résoudre le n-challenge YouTube : https://nodejs.org/fr/"
    )


def obtenir_info(url: str, opts_cookies: dict) -> dict | None:
    for extractor_args in (
        {"youtube": {"player_client": ["android"]}},
        {},
    ):
        opts = opts_base(".")
        opts.update({"quiet": True, "no_warnings": True, "skip_download": True})
        opts.update(opts_cookies)
        if extractor_args:
            opts["extractor_args"] = extractor_args
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                return ydl.extract_info(url, download=False)
            except yt_dlp.utils.DownloadError:
                continue
    return None


def afficher_formats(url: str, opts_cookies: dict):
    opts = opts_base(".")
    opts.update({
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {"youtube": {"player_client": ["android"]}},
    })
    opts.update(opts_cookies)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get("formats", [])
        print(f"\nFormats disponibles — {info.get('title', url)}\n")
        print(f"  {'ID':<12} {'EXT':<8} {'RÉSOLUTION':<14} {'FPS':<6} NOTE")
        print("  " + "─" * 58)
        for f in formats:
            print(
                f"  {f.get('format_id','?'):<12}"
                f" {f.get('ext','?'):<8}"
                f" {f.get('resolution','audio only'):<14}"
                f" {str(f.get('fps','') or '-'):<6}"
                f" {f.get('format_note','')}"
            )


# --- Orchestration ---

def executer_action(url: str, choix: str):
    opts_cookies: dict = {}

    while True:
        try:
            print("\nRécupération des informations…")
            info = obtenir_info(url, opts_cookies)
            if info:
                print(f"  Titre : {info.get('title', 'N/A')}")
                print(f"  Site  : {info.get('extractor_key', 'N/A')}")
                if duree := info.get("duration"):
                    m, s = divmod(int(duree), 60)
                    print(f"  Durée : {m}m {s:02d}s")

            if choix == "1":
                print("\nTéléchargement vidéo…")
                telecharger_avec_fallback(url, "video", opts_cookies)
            elif choix == "2":
                print("\nExtraction audio (MP3)…")
                telecharger_avec_fallback(url, "audio", opts_cookies)
            elif choix == "3":
                afficher_formats(url, opts_cookies)

            return

        except yt_dlp.utils.DownloadError as e:
            if est_erreur_cookie_db(e):
                nav_bloque = nom_navigateur_depuis_opts(opts_cookies)
                afficher_aide_erreur_cookie_db(nav_bloque)
                result = menu_choisir_cookies("Choisir une autre méthode")
                if result is None:
                    print("  Annulé.")
                    return
                opts_cookies = result

            elif est_erreur_age(e):
                print("\nVidéo restreinte par l'âge — connexion requise.")
                result = menu_choisir_cookies("Authentification requise")
                if result is None:
                    print("  Annulé.")
                    return
                opts_cookies = result

            else:
                msg = str(e).replace("ERROR: ERROR:", "ERROR:").strip()
                print(f"\nErreur : {msg}")
                return

        except KeyboardInterrupt:
            print("\n\nAnnulé.")
            return


def main():
    print(f"\n  Système : {platform.system()} {platform.release()}")
    print(f"  yt-dlp  : {yt_dlp.version.__version__}")

    while True:
        afficher_menu()
        choix = input("\nVotre choix : ").strip()

        if choix == "4":
            print("\nAu revoir.\n")
            sys.exit(0)

        if choix not in ("1", "2", "3"):
            print("Choix invalide, réessayez.")
            continue

        url = input("\nEntrez l'URL : ").strip()
        if not url:
            print("URL vide, réessayez.")
            continue
        if not valider_url(url):
            print("L'URL doit commencer par http:// ou https://")
            continue

        executer_action(url, choix)


if __name__ == "__main__":
    main()