#!/usr/bin/env python3
import hashlib
import hmac

def simulate_crypto_tree():
    print("🔑 [MOCK BIP-32]: Initializing cryptographic master generation...")
    
    # 1. Your private master recovery phrase (the core secret)
    master_seed_phrase = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    print(f"🌲 Master Root Phrase: '{master_seed_phrase}'")
    
    # 2. Derive the Master Parent Private Key using SHA-512
    master_seed_bytes = master_seed_phrase.encode('utf-8')
    master_hash = hmac.new(b"Bitcoin seed", master_seed_bytes, hashlib.sha512).digest()
    
    master_private_key = master_hash[:32]
    master_chain_code = master_hash[32:]
    print(f"🔒 Master Parent Key:  0x{master_private_key.hex()[:32]}...")

    print("\n🌿 Generating Derived Child Accounts (Leaves):")
    # 3. Simulate generating 3 unique account addresses from the single parent key
    for index in range(3):
        # We combine the index number with the parent chain code to branch out dynamically
        data = index.to_bytes(4, byteorder='big')
        child_hash = hmac.new(master_chain_code, master_private_key + data, hashlib.sha512).digest()
        
        child_private_key = child_hash[:32]
        # Generate a mock public address by hashing the child key
        mock_public_address = hashlib.sha256(child_private_key).hexdigest()[:40]
        
        print(f"   👉 Index {index} -> Public Account Address: 1x{mock_public_address}")

    print("\n🔍 SECURITY ANALYSIS:")
    print("Even if a quantum computer steals one of those public addresses, the math only goes one way (down the tree).")
    print("An attacker cannot invert the SHA-512/HMAC operations to climb back up and discover the Master Root Phrase.")

if __name__ == "__main__":
    simulate_crypto_tree()
