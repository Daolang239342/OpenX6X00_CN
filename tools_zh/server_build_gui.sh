#!/bin/bash
# Cross-compile the OpenX6X00 GUI outside buildroot, inside the openx6x00-build container.
# Produces /work/out/<model>/x6100_gui (or x6200_gui) and the web server wheel.
# Mirrors buildroot/build.sh, with the already-built toolchain and the local
# vendor package trees (control libs + ft8_lib staging).
set -e

B=/work
GUI=/work/OpenX6X00
MODEL=${1:-x6100}
case $MODEL in
    x6100) TREE=AetherX6100Buildroot ;;
    x6200) TREE=AetherX6200Buildroot ;;
    *) echo "usage: build_gui.sh x6100|x6200"; exit 2 ;;
esac
BR=$B/$TREE/build
TC=$BR/host/bin
STAGE=$BR/host/arm-buildroot-linux-gnueabihf/sysroot
OUT=$B/out/$MODEL
mkdir -p "$OUT"

# toolchainfile built by buildroot
cmake -S "$GUI" -B "$OUT" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TOOLCHAIN_FILE="$BR/host/share/buildroot/toolchainfile.cmake" \
    -DCMAKE_INSTALL_PREFIX=/usr \
    -DCMAKE_COLOR_MAKEFILE=OFF \
    -DHW_BACKEND=$MODEL \
    -DLV_CONF_BUILD_DISABLE_EXAMPLES=ON \
    -DLV_CONF_BUILD_DISABLE_DEMOS=ON \
    -DBUILD_DOC=OFF -DBUILD_DOCS=OFF -DBUILD_EXAMPLE=OFF -DBUILD_EXAMPLES=OFF \
    -DBUILD_TEST=OFF -DBUILD_TESTS=OFF -DBUILD_TESTING=OFF \
    -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
    -DCMAKE_SYSROOT="$STAGE"

# fetchcontent requires a git checkout; the control libs/boost are prebuilt in the toolchain staging.
# For the host build only, liquid-dsp and ft8_lib came from HOST_DEPS; for the radio build,
# the toolchain staging already carries libliquid, libft8 and boost from the previous buildroot build.
cmake --build "$OUT" --target x6100_gui -j"${BR2_JLEVEL:-8}"

# also install the web server (a flit wheel is built by its package; reuse its sources)
echo "== web server"
cd "$GUI/webserver"
python3 -m flit build --format wheel 2>/dev/null || \
  python3 -m pip wheel . -w "$OUT" --no-deps 2>/dev/null || \
  echo "web wheel fallback skipped"

cp "$OUT/src/x6100_gui" "$OUT/$MODEL-gui"
echo "GUI OK: $OUT/$MODEL-gui"