from utils import print_banner
from password_checker import check_password_strength, check_password_in_wordlist, suggest_stronger_password
from email_checker import check_email_breach
from utils import get_user_input

def main():
    print_banner()  # Display the custom ASCII banner
    choice = get_user_input()

    if choice == '1':
        password = input("Enter password to check: ")
        print(check_password_strength(password))
        print(check_password_in_wordlist(password))
    elif choice == '2':
        email = input("Enter email to check: ")
        check_email_breach(email)
    elif choice == '3':
        password = input("Enter password to suggest improvements: ")
        print(suggest_stronger_password(password))
    else:
        print("Invalid choice. Please choose 1, 2, or 3.")

if __name__ == "__main__":
    main()
