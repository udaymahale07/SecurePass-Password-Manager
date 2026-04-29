import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives import hashes

class EncryptionManager:

    def __init__(self):
        # We NEVER store the password in plain text.
        # We only store the derived key in memory while the app is running.
        self.key = None
	
    def derive_key(self, master_password: str, salt: bytes = None) -> tuple:
        """
        Phase 1: Key Derivation (Argon2id)
        Converts a text password into a 32-byte cryptographic key.
        """
        if salt is None:
            # Generate a random 16-byte salt for new users
            # Purpose: Makes same passwords produce different keys
	    # Prevents rainbow table attacks
            salt = os.urandom(16)
	
	
        # Configure Argon2id (The standard for password hashing)
        # This makes it slow for hackers to guess passwords (Brute Force Protection)
        kdf = Argon2id(
            salt=salt,
            length=32,          # 32 bytes = 256 bits (Required for AES-256)
            iterations=3,       # CPU cost (min recommended: 3 for OWASP compliance)
            lanes=4,            # Parallelism for performance
            memory_cost=64 * 1024, # Memory usage (64MB)
        )
        
        # Derive the key
        self.key = kdf.derive(master_password.encode('utf-8'))
        return self.key, salt

    def encrypt_data(self, plaintext: str) -> dict:
        """
        Phase 2: Encryption (AES-256-GCM)
        Encrypts the data and generates a unique Nonce (IV).
        """
        if not self.key:
            raise ValueError("Vault locked. Key not derived.")

        # Generate a unique 12-byte Nonce (Number used ONCE)
        # CRITICAL: Never reuse a nonce with the same key.
        # Prevent pettern recorgnition
        nonce = os.urandom(12) 

        # Create the AES-GCM cipher
        aesgcm = AESGCM(self.key)

        # Encrypt
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), associated_data=None)

        return {
            'ciphertext': ciphertext,
            'nonce': nonce
        }

    def decrypt_data(self, ciphertext: bytes, nonce: bytes) -> str:
        """
        Phase 3: Decryption
        Unlocks the data. If the data was tampered with, this crashes (Security Feature).
        """
        if not self.key:
            raise ValueError("Vault locked.")

        aesgcm = AESGCM(self.key)

        try:
            # Attempt to decrypt
            plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
            return plaintext_bytes.decode('utf-8')
        except Exception:
            return "ERROR: Integrity Check Failed (Wrong Key or Data Tampered)"
            
            
        # In crypto_manager.py → verify_master_password
    def verify_master_password(self, master_password: str, salt: bytes, stored_verifier: bytes) -> bool:
        try:
            self.derive_key(master_password, salt)
            digest = hashes.Hash(hashes.SHA256())
            digest.update(self.key)
            computed = digest.finalize()
            return computed == stored_verifier
        except Exception as e:
            print(f"[WARN] verify_master_password failed: {e}")
            return False
            

# --- TEST AREA (Run this file directly to verify) ---
if __name__ == "__main__":
    print("--- STARTING SECURITY CHECK ---")
    
    # 1. Setup
    manager = EncryptionManager()
    password = "MyStrongPassword123!"
    
    # 2. Derive Key
    print(f"[*] Deriving Key from: {password}")
    key, salt = manager.derive_key(password)
    print(f"    -> Salt Generated: {salt.hex()}")
    print(f"    -> Key Derived (Hidden): {key.hex()[:10]}...")
    
    # 3. Encrypt
    secret = "This is a secret message"
    print(f"\n[*] Encrypting: '{secret}'")
    data = manager.encrypt_data(secret)
    print(f"    -> Ciphertext: {data['ciphertext'].hex()[:20]}...")
    print(f"    -> Nonce: {data['nonce'].hex()}")
    
    # 4. Decrypt
    print(f"\n[*] Decrypting...")
    result = manager.decrypt_data(data['ciphertext'], data['nonce'])
    print(f"    -> Result: {result}")
    
    if result == secret:
        print("\n[SUCCESS] Engine is working correctly.")
    else:
        print("\n[FAIL] Decryption mismatch.")
