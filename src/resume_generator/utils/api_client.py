"""OpenAI-compatible API client utilities"""
import requests
import json
from ..config import OPENAI_API_BASE_URL, OPENAI_API_KEY, MAX_TOKENS, TEMPERATURE


class APIClient:
    """Client for OpenAI-compatible API requests"""
    
    def __init__(self, base_url=None, api_key=None):
        self.base_url = base_url or OPENAI_API_BASE_URL
        self.api_key = api_key or OPENAI_API_KEY
        self.headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def _make_request(self, messages, stream=False, temperature=None, max_tokens=None):
        """
        Make a request to the API.
        
        Args:
            messages (list): List of message dictionaries
            stream (bool): Whether to stream the response
            temperature (float): Temperature for response generation
            max_tokens (int): Maximum tokens in response
            
        Returns:
            requests.Response: API response
        """
        data = {
            "messages": messages,
            "temperature": temperature or TEMPERATURE,
            "max_tokens": max_tokens or MAX_TOKENS,
            "stream": stream
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                stream=stream
            )
            response.raise_for_status()
            return response
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise Exception("API authentication failed. Please check your OPENAI_API_KEY.")
            elif response.status_code == 403:
                raise Exception("API access forbidden. Please check your API key permissions.")
            else:
                raise Exception(f"API request failed: {e}")
    
    def query(self, prompt, stream=False, temperature=None, max_tokens=None):
        """
        Query the API with a prompt.
        
        Args:
            prompt (str): User prompt
            stream (bool): Whether to stream the response
            temperature (float): Temperature for response generation
            max_tokens (int): Maximum tokens in response
            
        Returns:
            str or dict or generator: API response content
        """
        messages = [{"role": "user", "content": prompt}]
        response = self._make_request(messages, stream, temperature, max_tokens)
        
        if stream:
            return self._handle_streaming_response(response)
        else:
            return self._handle_standard_response(response)
    
    def _handle_standard_response(self, response):
        """Handle standard (non-streaming) API response"""
        try:
            result = response.json()
            choice = result["choices"][0]
            content = choice["message"]["content"]
            
            # Handle reasoning content if available (e.g., from o1 models)
            reasoning = choice["message"].get("reasoning")
            if reasoning:
                return {
                    "content": content,
                    "reasoning": reasoning
                }
            return content
            
        except KeyError:
            raise Exception("Invalid API response format. Please check your API endpoint configuration.")
    
    def _handle_streaming_response(self, response):
        """Handle streaming API response"""
        full_content = ""
        reasoning_content = ""
        
        try:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(data_str)
                            choice = data.get('choices', [{}])[0]
                            delta = choice.get('delta', {})
                            
                            # Standard content
                            if 'content' in delta and delta['content']:
                                full_content += delta['content']
                            
                            # Reasoning content (for models like o1)
                            if 'reasoning' in delta and delta['reasoning']:
                                reasoning_content += delta['reasoning']
                                
                        except json.JSONDecodeError:
                            continue  # Skip malformed lines
            
            # Return reasoning if available
            if reasoning_content:
                return {
                    "content": full_content,
                    "reasoning": reasoning_content
                }
            return full_content
            
        except Exception as e:
            raise Exception(f"Streaming response error: {str(e)}")


# Global client instance
_client = None

def get_api_client():
    """Get the global API client instance"""
    global _client
    if _client is None:
        _client = APIClient()
    return _client


def query_model(prompt, stream=False, temperature=None, max_tokens=None):
    """
    Convenience function to query the model.
    
    Args:
        prompt (str): User prompt
        stream (bool): Whether to stream the response
        temperature (float): Temperature for response generation
        max_tokens (int): Maximum tokens in response
        
    Returns:
        str or dict: API response content
    """
    client = get_api_client()
    return client.query(prompt, stream, temperature, max_tokens)