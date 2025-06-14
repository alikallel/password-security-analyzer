import re
import hashlib
import secrets
import string
import time
from collections import Counter
from pathlib import Path
import requests
import math
from utils import ProgressIndicator, show_status, format_time, print_results_summary

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
        """Check if password has been compromised using HaveIBeenPwned API with progress indicator."""
        progress = ProgressIndicator()
        
        show_status("Checking password against breach database", "security")
        progress.spinner("Querying HaveIBeenPwned database")
        
        try:
            sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
            prefix, suffix = sha1_hash[:5], sha1_hash[5:]

            url = f"https://api.pwnedpasswords.com/range/{prefix}"
            
            start_time = time.time()
            response = requests.get(url, headers={"Add-Padding": "true"}, timeout=10)
            end_time = time.time()
            
            progress.stop_spinner()
            
            query_time = end_time - start_time
            show_status(f"Breach check completed in {format_time(query_time)}", "info")
            
            response.raise_for_status()

            for line in response.text.splitlines():
                hash_suffix, count = line.split(":")
                if hash_suffix == suffix:
                    show_status(f"⚠️ Password found in {int(count):,} breaches!", "warning")
                    return True, int(count)
            
            show_status("✅ Password not found in known breaches", "success")
            return False, 0

        except requests.RequestException as e:
            progress.stop_spinner()
            show_status(f"Breach check failed: {str(e)}", "error")
            return None, f"API error: {str(e)}"
        except Exception as e:
            progress.stop_spinner()
            show_status(f"Unexpected error during breach check: {str(e)}", "error")
            return None, f"Error: {str(e)}"

    def check_strength(self, password):
        """
        Check password strength including wordlist verification with progress indicators.
        Returns a dict with strength details and wordlist matches.
        """
        show_status("Starting comprehensive password analysis", "security")
        
        issues = []
        suggestions = []
        analysis_steps = []

        # Step 1: Basic checks
        show_status("Performing basic strength checks", "info")
        time.sleep(0.2)  # Small delay for UI feedback
        
        # Check length
        if len(password) < self.min_length:
            issues.append(f"Password must be at least {self.min_length} characters")
            suggestions.append(f"Add {self.min_length - len(password)} more characters")
        analysis_steps.append("✅ Length check completed")

        # Check required character types
        missing_chars = []
        for char_type, pattern in self.required_chars.items():
            if not re.search(pattern, password):
                missing_chars.append(char_type)
                issues.append(f"Missing {char_type} character")
                suggestions.append(f"Add at least one {char_type} character")
        analysis_steps.append("✅ Character type validation completed")

        # Step 2: Pattern analysis
        show_status("Analyzing password patterns", "info")
        time.sleep(0.3)
        
        # Check for common patterns
        if self._has_common_patterns(password):
            issues.append("Contains common patterns")
            suggestions.append("Avoid keyboard patterns and common sequences")
        analysis_steps.append("✅ Pattern analysis completed")

        # Check character repetition
        char_counts = Counter(password)
        most_common = char_counts.most_common(1)[0]
        if most_common[1] >= 3:
            issues.append(f"Character '{most_common[0]}' is repeated {most_common[1]} times")
            suggestions.append("Avoid repeating characters")
        analysis_steps.append("✅ Repetition analysis completed")

        # Step 3: Wordlist check
        show_status("Checking against common wordlists", "info")
        wordlist_result = self.check_in_wordlists_with_progress(password)
        if wordlist_result['found']:
            issues.append(f"Password found in wordlist: {wordlist_result['wordlist']}")
            suggestions.append("Choose a less common password")
        analysis_steps.append("✅ Wordlist check completed")

        # Step 4: Entropy calculation
        show_status("Calculating password entropy", "info")
        time.sleep(0.2)
        entropy_score = self._calculate_shannon_entropy(password)
        analysis_steps.append("✅ Entropy calculation completed")

        # Step 5: Breach check
        is_compromised, count = self.check_password_compromise(password)
        if is_compromised:
            issues.append(f"Password found in {count:,} data breaches")
            suggestions.append("Choose a password that hasn't been compromised")

        # Step 6: History check
        if password in self.password_history:
            issues.append("Password has been used previously")
            suggestions.append("Choose a unique password")
        analysis_steps.append("✅ History check completed")

        # Final analysis
        show_status("Finalizing analysis", "info")
        is_strong = (len(issues) == 0 and 
                     entropy_score >= 70 and 
                     not wordlist_result['found'] and not is_compromised)

        # Display analysis summary
        print("\n Analysis Steps Completed:")
        for step in analysis_steps:
            print(f"   {step}")

        result = {
            'is_strong': is_strong,
            'issues': issues,
            'suggestions': suggestions,
            'entropy_score': entropy_score,
            'wordlist_check': wordlist_result,
            'breach_check': {'found': is_compromised, 'count': count if isinstance(count, int) else 0}
        }

        # Display formatted results
        self._display_strength_results(result)
        
        return result

    def check_in_wordlists_with_progress(self, password):
        """
        Check if password exists in any of the specified wordlists with progress indicator.
        Returns dict with 'found' status and wordlist name if found.
        """
        progress = ProgressIndicator()
        result = {
            'found': False,
            'wordlist': None,
            'error': None
        }

        # Generate variations to check
        variations = self._generate_common_variations(password)
        
        # Check which wordlists exist
        available_wordlists = [p for p in self.wordlist_paths if Path(p).exists()]
        
        if not available_wordlists:
            show_status("No wordlists found for checking", "warning")
            return result

        show_status(f"Checking against {len(available_wordlists)} wordlist(s)", "info")

        for i, wordlist_path in enumerate(available_wordlists):
            path = Path(wordlist_path)
            progress.simple_progress_bar(i, len(available_wordlists), 
                                       prefix=f"Scanning {path.name}")
            
            try:
                with open(path, 'r', encoding='latin-1', errors='ignore') as f:
                    line_count = 0
                    for line in f:
                        line_count += 1
                        word = line.strip().lower()
                        if word in [v.lower() for v in variations]:
                            result['found'] = True
                            result['wordlist'] = path.name
                            progress.simple_progress_bar(len(available_wordlists), 
                                                       len(available_wordlists), 
                                                       prefix="Wordlist check")
                            show_status(f"⚠️ Password found in {path.name} (line {line_count})", "warning")
                            return result
                        
                        # Show progress for large files
                        if line_count % 100000 == 0:
                            show_status(f"Processed {line_count:,} entries in {path.name}...", "info")

            except Exception as e:
                result['error'] = f"Error reading {path.name}: {str(e)}"
                show_status(f"Error reading {path.name}: {str(e)}", "error")
                continue

        progress.simple_progress_bar(len(available_wordlists), len(available_wordlists), 
                                   prefix="Wordlist check")
        show_status("Password not found in any wordlist", "success")
        return result

    def _display_strength_results(self, result):
        """Display formatted password strength results."""
        print_results_summary({
            'Overall Strength': 'STRONG' if result['is_strong'] else 'WEAK',
            'Entropy Score': f"{result['entropy_score']}/100",
            'Issues Found': len(result['issues']),
            'In Wordlist': 'Yes' if result['wordlist_check']['found'] else 'No',
            'In Breaches': 'Yes' if result['breach_check']['found'] else 'No'
        }, "Password Strength Analysis")

        if result['issues']:
            print("\n❌ Issues Found:")
            for i, issue in enumerate(result['issues'], 1):
                print(f"   {i}. {issue}")

        if result['suggestions']:
            print("\n Suggestions:")
            for i, suggestion in enumerate(result['suggestions'], 1):
                print(f"   {i}. {suggestion}")

    def _generate_common_variations(self, password):
        """Generate common password variations to check against wordlist."""
        variations = {password.lower(), password}

        # Add some common substitutions (leetspeak)
        leetspeak = str.maketrans('aeios', '43105')
        variations.add(password.lower().translate(leetspeak))

        # Add common number suffixes (limited to avoid too many variations)
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
        """Suggest a stronger version of the given password with progress indicator."""
        progress = ProgressIndicator()
        
        show_status("Analyzing current password for improvements", "info")
        progress.spinner("Generating stronger password")
        
        time.sleep(1)  # Simulate processing time
        
        result = self.check_strength(password)

        if result['is_strong']:
            progress.stop_spinner("✅ Password is already strong!")
            return password

        improved = password
        
        # Add missing character types
        if not re.search(self.required_chars['uppercase'], improved):
            improved += secrets.choice(string.ascii_uppercase)
        if not re.search(self.required_chars['lowercase'], improved):
            improved += secrets.choice(string.ascii_lowercase)
        if not re.search(self.required_chars['numbers'], improved):
            improved += secrets.choice(string.digits)
        if not re.search(self.required_chars['special'], improved):
            improved += secrets.choice('!@#$%^&*')

        # Ensure minimum length
        while len(improved) < self.min_length:
            improved += secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*')

        # If still in wordlist, add random characters
        if self.check_in_wordlists(improved)['found']:
            improved += ''.join(secrets.choice(string.ascii_letters + string.digits) 
                                for _ in range(3))

        progress.stop_spinner("✅ Stronger password generated!")
        
        return improved

    def check_in_wordlists(self, password):
        """Quick wordlist check without progress indicator for internal use."""
        result = {
            'found': False,
            'wordlist': None,
            'error': None
        }

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

    def add_to_history(self, password):
        """Add password to the history."""
        self.password_history.add(password)