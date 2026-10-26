<h1 align="center">📺 Tv Parsa</h1>

<p align="center">
  <a href="https://github.com/Belfagor2005/tvParsa">
    <img src="https://img.shields.io/badge/Version-1.9-blue.svg" alt="Version">
  </a>

  <a href="https://www.enigma2.net">
    <img src="https://img.shields.io/badge/Enigma2-Plugin-ff6600.svg" alt="Enigma2">
  </a>

  <a href="https://www.python.org">
    <img src="https://img.shields.io/badge/Python-2.7%2B-blue.svg" alt="Python">
  </a>

  <a href="https://www.gnu.org/licenses/gpl-3.0.html">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="GPLv3">
  </a>

  <a href="https://github.com/Belfagor2005/tvParsa/actions/workflows/pylint.yml">
    <img src="https://github.com/Belfagor2005/tvParsa/actions/workflows/pylint.yml/badge.svg" alt="Python package">
  </a>

  <a href="https://github.com/Belfagor2005/tvParsa/actions/workflows/ruff.yml">
    <img src="https://github.com/Belfagor2005/tvParsa/actions/workflows/ruff.yml/badge.svg" alt="Ruff Status">
  </a>
</p>

<p align="center">
  <a href="https://github.com/Belfagor2005">
    <img src="https://komarev.com/ghpvc/?username=Belfagor2005&label=Repository%20Views&color=blueviolet" alt="Visitors">
  </a>
</p>

<p align="center">
  <a href="https://ko-fi.com/lululla">
    <img src="https://img.shields.io/badge/_-Donate-red.svg?logo=githubsponsors&labelColor=555555&style=for-the-badge" alt="Ko-fi">
  </a>

  <a href="https://paypal.me/belfagor2005">
    <img src="https://img.shields.io/badge/_-Donate-green.svg?logo=githubsponsors&labelColor=555555&style=for-the-badge" alt="PayPal">
  </a>
</p>

---

<p align="center">
  <img src="https://github.com/Belfagor2005/tvParsa/blob/main/usr/lib/enigma2/python/Plugins/Extensions/parsatv/logo.png" height="120">
</p>

**Enigma2 project**

