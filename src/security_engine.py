import secrets
import string
import re
import hashlib
import urllib.request
import urllib.error
import time

class SecurityEngine:
    @staticmethod
    def generate_secure_password(length=16):
        """Generates a highly secure random password."""
        if length < 12:
            length = 12

        characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
        password = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.digits),
            secrets.choice("!@#$%^&*"),
            secrets.choice(string.ascii_lowercase)
        ]
        while len(password) < length:
            password.append(secrets.choice(characters))

        secrets.SystemRandom().shuffle(password)
        return ''.join(password)

    @staticmethod
    def evaluate_password_strength(password: str):
        """Evaluates strength and returns UI-friendly colors/percentages."""
        score = 0
        if not password:
            return {"level": "None", "percentage": 0, "color": "#475569"}

        if len(password) >= 12: score += 25
        if len(password) >= 16: score += 20
        if re.search(r'[A-Z]', password): score += 15
        if re.search(r'[a-z]', password): score += 15
        if re.search(r'\d', password): score += 15
        if re.search(r'[^A-Za-z0-9]', password): score += 10

        if score >= 85:
            return {"level": "Strong", "percentage": score/100, "color": "#22c55e"}
        elif score >= 60:
            return {"level": "Moderate", "percentage": score/100, "color": "#eab308"}
        else:
            return {"level": "Weak", "percentage": score/100, "color": "#ef4444"}

    @staticmethod
    def check_pwned_password(password: str, db=None) -> int:
        """k-Anonymity breach check using HaveIBeenPwned API."""
        if not password: return 0
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1_hash[:5], sha1_hash[5:]
        
        # Cache check
        if db:
            cached = db.get_breach_cache(prefix)
            if cached:
                cached_resp, timestamp = cached
                # TTL of 7 days (604800 seconds)
                if time.time() - timestamp < 604800:
                    for line in cached_resp.splitlines():
                        returned_suffix, count = line.split(':')
                        if returned_suffix == suffix:
                            return int(count)
                    return 0

        url = f"https://api.pwnedpasswords.com/range/{prefix}"

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SecurePass-Project'})
            with urllib.request.urlopen(req, timeout=8) as response:
                result_str = response.read().decode('utf-8')
                if db:
                    db.set_breach_cache(prefix, result_str, time.time())
                results = result_str.splitlines()
            for line in results:
                returned_suffix, count = line.split(':')
                if returned_suffix == suffix:
                    return int(count)
            return 0
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            print(f"[WARN] Breach check network error: {e}")
            return -1

    @staticmethod
    def find_duplicate_passwords(entries: list, crypto) -> dict:
        """
        Groups entries that share the same decrypted password.
        Returns a dict: {password_hash: [list of entry dicts]} for groups with > 1 entry.
        """
        import hashlib
        groups = {}
        for row in entries:
            try:
                pwd = crypto.decrypt_data(row["ciphertext"], row["nonce"])
                key = hashlib.sha256(pwd.encode()).hexdigest()
                if key not in groups:
                    groups[key] = []
                groups[key].append(dict(row))
            except Exception:
                continue
        return {k: v for k, v in groups.items() if len(v) > 1}

    @staticmethod
    def find_weak_passwords(entries: list, crypto) -> list:
        """Returns list of entry dicts whose password strength is Weak."""
        weak = []
        for row in entries:
            try:
                pwd = crypto.decrypt_data(row["ciphertext"], row["nonce"])
                result = SecurityEngine.evaluate_password_strength(pwd)
                if result["level"] == "Weak":
                    weak.append(dict(row))
            except Exception:
                continue
        return weak

    @staticmethod
    def find_old_passwords(entries: list, days: int = 90) -> list:
        """Returns entries where created_at is older than 'days' days."""
        from datetime import datetime, timezone, timedelta
        threshold = datetime.now(timezone.utc) - timedelta(days=days)
        old = []
        for row in entries:
            try:
                # updated_at may not exist if DB migration hasn't run yet
                try:
                    ts_str = row["updated_at"] or row["created_at"]
                except Exception:
                    ts_str = row["created_at"]
                if not ts_str:
                    continue
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if ts < threshold:
                    old.append(dict(row))
            except Exception:
                continue
        return old
