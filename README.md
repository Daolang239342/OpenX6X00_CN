# OpenX6X00 中文版（X6100 / X6200）

> ## ⏸ 仓库已暂停维护
>
> **官方已内置中文（v0.3.13 起）。请优先使用官方固件，并把精力放在官方 `po/zh_CN.po` 上。**
>
> - 官方仓库：https://github.com/Guru-RF/OpenX6X00
> - 官方最新版：**v0.3.13**（2026-11-20）
> - 切换到中文：`设置 > 显示 > 接口 > 语言`，选择 **简体中文**
> - 官方中文实现：gettext（`po/zh_CN.po`）+ 专用字体
>   `NotoSansCJKsc-GB2312.otf`；用音频时官方说明还提到
>   `NotoSansCJKsc-GB2312.otf` 之外的字会显示方框
> - 官方中文状态：**draft（草稿）**，3408 条中已译 3139 条（92.1%）
>
> ### 如何帮官方完善中文（不需要编译固件）
>
> 1. 下载本项目根目录的 **`official_zh_CN_待翻译.tsv`**（269 条未译）
> 2. 在「译文(请填写)」列填上中文；**留空的条目会继续显示英文，不会出错**
> 3. 把填好的文件交给维护者，或按官方 `po/README.md` 提 PR
>
> 更快的试译方式：把 `<code>.po` 放到电台 SD 卡 DATA 分区的
> `/mnt/i18n/` 目录，然后在 `设置 > 显示 > 语言` 里再选一次该语言，
> GUI 会**立刻重新读取**你的文件，无需重新刷机。
>
> ---
>
> 本仓库保留的是 **v0.3.12** 的中文化（改 C 源码硬编码方式），
> 供存档与对照，不再继续跟进上游更新。

---

以下为 v0.3.12 中文版的历史内容。

## 成品镜像

| 型号 | 文件名 |
|---|---|
| X6100 | `X6100/OpenX6X00-x6100-v0.3.12-cn-sdcard.img.zip` |
| X6200 | `X6200/OpenX6X00-x6200-v0.3.12-cn-sdcard.img.zip` |

刷机方式：与原版一致。

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
