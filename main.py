from utils import print_banner, get_user_input
from password_checker import PasswordChecker
from email_checker import check_email_breach
from hash_identifier import SecurityChecker 
from hydra_integration import HydraIntegration

def main():
    print_banner()  
    checker = PasswordChecker()  
    security_checker = SecurityChecker() 
    hydra = HydraIntegration()
    
    while True:  
        choice = get_user_input()
        if choice.lower() == 'q':
            print("\nThank you for using the password checker. Goodbye!")
            print("\nExiting the Security Checker Tool. Stay safe!")
            break  # Exit the loop if user chooses 'q'
        
        elif choice == '1':
            password = input("Enter password to check: ")
            result = checker.check_strength(password)
            
            # Print results
            if result['is_strong']:
                print("Strong password!")
            else:
                print("\nIssues found:")
                for issue in result['issues']:
                    print(f"- {issue}")
                
                print("\nSuggestions:")
                for suggestion in result['suggestions']:
                    print(f"- {suggestion}")
                
                print(f"\nEntropy Score: {result['entropy_score']}/100")
                
            if result['wordlist_check']['found']:
                print(f"\nWARNING: Password found in wordlist: {result['wordlist_check']['wordlist']}")
        
        elif choice == '2':
            email = input("Enter email to check: ")
            check_email_breach(email)
        
        elif choice == '3':
            password = input("Enter password to suggest improvements: ")
            print("\nGenerating stronger password...")
            stronger_password = checker.suggest_stronger(password)
            print(f"\nSuggested stronger password: {stronger_password}")

        elif choice == '4':
            hash_input = input("Enter the hash to identify: ")
            security_checker.identify_hash(hash_input)

        elif choice == '5':
            # Hydra attack menu
            hydra_menu(hydra)

        else:
            print("Invalid choice. Please choose 1, 2, 3, 4, 5, or Q.")

def hydra_menu(hydra):
    """Display Hydra attack menu and handle user choices."""
    print("\n" + "="*50)
    print(" HYDRA BRUTE FORCE ATTACKS")
    print("="*50)
    print("1. Quick SSH Attack")
    print("2. Quick FTP Attack")
    print("3. Custom Attack (Full Configuration)")
    print("4. Show Available Wordlists")
    print("5. Hydra Help")
    print("6. Back to Main Menu")
    
    # Legal warning
    print("\n⚠️  LEGAL WARNING:")
    print("Only use on systems you own or have explicit permission to test!")
    print("Unauthorized access is illegal and unethical.")
    
    hydra_choice = input("\nEnter your choice (1-6): ").strip()
    
    if hydra_choice == '1':
        # Quick SSH Attack
        target = input("Enter target IP/hostname: ").strip()
        if not target:
            print("❌ Target is required!")
            return
        
        username = input("Enter username (or press Enter for common usernames): ").strip()
        username = username if username else None
        
        # Ask for custom passwords
        use_custom = input("Use custom passwords? (y/N): ").strip().lower() == 'y'
        custom_passwords = None
        
        if use_custom:
            custom_passwords = []
            print("Enter passwords (one per line, empty line to finish):")
            while True:
                pwd = input("Password: ").strip()
                if not pwd:
                    break
                custom_passwords.append(pwd)
        
        confirm = input(f"\n⚠️  Confirm SSH attack on {target}? (y/N): ").strip().lower()
        if confirm == 'y':
            hydra.quick_ssh_attack(target, username, custom_passwords)
        else:
            print("Attack cancelled.")
    
    elif hydra_choice == '2':
        # Quick FTP Attack
        target = input("Enter target IP/hostname: ").strip()
        if not target:
            print("❌ Target is required!")
            return
        
        username = input("Enter username (or press Enter for common usernames): ").strip()
        username = username if username else None
        
        confirm = input(f"\n⚠️  Confirm FTP attack on {target}? (y/N): ").strip().lower()
        if confirm == 'y':
            hydra.quick_ftp_attack(target, username)
        else:
            print("Attack cancelled.")
    
    elif hydra_choice == '3':
        # Custom Attack (Full Configuration)
        confirm = input("\n⚠️  Proceed with custom attack configuration? (y/N): ").strip().lower()
        if confirm == 'y':
            hydra.interactive_attack_setup()
        else:
            print("Attack cancelled.")
    
    elif hydra_choice == '4':
        # Show Available Wordlists
        print("\n Available Wordlists:")
        print("-" * 30)
        wordlists = hydra.get_available_wordlists()
        if wordlists:
            for i, wordlist in enumerate(wordlists, 1):
                try:
                    # Get file size
                    size = os.path.getsize(wordlist)
                    size_mb = size / (1024 * 1024)
                    print(f"{i}. {wordlist} ({size_mb:.1f} MB)")
                except:
                    print(f"{i}. {wordlist}")
        else:
            print("❌ No wordlists found!")
            print("Install wordlists: sudo apt install wordlists")
    
    elif hydra_choice == '5':
        # Hydra Help
        hydra.show_hydra_help()
    
    elif hydra_choice == '6':
        # Back to main menu
        return
    
    else:
        print("Invalid choice. Please choose 1-6.")
    
    # Ask if user wants to continue with Hydra menu
    if hydra_choice != '6':
        continue_hydra = input("\nReturn to Hydra menu? (Y/n): ").strip().lower()
        if continue_hydra != 'n':
            hydra_menu(hydra)

if __name__ == "__main__":
    import os
    main()