#!/bin/bash
set -euo pipefail
# Install the launcher only; the pipeline runs inside the downloaded Apptainer image.
mkdir -p "$PREFIX/bin"
cp scripts/rapdtool "$PREFIX/bin/rapdtool"
chmod +x "$PREFIX/bin/rapdtool"
