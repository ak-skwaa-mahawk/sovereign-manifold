#!/bin/bash
# run_pipeline.sh — Unified Pipeline Execution Wrapper

if [ -z "$1" ]; then
    echo "Usage: ./run_pipeline.sh \"your raw signal input here\""
    exit 1
fi

# Pass input cleanly through the core and directly into the dispatcher, skipping core logging prefixes
echo "$1" | python3 /data/data/com.termux/files/home/Turbo_Takeoff/manifold_core/isst_toft_core.py | grep -v "^🚀" | grep -v "^📡" | python3 /data/data/com.termux/files/home/Turbo_Takeoff/manifold_core/tools/manifold_dispatcher.py
