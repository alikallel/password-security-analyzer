import requests

def check_email_breach(email):
    """Check if the email is in a known breach using HackCheck API."""
    url = f"https://hackcheck.woventeams.com/api/v4/breachedaccount/{email}"
    response = requests.get(url)

    if response.status_code == 200:
        breaches = response.json()
        if breaches:
            print(f"Breaches found for {email}:")
            for breach in breaches:
                print(f"Title: {breach['Title']}, Domain: {breach['Domain']}, Breach Date: {breach['BreachDate']}")
        else:
            print(f"No breaches found for {email}.")
    elif response.status_code == 404:
        print(f"The email {email} has not been involved in any breaches.")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    email = input("Enter email to check: ")
    check_email_breach(email)
