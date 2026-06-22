# youtube-dl

Téléchargeur de vidéos et audio YouTube basé sur [`yt-dlp`](https://github.com/yt-dlp/yt-dlp).

Gère les vidéos restreintes par l'âge (cookies), le n-challenge JavaScript (Node.js) et la compatibilité Windows (MP4/H.264 + AAC).

---

## Table des matières

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Cookies YouTube](#cookies-youtube)
- [Diagnostics](#diagnostics)
- [Problèmes courants](#problèmes-courants)

---

## Prérequis

| Outil | Rôle |
|---|---|
| [Python 3.10+](https://www.python.org/) | Exécuter les scripts |
| [Node.js LTS](https://nodejs.org/) | Résoudre le n-challenge YouTube |
| [FFmpeg](https://ffmpeg.org/) | Fusionner/convertir les flux |

## Installation

```powershell
python -m pip install -U yt-dlp python-certifi-win32
```

Vérification :

```powershell
python --version
node --version
ffmpeg -version
python -m yt_dlp --version
```

---

## Utilisation

```powershell
cd "D:\youtube mp4"
```

### Télécharger une vidéo

```powershell
python download_direct.py "https://www.youtube.com/watch?v=..." video
```

### Télécharger l'audio (MP3)

```powershell
python download_direct.py "https://www.youtube.com/watch?v=..." audio
```

### Télécharger dans un sous-dossier

```powershell
python download_direct.py "https://www.youtube.com/watch?v=..." video ".\downloads"
```

### Menu interactif

```powershell
python downloader.py
```

---

## Cookies YouTube

Nécessaires pour les vidéos restreintes par l'âge. L'export doit être fait **immédiatement après un rechargement de la page** pour capturer les cookies `google.com` (SAPISID, SID…) en plus des cookies `youtube.com` — sans eux, l'authentification échoue.

### Chrome / Edge / Brave

1. Installer l'extension [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Aller sur [youtube.com](https://www.youtube.com) et se connecter
3. **Recharger la page** (`F5`)
4. **Immédiatement** cliquer sur l'extension → **Export** → choisir *Netscape HTTP Cookie Format*
5. Sauvegarder sous `D:\youtube mp4\cookies.txt`

### Firefox

1. Installer l'extension [cookies.txt](https://addons.mozilla.org/fr/firefox/addon/cookies-txt/)
2. Aller sur [youtube.com](https://www.youtube.com) et se connecter
3. **Recharger la page** (`F5`)
4. **Immédiatement** cliquer sur l'extension → **Export**
5. Sauvegarder sous `D:\youtube mp4\cookies.txt`

> [!WARNING]
> Ne jamais partager `cookies.txt`. Ce fichier contient votre session de connexion.

---

## Diagnostics

Lister les formats disponibles :

```powershell
python -m yt_dlp --cookies cookies.txt --list-formats "URL"
```

Lancer les tests :

```powershell
python -m pytest test_downloader.py -v
```

---

## Problèmes courants

### `Sign in to confirm your age`

Réexporter `cookies.txt` : recharger YouTube (`F5`) puis exporter immédiatement (voir [Cookies YouTube](#cookies-youtube)).

### `n challenge solving failed`

Node.js est absent ou non détecté. Installer [Node.js LTS](https://nodejs.org/) puis vérifier :

```powershell
node --version
```

### `CERTIFICATE_VERIFY_FAILED`

```powershell
python -m pip install python-certifi-win32
```

### Base de données cookies verrouillée (Chrome / Edge)

Le navigateur est ouvert et verrouille sa base SQLite. Solutions :
- Fermer le navigateur complètement puis réessayer
- Utiliser Firefox (ne verrouille pas sa base)
- Exporter `cookies.txt` manuellement (voir [Cookies YouTube](#cookies-youtube))

### Audio illisible sous Windows

Convertir en AAC :

```powershell
ffmpeg -y -i "input.mp4" -c:v copy -c:a aac -b:a 192k "output.mp4"
```