def print_banner():
    """Print a welcome banner using pyfiglet."""
    
    banner = """
   _____             ____  __. ____   ____            .__   __   
  /  _  \           |    |/ _| \   \ /   /____   __ __|  |_/  |_ 
 /  /_\  \   ______ |      <    \   Y   /\__  \ |  |  \  |\   __|
/    |    \ /_____/ |    |  \    \     /  / __ \|  |  /  |_|  |  
\____|__  /         |____|__ \    \___/  (____  /____/|____/__|  
        \/                  \/                \/                 
    """
    print(banner)

def get_user_input():
    """Prompt the user to select an option."""
    print("Select an option:")
    print("1. Check password strength")
    print("2. Check if email is breached")
    print("3. Suggest stronger password")
    choice = input("Enter your choice (1/2/3): ")
    return choice
