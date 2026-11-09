#!/bin/bash
# pptx → pdf → png для визуальной проверки
set -e
cd "$(dirname "$0")/.."
python3 build/build_deck.py
timeout 240 soffice --headless --convert-to pdf --outdir . Ulytau_Gid_Pitch.pptx >/dev/null 2>&1
OUT=${1:-/tmp/render}; rm -rf "$OUT"; mkdir -p "$OUT"
pdftoppm -r ${2:-60} -png Ulytau_Gid_Pitch.pdf "$OUT/s"
ls "$OUT" | wc -l
