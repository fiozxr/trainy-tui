# Trainy TUI

<p align="center">
  <img src="https://img.shields.io/badge/Trainy-TUI_Music_Client-111111?style=for-the-badge&logoColor=ffffff" alt="Trainy TUI">
  <img src="https://img.shields.io/badge/Visualizer-Animated_Beat_Bars-000000?style=for-the-badge" alt="Animated Beat Bars">
  <img src="https://img.shields.io/badge/Playlists-YouTube_&_YT_Music-000000?style=for-the-badge" alt="Playlist Links">
  <img src="https://img.shields.io/badge/Python-3.10+-black?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Linux-000000?style=for-the-badge&logo=linux" alt="Linux">
  <img src="https://img.shields.io/badge/License-GPL--3.0-black?style=for-the-badge" alt="GPL 3.0">
</p>

An open-source, ultra-fast, minimalist **Terminal YouTube Music Player** built for Linux CLI power users. Featuring **YouTube playlist link playback**, an **animated real-time beat bars visualizer**, continuous **Smart Radio autoplay**, synchronized LRC lyrics, time seeking, and complete queue management—all in a sleek monochrome TUI.

---

## ⚡ Global 1-Line Installation (Auto-Cleaned)

Install Trainy TUI globally with auto-cleanup:

```bash
curl -fsSL https://raw.githubusercontent.com/fiozxr/trainy-tui/main/install.sh | bash
```

Once installed, launch Trainy from **any terminal directory**:
```bash
trainy
```

---

## Architecture & Visualizer Showcase

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ TRAINY TUI   [Home (1)]   [Queue (2)]   [Player (3/F)]                     │
├────────────────────────────────────────────────────────────────────────────┤
│ Search songs or paste YouTube Playlist link... (Press / to focus)          │
├─────────────────────────────────────────────┬──────────────────────────────┤
│ TRACK SEARCH RESULTS & LIBRARY              │ SYNCED LYRICS (LRCLIB)       │
│                                             │                              │
│ > Track Title           Artist     Duration │   [00:15] Verse line 1       │
│   Track Title 2         Artist 2   03:45    │ > [00:19] Active lyric line  │
│   Track Title 3         Artist 3   04:12    │   [00:24] Verse line 3       │
│                                             │                              │
├─────────────────────────────────────────────┴──────────────────────────────┤
│ ┌──────────────────────────────────────────┐                               │
│ │  [ █  ▅  ▃  ▇  ▄  █  ▆  ▂  ▅  █  ▃  ▇  ▅ ]  │  <- ANIMATED BEAT BARS    │
│ └──────────────────────────────────────────┘                               │
│ Playing: Track Title - Artist [Radio]  [████████████░░░░░░░░] 01:23 / 03:45│
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Features

- 🔗 **YouTube & YT Music Playlist Links:** Paste any YouTube or YouTube Music playlist URL (or playlist ID) directly into the search bar to load and play the entire playlist!
- 🎵 **Animated Dancing Beat Bars Visualizer:** Real-time dynamic ASCII spectrum visualizer dancing to playback inside Full Player mode (`3` / `F`).
- ⚡ **Global Installation with Auto-Cleanup:** Installs system-wide to `~/.local/bin/trainy` and automatically deletes temporary setup/clone files upon completion.
- 📻 **Smart Radio & Autoplay:** Continuous track recommendation engine powered by YouTube Music—automatically queues related songs so music never stops.
- 🔍 **Instant YouTube Music Search:** Search songs, artists, and albums in milliseconds.
- 📜 **Synchronized LRC Lyrics:** Real-time auto-scrolling lyrics via [LRCLIB](https://lrclib.net).
- ⏩ **Time Seeking:** Skip forward (`+10s`) or rewind (`-10s`) with arrow keys.
- 🎶 **Queue & Playlist Management:** View, navigate, and clear your upcoming playback queue.
- 🔀 **Shuffle & Repeat:** Toggle random track selection (`S`) and track looping.
- 🔳 **Monochrome Design:** High-contrast text UI designed for dotfile customization, tmux sessions, and minimal Linux setups.

---

## Prerequisites

Trainy requires **Python 3.10+** and **FFmpeg (`ffplay`)** for native audio streaming.

### Installing FFmpeg

#### Ubuntu / Debian
```bash
sudo apt update && sudo apt install ffmpeg python3-pip
```

#### Arch Linux
```bash
sudo pacman -S ffmpeg python-pip
```

#### Fedora
```bash
sudo dnf install ffmpeg python3-pip
```

---

## Keyboard Shortcuts

| Key / Control | Action |
| :--- | :--- |
| **`1`** | Home / Search View |
| **`2`** | Up Next Queue View |
| **`3`** or **`f`** | Full Player Screen Mode |
| **`/`** | Focus Search Input Bar |
| **`Enter`** | Search / Load Playlist / Play Selected Track |
| **`Space`** | Play / Pause Playback |
| **`→`** or **`.`** | Skip +10 Seconds Forward |
| **`←`** or **`,`** | Skip -10 Seconds Backward |
| **`s`** | Toggle Shuffle Mode (ON / OFF) |
| **`r`** | Toggle Smart Radio Autoplay (ON / OFF) |
| **`n`** | Next Track |
| **`p`** | Previous Track |
| **`q`** | Quit Application |

---

## License

Distributed under the **GPL-3.0 License**. Free and open-source software.
