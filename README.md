# OpenX6X00 中文版（X6100 / X6200）

为协谷短波电台 **X6100** 与 **X6200** 第三方开源固件
[OpenX6X00 v0.3.12](https://github.com/Guru-RF/OpenX6X00) 提供的中文界面版本。

在不修改原固件任何功能的前提下，将电台屏幕界面（LVGL GUI）与网页配置器
（Web configurator）的全部可见文字翻译为简体中文；`FT8`、`RTTY`、`CW`、
`AGC`、`ATT`、`ATU`、`PRE`、`VOX`、`SWR`、`ALC`、`SSB`、`PWR`、`SNR`、
`SOTA`、`POTA`、`WSPR`、`JS8`、`QSO`、`CQ` 等专业/协议术语保留不译。

## 成品镜像

| 型号 | 文件名 |
|---|---|
| X6100 | `X6100/OpenX6X00-x6100-v0.3.12-cn-sdcard.img.zip` |
| X6200 | `X6200/OpenX6X00-x6200-v0.3.12-cn-sdcard.img.zip` |

刷机方式与原版一致：用
[balenaEtcher](https://etcher.balena.io/) 将 zip 内的 `.img` 写入 microSD 卡
即可。原版镜像位于各型号的 `raw_build/` 目录，未做任何改动。

## 本仓库内容

- `source/`：基于 `Guru-RF/OpenX6X00` tag `v0.3.12` 的中文化源码
  - `source/src/fonts/zh_*.c`：新增的 Noto Sans CJK SC 子集字体（17 个字号）
  - `source/src/fonts/font_select.c`：挂载中文字体 fallback 链
  - `source/webserver/`：中文版网页配置器
- `tools_zh/`：翻译与构建辅助工具
  - `extract_zh.py` / `apply_zh.py`：提取 UI 英文串并按词典改写源码
  - `gen_fonts.py`：从译文提取用字，生成 CJK 子集字体
  - `dict_zh/`：中文翻译词典（按 core / apps / extras / web 分文件）
  - `server_*.sh`：在 Linux 服务器上用官方 buildroot 交叉编译的辅助脚本
- `buildroot-trees/`：构建时使用的 AetherX6100 / AetherX6200 buildroot 树
  （体积较大，本地保留，git 不跟踪）

## 重新构建

构建与官方一致：在 Ubuntu 22.04 的 buildroot 容器中交叉编译，X6100 / X6200
各一套。要点见 `source/buildroot/local-build.sh` 与 `tools_zh/server_setup.sh`。

由于上游 `x0rro/xara`（VARA 兼容 Winlink 调制解调器）仓库已停更、release 资产
被删除，无法从源码重建；构建后的镜像会从官方 v0.3.12 镜像中注入现成的
`/usr/bin/xara` 及其许可文件，以完整保留 Winlink / XARA 功能。

## 许可

与本项目同源，遵循原 OpenX6X00 的许可证：
- GUI 主体：LGPL-2.1+
- JS8 引擎（third-party/js8core）：GPL-3.0
- 字体：Noto Sans CJK SC 采用 SIL Open Font License 1.1

详见 `source/LICENSE` 及各组件目录内的许可文件。
