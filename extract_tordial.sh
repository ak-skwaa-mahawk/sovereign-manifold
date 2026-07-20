#!/bin/bash
# extract_tordial.sh — Extract and integrate Tordial Manifold Core into Turbo_Takeoff

REPO_DIR="$HOME/Turbo_Takeoff"
TARBALL="$HOME/Tordial-GS-_Manifold/dist/tordial_core_v1.7.0.tar.gz"

echo "⚡ EXTRUDING TORDIAL CORES INTO WORKSPACE..."

if [ ! -f "$TARBALL" ]; then
    echo "❌ [DEPLOY ERROR]: core archive not found at $TARBALL"
    exit 1
fi

# Create target organizational structure inside the repo
mkdir -p "$REPO_DIR/manifold_core/tools"
mkdir -p "$REPO_DIR/ingress_payloads"

# Extract core files directly into the repository namespace
tar -xzf "$TARBALL" -C "$REPO_DIR/manifold_core/"

# Reposition shell wrapper for repository execution
mv "$REPO_DIR/manifold_core/run_pipeline.sh" "$REPO_DIR/run_pipeline.sh"
chmod +x "$REPO_DIR/run_pipeline.sh"

# Adjust execution paths in the repository version of run_pipeline
sed -i "s|~/Tordial-GS-_Manifold/isst_toft_core.py|$REPO_DIR/manifold_core/isst_toft_core.py|g" "$REPO_DIR/run_pipeline.sh"
sed -i "s|~/Tordial-GS-_Manifold/tools/manifold_dispatcher.py|$REPO_DIR/manifold_core/tools/manifold_dispatcher.py|g" "$REPO_DIR/run_pipeline.sh"

echo "✅ TORDIAL MANIFOLD CORE v1.7.0 EXTRACTED AND WORKSPACE PATHS UPDATED."
echo "🔗 Run pipeline inside repository using: ./run_pipeline.sh \"signal\""
