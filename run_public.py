import sys
import time
from pyngrok import ngrok
from app import app

# Configure your personal Ngrok account token string context safely
# Replace the string parameter below with your actual token value from dashboard.ngrok.com
NGROK_AUTHTOKEN = "3FrDYkcEVF2LxPr03hRTNRP1p9s_2NfRXRFscgEbrLZPnYcvb"

def launch_public_mirror():
    print("\n[System] Initializing secure public deployment proxy infrastructure...")
    
    try:
        # Bind the token validation profile
        ngrok.set_auth_token(NGROK_AUTHTOKEN)
        
        # Connect an HTTP route channel to local development port 5000
        public_tunnel = ngrok.connect(5000, "http")
        
        print("\n" + "="*54)
        print("YOUR PUBLIC WEBSITE URL IS LIVE!")
        print(f"URL: {public_tunnel.public_url}")
        print("="*54 + "\n")
        print("[Note] Keep this console session open to sustain active proxy routing lines.\n")
        
        # Run app with debug=False to block process re-loaders from dropping the connection
        app.run(debug=False, port=5000)
        
    except Exception as error:
        print(f"\n[Error] Proxy environment startup interrupted: {str(error)}")
        print("[Action] Verify your token assignment variable is correct inside run_public.py.\n")
        sys.exit(1)

if __name__ == "__main__":
    launch_public_mirror()