Player for **Parsa TV** — an Enigma2 plugin that brings the public live TV channels listed on [parsatv.com](https://www.parsatv.com/) directly into your satellite receiver, with no subscriptions, no accounts, and no external apps.

---

## 📖 What it does

`tvParsa` is a lightweight browser + player for the free live streams published by Parsa TV.
The plugin scrapes the public mobile site (`https://www.parsatv.com/m/`), extracts
the channel list, and hands it to Enigma2 as a playable service reference.

You browse the catalogue inside the plugin menu, select a channel, and it plays —
the same way any satellite channel would. You can also **convert any category into a
favourite `.tv` bouquet**, so the channels show up in your normal channel list and can
be zapped with the remote.

No streams are hosted by this plugin. It is only a front-end for the streams that
Parsa TV publishes publicly.

---

## ✨ Features

### Three ways to browse

| Menu entry | What it shows |
|---|---|
| **PARSA ALL TV** | Every channel available on the site, sorted alphabetically |
| **PARSA TV CATEGORY** | Channels grouped by language/genre (Persian, News, Radio, Music, Sport, Movies, Arabic, Turkish, Kurdish, Afghan, Armenian, Hebrew, Spanish, German, Ukrainian, Indian, IRIB, …) |
| **PARSA SPORT** | Only sport channels (direct scrape of the Sport category) |

### Player

- Live playback through the standard Enigma2 player (`4097` / `8193` service types)
- Infobar with **IMDb / TMDB** lookup (if `IMDb` or `TMDB` plugin is installed)
- Aspect-ratio restoration on exit
- Automatic cleanup of temporary HLS files

### Conversion to bouquet

Press **YELLOW — Convert** inside any list and the current category is written to:

- `/etc/enigma2/userbouquet.<name>.tv`
- registered in `/etc/enigma2/bouquets.tv`
- bouquets and service list reloaded automatically

The bouquet name is derived from the category name, so `Persian` becomes
`userbouquet.persian.tv` and appears in your channel list as *PERSIAN (TV)*.

### Update checker

On startup the plugin reads the remote `version` / `changelog` from the installer
script on GitHub and offers a one-click update if a newer release is available.
`GREEN` / `YELLOW` in the main menu trigger the update manually, and `INFO` long-press
forces the latest development snapshot.

### Skin-aware

The plugin ships with **HD**, **FHD** and **UHD** skins, plus a **DreamOS**
variant, and picks the right one at runtime by reading `getDesktop(0).size()`.

---

## 📦 Installation

### From `.ipk`

```bash
opkg install enigma2-plugin-extensions-parsatv_1.9_all.ipk
```

### Manual

Copy the plugin folder to:

```
/usr/lib/enigma2/python/Plugins/Extensions/parsatv/
```

then restart the GUI (`Menu → Standby & Restart → Restart GUI`).

### Requirements

- Enigma2 image (OpenATV, OpenPLi, OpenBH, OpenVision, DreamOS, …)
- Python **2.7** or **3.x**
- Internet connection on the receiver
- Optional: `IMDb` or `TMDB` plugin for the info button
- Optional: `streamlink` or `exteplayer3` for HLS-only streams

---

## 🚀 Usage

1. Open **Menu → Plugins → Parsa TV**
2. Pick one of the three sections (`ALL TV` / `CATEGORY` / `SPORT`)
3. Browse with **UP / DOWN** and press **OK** to open a category or play a channel
4. In a channel list:
   - **GREEN** → play the selected channel
   - **YELLOW** → convert the whole list to a `.tv` bouquet
   - **RED** → back
5. In the player:
   - **INFO** → IMDb / TMDB lookup
   - **STOP** / **EXIT** → stop and return to the previous channel

---

## 🗒️ Changelog

### 1.9

- **Robustness:** every `_gotPageLoad` and `okRun` now checks `if not content: return`
  and shows a friendly error instead of crashing on empty responses
- **Parsa Sport:** now scrapes the `<td id="sport">` section directly
  (the previous URL-based filter was silently dropping ~75 % of sport channels)
- **Convert:** `functools.partial(make_m3u2, namex)` — the timer no longer
  calls `None`
- **Play:** `match[-1]` + `try/except` — no more `NameError` when a page
  yields no video link
- **parsatv3:** handles `n1 == -1` and `n2 == -1` gracefully (last category
  no longer truncated)
- **parsatv:** uses `content[n1:]` instead of the fragile `</ul></td>` terminator
- **parsatv2:** fixed `url` shadowing inside the parsing loop
- **convert_bouquet:** `split(",", 1)` so channel names containing a comma survive
- **check_vers:** tolerant version comparison (`_ver()`) and `try/except` around
  the remote fetch
- **`aspect_manager.restore_aspect()`** — the missing parentheses were preventing
  aspect-ratio restoration on exit
- **Quality:** `ruff`-clean (`ruff.toml` provided), removed dead code, removed
  redundant `int()` casts, replaced manual index loops with `enumerate()`,
  simplified nested `if`s
- **i18n:** all user-facing strings and docstrings are now in **English**

### 1.8 and earlier

- See commit history.

---

## ⚖️ Legal Disclaimer

No video files are stored in this repository.
The repository contains **user-submitted links** to publicly available video stream URLs, which — to the best of our knowledge — have been intentionally made public by the copyright holders.

If any links infringe your rights as a copyright holder, they may be removed by:
- opening an **Issue**
- submitting a **Pull Request**

We have **no control** over the destination of external links.
Removing a link from a playlist **does not remove the content from the web**.

Linking does **not directly infringe copyright**, as no copy is made on this repository.
To remove content from the web, contact the **hosting provider** (not GitHub or repository maintainers).

---

## ⚠️ Notes

- No media files are hosted on the repository or on any server of the project
- Channel availability depends entirely on **parsatv.com** and on the broadcasters
- Broken channels are the responsibility of the upstream provider, not of this plugin
- Website: [www.tivustream.com](http://www.tivustream.com)

---

## 👤 Credits

- **Code:** Lululla & PCD
- **Skins:** MMark
- **Original website:** [parsatv.com](https://www.parsatv.com/)
- **License:** GPL-3.0

If you find this plugin useful and want to say thanks:

[![Ko-fi](https://img.shields.io/badge/_-Ko--fi-red.svg?logo=githubsponsors&labelColor=555555&style=for-the-badge)](https://ko-fi.com/lululla)
[![PayPal](https://img.shields.io/badge/_-PayPal-green.svg?logo=githubsponsors&labelColor=555555&style=for-the-badge)](https://paypal.me/belfagor2005)

