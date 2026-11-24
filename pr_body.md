## What

Completes the Simplified Chinese translation in `po/zh_CN.po`. **39 entries newly translated; 41 lines changed; one file; no source code touched.**

## Added translations

**xOTA site types** — English and French spellings name the same kind of place, so each pair gets one Chinese word:

| msgid | zh_CN |
|---|---|
| `Bunker:` | 掩体： |
| `Ruin:` / `Ruine:` | 废墟： |
| `Remains:` / `Vestige:` | 遗迹： |
| `Memorial:` / `Memoire:` | 纪念物： |
| `Abandoned:` / `Abandonne:` | 已废弃： |

**App page tabs**

| msgid | zh_CN |
|---|---|
| ` APP WeFax ` | ` 应用 传真 ` |
| ` APP NavTex ` | ` 应用 NAVTEX ` |
| ` APP Zello ` | ` 应用 Zello ` |
| ` APP SVXConnect ` | ` 应用 SVXConnect ` |

**Other UI**

| msgid | zh_CN |
|---|---|
| `SmartCW (MIDI)` | SmartCW（MIDI） |
| `QSOs` | 通联次数 |
| `GhostNet RTTY: 7.077 MHz, 45.45 baud, 170 Hz` | GhostNet RTTY：7.077 MHz，45.45 波特，170 Hz |
| `airplanes.live, adsb.lol (ODbL)` | airplanes.live、adsb.lol（ODbL） |
| `WiFi: %s` / `WiFi %s: %s` | Wi-Fi：%s / Wi-Fi %s：%s |
| `Error: Failed to modify connection '%s': %s` | 修改连接“%s”失败：%s |
| `Error: Failed to delete connection '%s': %s` | 删除连接“%s”失败：%s |
| `Connection '%s' (%s) successfully modified.` | 连接“%s”（%s）已成功修改。 |
| `Connection '%s' (%s) successfully deleted.` | 连接“%s”（%s）已成功删除。 |
| `Tailscale: %s` | Tailscale：%s |
| `Winlink: %s` | Winlink：%s |
| `OpenX6X00 by RF.Guru` | RF.Guru 出品的 OpenX6X00 |
| `the radio is in %s, not USB-D%s` | 电台当前处于 %s 模式，而不是 USB-D%s |
| ` (an app holds the mode)` | ` （某个应用程序正在占用该模式）` |
| `RX %s %s  Hound: %s` | 接收 %s %s  Hound: %s |

The leading space of ` (an app holds the mode)` is kept on purpose: the GUI concatenates it after the line above, and without it the two run together. The `Hound` colon goes back to ASCII so it matches the source format.

## Terminology unified

The CW keyer dropdown already has a hand-written `手动` next to these, so the letters are spelled out instead of left as bare `-L` / `-R`:

| before | after |
|---|---|
| `自动-L` | `自动(左)` |
| `自动-R` | `自动(右)` |

## Left in English on purpose

None of these reach an LVGL text call, so `i18n_tr()` never sees them (`src/i18n_hook.h`). Translating them has no effect on the radio and only makes the file harder to keep:

- `X6100 GUI Play` / `Capture` / `Network voice` / `Local` / `Station` / `Zello` / `SVXConnect` / `Monitor` — `pa_stream_new()` names, seen only in `pavucontrol`
- ` fault settings` — argument of `x6100-update`
- `rx on` / `rx off` — argument of `btaudio_run()`
- ` funnel on` / ` funnel off` — arguments of `tailscale funnel`
- `gpsd, let go` — spoken by `said_answer()`, never drawn
- `Funnel` — Tailscale's product name for that feature

## Checks

- `msgfmt -c` — no errors; **3195 translated, 506 untranslated**
- Every `msgstr` character is inside **GB2312**, the range `NotoSansCJKsc-GB2312.otf` covers, so no new boxes
- Placeholders, `#rrggbb` colour codes and `\n` counts unchanged; the existing `%.0s` that swallows the English plural `s` is left as it was
- `git diff` — 41 insertions, 41 deletions, one file

## Testing

Not run on a radio. Verified by inspection and `msgfmt`; these are pure UI strings. Copying the file to the card's `/mnt/i18n/zh_CN.po` and re-picking 简体中文 under *Settings > Display > Interface > Language* shows the result without flashing. The language stays marked **draft** until a native speaker has read it on a radio.