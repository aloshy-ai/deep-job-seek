import os
import sys
import openai
from colorama import Fore, Back, Style, init

init() # Initialize Colorama for cross-platform compatibility

# Load configuration from environment variables
OPENAI_API_BASE_URL = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def validate_openai_api_key():
    """Validates the OpenAI API key by making a small test request using the openai library."""

    try:
        client = openai.OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE_URL,
            timeout=10.0, # seconds
        )
        
        # Make a small test request to verify credentials
        # Using a dict with type ignore to satisfy the type checker
        client.chat.completions.create(
            model="gpt-3.5-turbo", # This model is generally available and cheap for a test
            messages=[
                {"role": "user", "content": "test"}  # type: ignore
            ],
            max_tokens=1,
            temperature=0
        )
        
        print(f"{Fore.GREEN}✅ SUCCESS: OpenAI API accessible at {OPENAI_API_BASE_URL}{Style.RESET_ALL}")
        return True

    except openai.AuthenticationError:
        print(f"{Fore.RED}❌ ERROR: API authentication failed.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 HINT: Your OPENAI_API_KEY might be incorrect, expired, or lack necessary permissions.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}ACTION: Please double-check your API key on {Style.BRIGHT}https://platform.openai.com/api-keys{Style.RESET_ALL} and ensure it's correctly set in your environment variables.")
        return False
    except openai.APITimeoutError:
        print(f"{Fore.RED}❌ ERROR: API request timed out at {OPENAI_API_BASE_URL}.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 HINT: The API did not respond within the expected time (10 seconds). This can happen due to high server load or slow network.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}ACTION: Try again later. If the issue persists, consider checking the API server's status or your network speed.{Style.RESET_ALL}")
        return False
    except openai.APIConnectionError:
        print(f"{Fore.RED}❌ ERROR: Unable to connect to OpenAI API.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 HINT: Verify your API Key and Base URL. If issues persist, check your internet connection or proxy settings.{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}       Attempted {Fore.CYAN}OPENAI_API_BASE_URL{Style.RESET_ALL}: {Back.BLUE}{Fore.WHITE}{OPENAI_API_BASE_URL}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}       Attempted {Fore.CYAN}OPENAI_API_KEY{Style.RESET_ALL}     : {Back.BLUE}{Fore.WHITE}{f"{OPENAI_API_KEY[:4]}****{OPENAI_API_KEY[-4:]}" if OPENAI_API_KEY and len(OPENAI_API_KEY) > 8 else (OPENAI_API_KEY if OPENAI_API_KEY else 'Not Set')}{Style.RESET_ALL}")
        return False
    except openai.APIStatusError as e:
        print(f"{Fore.RED}❌ ERROR: API request failed with status {e.status_code}.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 HINT: This indicates an issue on the API server's side related to your request.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}ACTION: Review the error message from the API for more details: {e.response}. Common causes include invalid model names, rate limits, or malformed requests.{Style.RESET_ALL}")
        return False
    except Exception as e:
        error_message = str(e)
        if "Client.__init__() got an unexpected keyword argument 'proxies'" in error_message or "api_key client option must be set" in error_message:
            print(f"{Fore.RED}❌ ERROR: There's a problem setting up the OpenAI connection.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 HINT: Please verify your API Key and Base URL.{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}       Attempted {Fore.CYAN}OPENAI_API_BASE_URL{Style.RESET_ALL}: {Back.BLUE}{Fore.WHITE}{OPENAI_API_BASE_URL}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}       Attempted {Fore.CYAN}OPENAI_API_KEY{Style.RESET_ALL}     : {Back.BLUE}{Fore.WHITE}{f"{OPENAI_API_KEY[:4]}****{OPENAI_API_KEY[-4:]}" if OPENAI_API_KEY and len(OPENAI_API_KEY) > 8 else (OPENAI_API_KEY if OPENAI_API_KEY else 'Not Set')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ ERROR: An unexpected error occurred during API validation: {error_message}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 HINT: This might indicate an issue with your OpenAI library installation, an unexpected response from the API, or a configuration problem.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}ACTION: Ensure your 'openai' library is up to date (`pip install --upgrade openai`). If the problem persists, consult the error message for clues or seek support.{Style.RESET_ALL}")
        return False

if __name__ == "__main__":
    # Add src to Python path for local execution if needed
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, '..', '..', '..') # Adjust path to reach 'src' if run directly
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    if not validate_openai_api_key():
        sys.exit(1)