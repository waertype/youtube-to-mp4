#!/usr/bin/env python3
"""
Usage: python download_direct.py <url> [video|audio] [dossier]
"""

import sys
import os
import yt_dlp
from downloader import (
    telecharger_avec_fallback,
    valider_url,
    obtenir_info,
    est_erreur_age,
    est_erreur_cookie_db,
)


def check_youtube_cookies() -> bool:
    if not os.path.exists("cookies.txt"):
        return False
    try:
        with open("cookies.txt", "r", encoding="utf-8", errors="ignore") as f:
            names = set()
            domains = set()
            for line in f:
                if not line.strip() or line.startswith("#"):
                    continue
                parts = line.rstrip("\n").split("\t")
                if len(parts) >= 7:
                    domains.add(parts[0].lower())
                    names.add(parts[5])

            has_youtube = any("youtube.com" in d for d in domains)
            has_session = any(n in names for n in (
                "SID", "HSID", "SSID", "APISID", "SAPISID",
                "__Secure-1PSID", "__Secure-3PSID", "LOGIN_INFO",
            ))
            return has_youtube and has_session
    except Exception:
        return False


def telecharger_direct(url: str, mode: str = "video", dossier: str = ".") -> bool:
    if not url.strip():
        print("Erreur : URL vide")
        return False

    if not valider_url(url):
        print("Erreur : l'URL doit commencer par http:// ou https://")
        return False

    if mode not in ("video", "audio"):
        print("Erreur : mode doit être 'video' ou 'audio'")
        return False

    if dossier != ".":
        os.makedirs(dossier, exist_ok=True)

    has_yt_cookies = check_youtube_cookies()

    strategies_auth = [{}]

    if has_yt_cookies:
        strategies_auth.insert(0, {"cookiefile": "cookies.txt"})
        print("cookies.txt avec session YouTube détecté.\n")
    else:
        print("cookies.txt sans session YouTube — export recommandé.\n")

    strategies_auth.extend([
        {"cookiesfrombrowser": ("chrome",)},
        {"cookiesfrombrowser": ("edge",)},
        {"cookiesfrombrowser": ("firefox",)},
        {"cookiesfrombrowser": ("brave",)},
        {"cookiesfrombrowser": ("opera",)},
    ])

    for idx, opts_cookies in enumerate(strategies_auth, 1):
        method = (
            "cookies.txt" if opts_cookies.get("cookiefile")
            else opts_cookies["cookiesfrombrowser"][0] if opts_cookies
            else "défaut"
        )

        try:
            print(f"Tentative {idx} ({method})…")
            info = obtenir_info(url, opts_cookies)
            if info:
                print(f"  Titre : {info.get('title', 'N/A')}")
                if duree := info.get("duration"):
                    m, s = divmod(int(duree), 60)
                    print(f"  Durée : {m}m {s:02d}s")

            telecharger_avec_fallback(url, mode, opts_cookies, dossier)
            print("\nTerminé.")
            return True

        except yt_dlp.utils.DownloadError as e:
            if est_erreur_cookie_db(e):
                print("  Base de données cookies verrouillée, essai suivant…")
                continue

            elif est_erreur_age(e):
                if idx == len(strategies_auth):
                    print("\nVidéo restreinte par l'âge.")
                    print("Exportez vos cookies YouTube depuis le navigateur (voir README).")
                    return False
                continue

            else:
                msg = str(e).replace("ERROR: ERROR:", "ERROR:").strip()
                if "not available" in str(e).lower() or "no formats" in str(e).lower():
                    print("  Format indisponible, essai suivant…")
                    continue
                print(f"\nErreur : {msg[:200]}")
                return False

        except KeyboardInterrupt:
            print("\nAnnulé.")
            return False

        except Exception as e:
            if idx == len(strategies_auth):
                print(f"Erreur : {str(e)[:200]}")
                return False
            continue

    print("\nÉchec — toutes les méthodes ont été essayées.")
    print("Exportez vos cookies YouTube depuis le navigateur (voir README).")
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python download_direct.py <url> [video|audio] [dossier]")
        sys.exit(1)

    url    = sys.argv[1]
    mode   = sys.argv[2] if len(sys.argv) > 2 else "video"
    dossier = sys.argv[3] if len(sys.argv) > 3 else "."

    success = telecharger_direct(url, mode, dossier)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()