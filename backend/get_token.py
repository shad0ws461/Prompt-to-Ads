import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Load credentials from environment variables instead of committing secrets
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Google Ads API ka scope
SCOPES = ["https://www.googleapis.com/auth/adwords"]

def main():
    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
        }
    }

    # Flow initialize karna localhost redirect ke sath
    flow = InstalledAppFlow.from_client_config(
        client_config, 
        scopes=SCOPES, 
        redirect_uri="http://localhost:8000/api/oauth/callback"
    )

    # Auth URL generate karna
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

    print("\n--- STEP 1: IS LINK KO BROWSER ME OPEN KARO ---")
    print(auth_url)
    print("------------------------------------------------\n")

    code = input("Browser me allow karne ke baad, URL se 'code=' ke aage wala part copy karke yahan paste karo: ").strip()

    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        print("\n--- 🔥 AAPKA REFRESH TOKEN 🔥 ---")
        print(f"Refresh Token: {credentials.refresh_token}")
        print("----------------------------------\n")
    except Exception as e:
        print(f"\nError token nikalne me: {e}")

if __name__ == "__main__":
    main()