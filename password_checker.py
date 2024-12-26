import re
import hashlib

def check_password_strength(password):
    """Check if password is strong."""
    if len(password) < 8:
        return "Weak: Password should be at least 8 characters."
    if not re.search(r'[A-Z]', password):
        return "Weak: Password should contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return "Weak: Password should contain at least one lowercase letter."
    if not re.search(r'[0-9]', password):
        return "Weak: Password should contain at least one number."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "Weak: Password should contain at least one special character."
    return "Strong"

def check_password_in_wordlist(password, wordlist_path="/usr/share/wordlists/rockyou.txt"):
    """Check if password is in the wordlist (e.g., rockyou)."""
    try:
        with open(wordlist_path, "r", encoding="latin-1") as file:
            for line in file:
                if password == line.strip():
                    return "Weak: Password is too common (in wordlist)."
    except FileNotFoundError:
        return "Wordlist not found."
    return "Not in wordlist."

def suggest_stronger_password(password):
    """Suggest a stronger password based on the given password."""
    stronger_password = password + "2024!"  # Simple suggestion (append numbers/special chars)
    return f"Suggested stronger password: {stronger_password}"

if __name__ == "__main__":
    password = input("Enter password to check: ")
    print(check_password_strength(password))
    print(check_password_in_wordlist(password))
    print(suggest_stronger_password(password))
