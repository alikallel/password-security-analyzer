import sys
import time
import threading
from itertools import cycle

class ProgressIndicator:
    """A class to handle various types of progress indicators."""
    
    def __init__(self):
        self.is_running = False
        self.spinner_thread = None
    
    def simple_progress_bar(self, current, total, bar_length=50, prefix="Progress"):
        """Display a simple progress bar."""
        percent = float(current) * 100 / total
        arrow = '█' * int(percent/100 * bar_length - 1) + '>'
        spaces = ' ' * (bar_length - len(arrow))
        
        sys.stdout.write(f'\r{prefix}: [{arrow}{spaces}] {percent:.1f}% ({current}/{total})')
        sys.stdout.flush()
        
        if current == total:
            print()  # New line when complete
    
    def spinner(self, message="Processing", spinner_chars=None):
        """Start a spinner animation."""
        if spinner_chars is None:
            spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        
        self.spinner_chars = cycle(spinner_chars)
        self.message = message
        self.is_running = True
        self.spinner_thread = threading.Thread(target=self._spin)
        self.spinner_thread.start()
    
    def _spin(self):
        """Internal method to run the spinner."""
        while self.is_running:
            sys.stdout.write(f'\r{self.message} {next(self.spinner_chars)}')
            sys.stdout.flush()
            time.sleep(0.1)
    
    def stop_spinner(self, final_message=None):
        """Stop the spinner animation."""
        if self.is_running:
            self.is_running = False
            if self.spinner_thread:
                self.spinner_thread.join()
            if final_message:
                sys.stdout.write(f'\r{final_message}\n')
            else:
                sys.stdout.write('\r' + ' ' * (len(self.message) + 5) + '\r')
            sys.stdout.flush()
    
    def dots_animation(self, message="Loading", duration=None):
        """Show a dots animation."""
        dots = cycle(['', '.', '..', '...'])
        start_time = time.time()
        
        try:
            while True:
                if duration and (time.time() - start_time) > duration:
                    break
                sys.stdout.write(f'\r{message}{next(dots)}   ')
                sys.stdout.flush()
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            sys.stdout.write('\r' + ' ' * (len(message) + 10) + '\r')
            sys.stdout.flush()
    
    def estimate_time_remaining(self, start_time, current, total):
        """Estimate time remaining based on current progress."""
        if current == 0:
            return "Calculating..."
        
        elapsed = time.time() - start_time
        rate = current / elapsed
        remaining = (total - current) / rate if rate > 0 else 0
        
        if remaining < 60:
            return f"{remaining:.0f}s remaining"
        elif remaining < 3600:
            return f"{remaining/60:.1f}m remaining"
        else:
            return f"{remaining/3600:.1f}h remaining"

def print_banner():
    """Print a welcome banner."""
    
    banner = """
   _____             ____  __. ____   ____            .__   __   
  /  _  \           |    |/ _| \   \ /   /____   __ __|  |_/  |_ 
 /  /_\  \   ______ |      <    \   Y   /\__  \ |  |  \  |\   __|
/    |    \ /_____/ |    |  \    \     /  / __ \|  |  /  |_|  |  
\____|__  /         |____|__ \    \___/  (____  /____/|____/__|  
        \/                  \/                \/                 
    
        
  
    ╔═══════════════════════════════════════╗
    ║ Security Checker Tool A-K Vault v2.0  ║
    ╠═══════════════════════════════════════╣
    ║ 1. Check Password Strength            ║
    ║ 2. Check Email for Data Breaches      ║
    ║ 3. Get Password Suggestions           ║
    ║ 4. Identify Hash Type                 ║
    ║ 5. Hydra Brute Force Attacks          ║
    ║ Q. Quit                               ║
    ╚═══════════════════════════════════════╝
    
    """
    print(banner)

def get_user_input():
    """Prompt the user to select an option."""
    print("Select an option:")
    print("1. Check password strength")
    print("2. Check if email is breached")
    print("3. Suggest stronger password")
    print("4. Identify hash type")
    print("5. Hydra brute force attacks")
    choice = input("Enter your choice (1/2/3/4/5/Q): ")
    return choice

def show_status(message, status_type="info"):
    """Show status messages with icons."""
    icons = {
        "success": "✅ ",
        "warning": "⚠️ ",
        "error": "❌ ",
    }
    
    icon = icons.get(status_type, "•")
    print(f"{icon} {message}")

def confirm_action(message, default_yes=False):
    """Ask for user confirmation with a clear prompt."""
    suffix = " (Y/n)" if default_yes else " (y/N)"
    response = input(f"⚠️  {message}{suffix}: ").strip().lower()
    
    if default_yes:
        return response != 'n'
    else:
        return response == 'y'

def format_time(seconds):
    """Format seconds into a readable time string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def print_section_header(title, width=50):
    """Print a formatted section header."""
    print("\n" + "="*width)
    print(f" {title.upper()}")
    print("="*width)

def print_results_summary(results_dict, title="Results Summary"):
    """Print a formatted results summary."""
    print_section_header(title)
    
    for key, value in results_dict.items():
        if isinstance(value, bool):
            status = "✅ Yes" if value else "❌ No"
            print(f"{key}: {status}")
        elif isinstance(value, (int, float)):
            print(f"{key}: {value}")
        elif isinstance(value, list):
            print(f"{key}: {len(value)} items")
            for item in value[:3]:  # Show first 3 items
                print(f"  • {item}")
            if len(value) > 3:
                print(f"  ... and {len(value) - 3} more")
        else:
            print(f"{key}: {value}")
    
    print("-" * 50)