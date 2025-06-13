import subprocess
import os
import sys
from pathlib import Path
import time

class HydraIntegration:
    def __init__(self):
        self.common_wordlists = [
            "/usr/share/wordlists/rockyou.txt",
            "/usr/share/wordlists/fasttrack.txt",
            "/usr/share/wordlists/dirb/common.txt",
            "/usr/share/wordlists/metasploit/common_passwords.txt"
        ]
        
        self.common_usernames = [
            "admin", "administrator", "root", "user", "guest", "test",
            "demo", "anonymous", "ftp", "mail", "www", "web", "ssh"
        ]
        
        self.service_ports = {
            "ssh": 22,
            "ftp": 21,
            "telnet": 23,
            "smtp": 25,
            "http": 80,
            "https": 443,
            "pop3": 110,
            "imap": 143,
            "snmp": 161,
            "mysql": 3306,
            "rdp": 3389,
            "vnc": 5900
        }

    def check_hydra_installed(self):
        """Check if Hydra is installed on the system."""
        try:
            result = subprocess.run(
                ["hydra", "-h"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            return True
        except FileNotFoundError:
            return False

    def get_available_wordlists(self):
        """Get list of available wordlists on the system."""
        available = []
        for wordlist in self.common_wordlists:
            if Path(wordlist).exists():
                available.append(wordlist)
        return available

    def create_custom_wordlist(self, passwords):
        """Create a temporary wordlist file from provided passwords."""
        temp_file = "/tmp/custom_wordlist.txt"
        try:
            with open(temp_file, 'w') as f:
                for password in passwords:
                    f.write(f"{password}\n")
            return temp_file
        except Exception as e:
            print(f"Error creating custom wordlist: {e}")
            return None

    def create_username_list(self, usernames=None):
        """Create a username list file."""
        temp_file = "/tmp/usernames.txt"
        users = usernames or self.common_usernames
        try:
            with open(temp_file, 'w') as f:
                for username in users:
                    f.write(f"{username}\n")
            return temp_file
        except Exception as e:
            print(f"Error creating username list: {e}")
            return None

    def run_hydra_attack(self, target, service, username=None, userlist=None, 
                        password=None, passlist=None, port=None, threads=16, 
                        verbose=False, stop_on_success=True):
        """
        Run Hydra attack with specified parameters.
        
        Args:
            target: Target IP or hostname
            service: Service to attack (ssh, ftp, http, etc.)
            username: Single username to try
            userlist: Path to username list file
            password: Single password to try
            passlist: Path to password list file
            port: Custom port (optional)
            threads: Number of parallel threads
            verbose: Enable verbose output
            stop_on_success: Stop after first successful login
        """
        
        if not self.check_hydra_installed():
            return {
                'success': False,
                'error': 'Hydra is not installed. Install it using: sudo apt install hydra'
            }

        # Build Hydra command
        cmd = ["hydra"]
        
        # Add username options
        if username:
            cmd.extend(["-l", username])
        elif userlist:
            cmd.extend(["-L", userlist])
        else:
            # Create default username list
            default_userlist = self.create_username_list()
            if default_userlist:
                cmd.extend(["-L", default_userlist])
        
        # Add password options
        if password:
            cmd.extend(["-p", password])
        elif passlist:
            cmd.extend(["-P", passlist])
        else:
            # Use first available wordlist
            available_wordlists = self.get_available_wordlists()
            if available_wordlists:
                cmd.extend(["-P", available_wordlists[0]])
            else:
                return {
                    'success': False,
                    'error': 'No wordlists available. Please specify a password list.'
                }
        
        # Add other options
        cmd.extend(["-t", str(threads)])
        
        if stop_on_success:
            cmd.append("-f")
        
        if verbose:
            cmd.append("-V")
        
        # Add port if specified
        if port:
            cmd.extend(["-s", str(port)])
        elif service in self.service_ports:
            cmd.extend(["-s", str(self.service_ports[service])])
        
        # Add target and service
        cmd.extend([target, service])
        
        print(f"Running Hydra command: {' '.join(cmd)}")
        print("This may take a while depending on the wordlist size...")
        
        try:
            # Run Hydra attack
            start_time = time.time()
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                'success': True,
                'stdout': process.stdout,
                'stderr': process.stderr,
                'return_code': process.returncode,
                'duration': duration,
                'command': ' '.join(cmd)
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Hydra attack timed out after 1 hour'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error running Hydra: {str(e)}'
            }

    def parse_hydra_output(self, output):
        """Parse Hydra output to extract successful logins."""
        successful_logins = []
        lines = output.split('\n')
        
        for line in lines:
            if '[' in line and ']' in line and 'login:' in line and 'password:' in line:
                # Extract login credentials from output
                try:
                    # Example: [22][ssh] host: 192.168.1.1   login: admin   password: password123
                    parts = line.split()
                    login_idx = parts.index('login:')
                    password_idx = parts.index('password:')
                    
                    username = parts[login_idx + 1]
                    password = parts[password_idx + 1]
                    
                    successful_logins.append({
                        'username': username,
                        'password': password,
                        'full_line': line.strip()
                    })
                except (ValueError, IndexError):
                    continue
        
        return successful_logins

    def quick_ssh_attack(self, target, username=None, custom_passwords=None):
        """Quick SSH brute force attack."""
        print(f"\n Starting SSH brute force attack on {target}")
        
        # Use custom passwords if provided
        passlist = None
        if custom_passwords:
            passlist = self.create_custom_wordlist(custom_passwords)
        
        result = self.run_hydra_attack(
            target=target,
            service="ssh",
            username=username,
            passlist=passlist,
            threads=4,  # Lower threads for SSH to avoid detection
            verbose=True
        )
        
        return self.process_attack_result(result)

    def quick_ftp_attack(self, target, username=None):
        """Quick FTP brute force attack."""
        print(f"\n Starting FTP brute force attack on {target}")
        
        result = self.run_hydra_attack(
            target=target,
            service="ftp",
            username=username,
            verbose=True
        )
        
        return self.process_attack_result(result)

    def quick_http_attack(self, target, path="/login", method="POST"):
        """Quick HTTP form brute force attack."""
        print(f"\n Starting HTTP brute force attack on {target}")
        
        # Note: HTTP form attacks require more specific parameters
        # This is a basic implementation
        result = self.run_hydra_attack(
            target=target,
            service="http-post-form",
            verbose=True
        )
        
        return self.process_attack_result(result)

    def process_attack_result(self, result):
        """Process and display attack results."""
        if not result['success']:
            print(f"❌ Attack failed: {result['error']}")
            return result
        
        print(f"\n  Attack completed in {result['duration']:.2f} seconds")
        
        # Parse successful logins
        successful_logins = self.parse_hydra_output(result['stdout'])
        
        if successful_logins:
            print(f"\n✅ Found {len(successful_logins)} successful login(s):")
            for login in successful_logins:
                print(f"    Username: {login['username']}")
                print(f"    Password: {login['password']}")
                print(f"    Full: {login['full_line']}")
                print()
        else:
            print("\n❌ No successful logins found")
        
        # Show verbose output if needed
        if result['stderr']:
            print(f"\n⚠️  Errors/Warnings:")
            print(result['stderr'])
        
        return result

    def interactive_attack_setup(self):
        """Interactive setup for Hydra attacks."""
        print("\n Hydra Attack Configuration")
        print("=" * 40)
        
        # Get target
        target = input("Enter target IP/hostname: ").strip()
        if not target:
            print("❌ Target is required!")
            return None
        
        # Get service
        print("\nAvailable services:")
        services = list(self.service_ports.keys())
        for i, service in enumerate(services, 1):
            print(f"{i}. {service} (port {self.service_ports[service]})")
        
        try:
            service_choice = int(input(f"\nSelect service (1-{len(services)}): "))
            service = services[service_choice - 1]
        except (ValueError, IndexError):
            print("❌ Invalid service selection!")
            return None
        
        # Get username option
        print("\nUsername options:")
        print("1. Single username")
        print("2. Username list (common usernames)")
        print("3. Custom username list")
        
        username_choice = input("Select option (1-3): ").strip()
        username = None
        userlist = None
        
        if username_choice == "1":
            username = input("Enter username: ").strip()
        elif username_choice == "2":
            userlist = self.create_username_list()
        elif username_choice == "3":
            userlist_path = input("Enter path to username list: ").strip()
            if not Path(userlist_path).exists():
                print("❌ Username list file not found!")
                return None
            userlist = userlist_path
        
        # Get password option
        print("\nPassword options:")
        print("1. Single password")
        print("2. Wordlist (rockyou.txt)")
        print("3. Custom wordlist")
        print("4. Custom password list")
        
        password_choice = input("Select option (1-4): ").strip()
        password = None
        passlist = None
        
        if password_choice == "1":
            password = input("Enter password: ").strip()
        elif password_choice == "2":
            available_wordlists = self.get_available_wordlists()
            if available_wordlists:
                passlist = available_wordlists[0]
                print(f"Using: {passlist}")
            else:
                print("❌ No wordlists found!")
                return None
        elif password_choice == "3":
            passlist_path = input("Enter path to wordlist: ").strip()
            if not Path(passlist_path).exists():
                print("❌ Wordlist file not found!")
                return None
            passlist = passlist_path
        elif password_choice == "4":
            passwords = []
            print("Enter passwords (one per line, empty line to finish):")
            while True:
                pwd = input("Password: ").strip()
                if not pwd:
                    break
                passwords.append(pwd)
            
            if passwords:
                passlist = self.create_custom_wordlist(passwords)
        
        # Get additional options
        threads = input("Number of threads (default 16): ").strip()
        threads = int(threads) if threads.isdigit() else 16
        
        port = input(f"Custom port (default {self.service_ports.get(service, 'auto')}): ").strip()
        port = int(port) if port.isdigit() else None
        
        verbose = input("Verbose output? (y/N): ").strip().lower() == 'y'
        
        # Run the attack
        print(f"\n Starting {service.upper()} attack on {target}...")
        
        result = self.run_hydra_attack(
            target=target,
            service=service,
            username=username,
            userlist=userlist,
            password=password,
            passlist=passlist,
            port=port,
            threads=threads,
            verbose=verbose
        )
        
        return self.process_attack_result(result)

    def show_hydra_help(self):
        """Show help information for Hydra functionality."""
        help_text = """
 Hydra Integration Help
========================

This tool integrates THC-Hydra for password brute-force attacks.

Supported Services:
- SSH (port 22)
- FTP (port 21)
- Telnet (port 23)
- HTTP/HTTPS (ports 80/443)
- SMTP (port 25)
- POP3 (port 110)
- IMAP (port 143)
- MySQL (port 3306)
- RDP (port 3389)
- VNC (port 5900)

Quick Attack Options:
1. SSH Attack - Optimized for SSH services
2. FTP Attack - Optimized for FTP services
3. Custom Attack - Full configuration options

Requirements:
- Hydra must be installed: sudo apt install hydra
- Wordlists recommended: /usr/share/wordlists/rockyou.txt

⚠️  Legal Notice:
Only use this tool on systems you own or have explicit permission to test.
Unauthorized access to computer systems is illegal.
        """
        print(help_text)