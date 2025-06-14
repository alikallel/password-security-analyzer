# A-K Password and Email Security Checker

[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)

---

##  Overview

A security tool built to check password strength, verify passwords against breach databases, and check email addresses for exposure in known data breaches. This tool uses custom checks to assess password complexity and integrity while suggesting stronger alternatives.

---

##  Features

### 🔐 Password Strength Checker
* **Length Check** - Ensures the password meets minimum length requirements
* **Character Type Validation** - Checks for uppercase, lowercase, numeric, and special characters
* **Entropy Scoring** - Provides an entropy score to measure password strength
* **Common Patterns Detection** - Identifies easily guessable patterns like `12345`, `qwerty`

### 🌐 Wordlist Check
* **Wordlist Verification** - Checks if the password is found in known wordlists such as rockyou.txt
* **Leetspeak & Variations** - Detects common substitutions and variations

### 📧 Email Breach Check
* **HackCheck API Integration** - Verifies if an email address is part of known data breaches
* **Breach Information** - Provides details about any breaches found

### 🔑 Password Strength Suggestions
* **Improved Password Suggestions** - Suggests stronger passwords based on missing character types
* **Entropy Enhancements** - Increases password entropy by adding missing complexity

---

## 🔧 Technical Details

### Password Strength Checker Class
* **check_strength(password)** - Analyzes password strength and provides suggestions
* **check_in_wordlists(password)** - Verifies password against known wordlists
* **suggest_stronger(password)** - Suggests a stronger password based on the current one

### Email Breach Checker
* **check_email_breach(email)** - Uses HackCheck API to check email against known data breaches

### Hash Identifier
* **identify_hash(hash_input)** - Identifies the type of hash provided using the `hash-identifier` tool. Supports various hash types such as MD5, SHA1, SHA256, etc.

### Hydra Integration
* **Flexible Execution** run_hydra_attack() allows full control over Hydra attack parameters.

* **Quick Attacks** Predefined SSH and FTP brute force functions for fast setup.
* **Output Parsing** Extracts valid credentials from Hydra results automatically.

### Acknowledgments
* **HackCheck API** for breach checking.
* **hash-identifier** tool for hash identification.


This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
