#!/bin/bash
# OpenX6X00 CN build workspace setup (runs on the server)
set -e
B=/mnt/sd/sdl_1t/openx6x00-cn
mkdir -p "$B/work/.brhome"

# siblings layout required by buildroot/local-build.sh
if [ ! -d "$B/work/OpenX6X00" ]; then
  mkdir -p "$B/work/OpenX6X00"
  rsync -a --exclude .git --exclude build-docker --exclude build-host "$B/source/" "$B/work/OpenX6X00/"
fi
[ -d "$B/work/AetherX6100Buildroot" ] || rsync -a "$B/buildroot-trees/AetherX6100Buildroot/" "$B/work/AetherX6100Buildroot/"
[ -d "$B/work/AetherX6200Buildroot" ] || rsync -a "$B/buildroot-trees/AetherX6200Buildroot/" "$B/work/AetherX6200Buildroot/"

# pre-stage u-boot tarballs (avoids ftp.denx.de)
for t in AetherX6100Buildroot AetherX6200Buildroot; do
  mkdir -p "$B/work/$t/buildroot/dl/uboot"
  cp -a "$B/dl/uboot/u-boot-2023.01.tar.bz2" "$B/work/$t/buildroot/dl/uboot/"
  cp -a "$B/dl/uboot/u-boot-2026.07.tar.bz2" "$B/work/$t/buildroot/dl/uboot/"
done

# NJU primary site mirrors the upstream sources.buildroot.net tree layout
for t in AetherX6100Buildroot AetherX6200Buildroot; do
  case $t in
    AetherX6100Buildroot) cfg=X6100_defconfig ;;
    AetherX6200Buildroot) cfg=X6200_defconfig ;;
  esac
  D="$B/work/$t/br2_external/configs/$cfg"
  grep -q '^BR2_PRIMARY_SITE=' "$D" || echo 'BR2_PRIMARY_SITE="https://mirrors.nju.edu.cn/buildroot"' >> "$D"
  grep -q '^BR2_BACKUP_SITE=' "$D" || echo 'BR2_BACKUP_SITE="https://sources.buildroot.net"' >> "$D"
  echo "== $cfg =="
  grep -E '^BR2_(PRIMARY|BACKUP)_SITE=' "$D"
done

# build wrappers: GitHub via ghfast proxy, Go via goproxy.cn
cat > "$B/build-x6100.sh" <<'EOF'
#!/bin/bash
set -x
export HOME=/work/.brhome
mkdir -p "$HOME"
git config --global url."https://ghfast.top/https://github.com/".insteadOf "https://github.com/"
git config --global http.lowSpeedLimit 1000
git config --global http.lowSpeedTime 120
export GOPROXY=https://goproxy.cn,direct
MODEL=x6100 GUI_DIR=/work/OpenX6X00 BR_DIR=/work/AetherX6100Buildroot bash /work/OpenX6X00/buildroot/local-build.sh
EOF

cat > "$B/build-x6200.sh" <<'EOF'
#!/bin/bash
set -x
export HOME=/work/.brhome
mkdir -p "$HOME"
git config --global url."https://ghfast.top/https://github.com/".insteadOf "https://github.com/"
git config --global http.lowSpeedLimit 1000
git config --global http.lowSpeedTime 120
export GOPROXY=https://goproxy.cn,direct
MODEL=x6200 GUI_DIR=/work/OpenX6X00 BR_DIR=/work/AetherX6200Buildroot bash /work/OpenX6X00/buildroot/local-build.sh
EOF
chmod +x "$B/build-x6100.sh" "$B/build-x6200.sh"

echo "SETUP OK"
ls "$B/work"