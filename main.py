from utils import print_banner, get_user_input
from password_checker import PasswordChecker
from email_checker import check_email_breach
from hash_identifier import SecurityChecker 

def main():
    print_banner()  
    checker = PasswordChecker()  
    security_checker = SecurityChecker() 
    
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

        else:
            print("Invalid choice. Please choose 1, 2, or 3.")

if __name__ == "__main__":
    main()
