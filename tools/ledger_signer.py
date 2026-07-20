#!/usr/bin/env python3
# ledger_signer.py — Cryptographic Sealed Record Generator (v1.0.0)
import os
import hashlib
import json
import time

class LedgerSigner:
    def __init__(self):
        self.keys_dir = os.path.expanduser("~/Turbo_Takeoff/config/identity")
        self.priv_path = os.path.join(self.keys_dir, "private_seed.key")
        self.pub_path = os.path.join(self.keys_dir, "public_anchor.pub")
        
    def sign_record(self, record_payload: dict) -> dict:
        if not os.path.exists(self.priv_path) or not os.path.exists(self.pub_path):
            return {"error": "Cryptographic keys missing. Run generate_keys.py first."}
            
        with open(self.priv_path, "r") as f:
            priv_key = f.read().strip()
        with open(self.pub_path, "r") as f:
            pub_anchor = f.read().strip()
            
        # Serialize payload cleanly to ensure deterministic hashing
        serialized_payload = json.dumps(record_payload, sort_keys=True)
        
        # Combine payload with the private seed to form a keyed cryptographic signature hash
        signing_buffer = serialized_payload + priv_key
        signature = hashlib.sha256(signing_buffer.encode('utf-8')).hexdigest()
        
        sealed_envelope = {
            "version": "1.0.0",
            "timestamp": time.time(),
            "public_verification_anchor": pub_anchor,
            "data": record_payload,
            "signature_hash_proof": signature
        }
        return sealed_envelope

if __name__ == "__main__":
    signer = LedgerSigner()
    test_data = {"metric": "initialization_verification", "status": "ONLINE"}
    print(json.dumps(signer.sign_record(test_data), indent=2))
