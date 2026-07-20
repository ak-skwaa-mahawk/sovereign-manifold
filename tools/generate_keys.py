#!/usr/bin/env python3
# generate_keys.py — Sovereign Cryptographic Identity Generator (v1.0.0)
import os
import hashlib

def generate_simple_identity():
    keys_dir = os.path.expanduser("~/Turbo_Takeoff/config/identity")
    os.makedirs(keys_dir, exist_ok=True)
    
    # Generate 32 bytes of secure entropy for a private seed
    private_seed = os.urandom(32)
    private_hex = private_seed.hex()
    
    # Create the corresponding public verification anchor via SHA-256
    public_anchor = hashlib.sha256(private_seed).hexdigest()
    
    with open(os.path.join(keys_dir, "private_seed.key"), "w") as f:
        f.write(private_hex)
    with open(os.path.join(keys_dir, "public_anchor.pub"), "w") as f:
        f.write(public_anchor)
        
    print("=====================================================================")
    print("        🔑 SOVEREIGN IDENTITY COGNITIVE ANCHOR GENERATED             ")
    print("=====================================================================")
    print(f"  Public Verification Anchor ID: {public_anchor}")
    print("  Private Signing Key: [STORED SECURELY ON-DEVICE]")
    print("=====================================================================")

if __name__ == "__main__":
    generate_simple_identity()
