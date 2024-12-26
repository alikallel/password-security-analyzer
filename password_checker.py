import re
import hashlib
import secrets
import string
from collections import Counter
from pathlib import Path
import requests
import math

class PasswordChecker:
    def __init__(self, wordlist_paths=None, password_history=None):
        self.min_length = 10
        self.required_chars = {
            'uppercase': r'[A-Z]',
            'lowercase': r'[a-z]',
            'numbers': r'[0-9]',
            'special': r'[!@#$%^&*(),.?":{}|<>]'
        }

        # Default wordlist paths to check
        self.wordlist_paths = wordlist_paths or [
            "/usr/share/wordlists/rockyou.txt",
            "/usr/share/wordlists/fasttrack.txt",
            "/usr/share/wordlists/dirb/common.txt"
        ]

        # Store password history to prevent reuse
        self.password_history = password_history or set()

    def check_password_compromise(self, password):
        """Check if password has been compromised using HaveIBeenPwned API."""    
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1_hash[:5], sha1_hash[5:]

        try:
            url = f"https://api.pwnedpasswords.com/range/{prefix}"
            response = requests.get(url, headers={"Add-Padding": "true"})
            response.raise_for_status()

            for line in response.text.splitlines():
                hash_suffix, count = line.split(":")
                if hash_suffix == suffix:
                    return True, int(count)
            return False, 0

        except requests.RequestException as e:
            return None, f"API error: {str(e)}"

    def check_strength(self, password):
        """
        Check password strength including wordlist verification.
        Returns a dict with strength details and wordlist matches.
        """
        issues = []
        suggestions = []

        # Check length
        if len(password) < self.min_length:
            issues.append(f"Password must be at least {self.min_length} characters")
            suggestions.append(f"Add {self.min_length - len(password)} more characters")

        # Check required character types
        missing_chars = []
        for char_type, pattern in self.required_chars.items():
            if not re.search(pattern, password):
                missing_chars.append(char_type)
                issues.append(f"Missing {char_type} character")
                suggestions.append(f"Add at least one {char_type} character")

        # Check for common patterns
        if self._has_common_patterns(password):
            issues.append("Contains common patterns")
            suggestions.append("Avoid keyboard patterns and common sequences")

        # Check character repetition
        char_counts = Counter(password)
        most_common = char_counts.most_common(1)[0]
        if most_common[1] >= 3:
            issues.append(f"Character '{most_common[0]}' is repeated {most_common[1]} times")
            suggestions.append("Avoid repeating characters")

        # Check in wordlists
        wordlist_result = self.check_in_wordlists(password)
        if wordlist_result['found']:
            issues.append(f"Password found in wordlist: {wordlist_result['wordlist']}")
            suggestions.append("Choose a less common password")

        # Calculate entropy
        entropy_score = self._calculate_shannon_entropy(password)
        is_compromised, count = self.check_password_compromise(password)
        if is_compromised:
            issues.append(f"Password found in {count} data breaches")
            suggestions.append("Choose a password that hasn't been compromised")

        # Prevent reuse of historical passwords
        if password in self.password_history:
            issues.append("Password has been used previously")
            suggestions.append("Choose a unique password")

        # Determine overall strength
        is_strong = (len(issues) == 0 and 
                     entropy_score >= 70 and 
                     not wordlist_result['found'] and not is_compromised)

        return {
            'is_strong': is_strong,
            'issues': issues,
            'suggestions': suggestions,
            'entropy_score': entropy_score,
            'wordlist_check': wordlist_result
        }

    def check_in_wordlists(self, password):
        """
        Check if password exists in any of the specified wordlists.
        Returns dict with 'found' status and wordlist name if found.
        """
        result = {
            'found': False,
            'wordlist': None,
            'error': None
        }

        # Also check common variations
        variations = self._generate_common_variations(password)

        for wordlist_path in self.wordlist_paths:
            path = Path(wordlist_path)
            if not path.exists():
                continue

            try:
                with open(path, 'r', encoding='latin-1', errors='ignore') as f:
                    for line in f:
                        word = line.strip()
                        if word in variations:
                            result['found'] = True
                            result['wordlist'] = path.name
                            return result

            except Exception as e:
                result['error'] = f"Error reading {path.name}: {str(e)}"
                continue

        return result

    def _generate_common_variations(self, password):
        """Generate common password variations to check against wordlist."""
        variations = {password.lower(), password}

        # Add some common substitutions (leetspeak)
        leetspeak = str.maketrans('aeios', '43105')
        variations.add(password.lower().translate(leetspeak))

        # Add common number suffixes
        variations.update([
            password + str(n) for n in range(100)
        ])

        # Add common special char suffixes
        variations.update([
            password + c for c in '!@#$%'
        ])

        return variations

    def _has_common_patterns(self, password):
        """Check for common weak patterns in password."""
        common_patterns = [
            r'12345',
            r'qwerty',
            r'password',
            r'admin',
            r'([a-zA-Z0-9])\1{2,}', 
            r'\d{4}', 
            r'(?i)pass'
        ]
        return any(re.search(pattern, password) for pattern in common_patterns)

    def _calculate_shannon_entropy(self, password):
        """Calculate Shannon entropy for the password."""
        if not password:
            return 0

        entropy = 0
        length = len(password)
        char_counts = Counter(password)
        for count in char_counts.values():
            prob = count / length
            entropy -= prob * math.log2(prob)  

        return round(entropy * 100 / 8, 2)  

    def suggest_stronger(self, password):
        """Suggest a stronger version of the given password."""
        result = self.check_strength(password)

        if result['is_strong']:
            return password

        improved = password
        if not re.search(self.required_chars['uppercase'], improved):
            improved += secrets.choice(string.ascii_uppercase)
        if not re.search(self.required_chars['lowercase'], improved):
            improved += secrets.choice(string.ascii_lowercase)
        if not re.search(self.required_chars['numbers'], improved):
            improved += secrets.choice(string.digits)
        if not re.search(self.required_chars['special'], improved):
            improved += secrets.choice('!@#$%^&*')

        while len(improved) < self.min_length:
            improved += secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*')

        if self.check_in_wordlists(improved)['found']:
            improved += ''.join(secrets.choice(string.ascii_letters + string.digits) 
                                for _ in range(3))

        return improved

    def add_to_history(self, password):
        """Add password to the history."""
        self.password_history.add(password)