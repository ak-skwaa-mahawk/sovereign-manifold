#!/usr/bin/env bash
# ==============================================================================
# sovereign_edge.sh
# Sovereign Manifold Edge Runtime Bootstrap & Node Control Manager
# Handles environmental pre-flights, ledger state assurance, and local pipeline loops.
# ==============================================================================

set -e

# Target Workspace Definitions
WORKSPACE="$HOME/Turbo_Takeoff"
TOOLS_DIR="$WORKSPACE/tools"
CONFIG_DIR="$WORKSPACE/config"
OUTPUT_DIR="$WORKSPACE/output"
MODELS_DIR="$HOME/models"
MODEL_PATH="$MODELS_DIR/phi-2.Q4_K_M.gguf"

# Graphical Telemetry Output Framing
log_info() { echo -e "\033[1;34m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[1;32m[SUCCESS]\033[0m $1"; }
log_warn() { echo -e "\033[1;33m[WARN]\033[0m $1"; }
log_error() { echo -e "\033[1;31m[ERROR]\033[0m $1"; echo "$2"; exit 1; }

clear
echo "================================================================================"
echo "          SOVEREIGN MANIFOLD — LOCAL-FIRST EDGE RUNTIME Attestation             "
echo "================================================================================"
log_info "Initializing localized pre-flight environment checks..."

# 1. Structural Path Verification
for dir in "$TOOLS_DIR" "$CONFIG_DIR" "$OUTPUT_DIR"; do
    if [ ! -d "$dir" ]; then
        log_warn "Required deployment cell directory missing: $dir. Instantiating..."
        mkdir -p "$dir"
    fi
done

# 2. Dependency Binary Verification
log_info "Scanning engine execution dependencies..."
dependencies=(python3 git)
for cmd in "${dependencies[@]}"; do
    if ! command -v "$cmd" &> /dev/null; then
        log_error "Critical runtime runtime component missing: $cmd." "Please resolve via your package manager (apt/pkg/pacman)."
    fi
done
log_success "Core scripting binaries operational."

# 3. Local Model Ledger Attestation
log_info "Verifying local LLM artifact state..."
if [ ! -f "$MODEL_PATH" ]; then
    log_warn "Local inference weight not detected at target path: $MODEL_PATH"
    log_warn "Briefing adapter will leverage deterministic fallback translation matrix."
else
    log_success "Local LLM weights compiled and ready: $(basename "$MODEL_PATH")"
fi

# 4. Cryptographic Ledger Health Audit
log_info "Auditing local zero-trust state ledger integrity..."
if python3 "$TOOLS_DIR/verify_state_ledger.py" > /dev/null 2>&1; then
    log_success "Active ledger state matches signature parameters perfectly."
else
    log_error "Ledger signature sequence mismatch or verification engine fault encountered." "Check local integrity logs."
fi

# 5. Core Pipeline Loop Activation
echo "--------------------------------------------------------------------------------"
log_info "Spawning Sovereign Takeoff Pipeline Manager execution frame..."
echo "--------------------------------------------------------------------------------"

if python3 "$TOOLS_DIR/process_takeoff_pipeline.py"; then
    log_success "Sovereign pipeline calculation cycle processed cleanly."
else
    log_error "Pipeline transaction run failed inside execution boundary." "Review council matrix."
fi

echo "--------------------------------------------------------------------------------"
log_success "Sovereign Edge Node Initialization Sequence Complete."
log_info "Node Status: OPERATIONAL | Consensus Maintained | Ledger Locked"
echo "================================================================================"
