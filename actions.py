import requests
import time

def get_response_time(url: str) -> str:
    if not url.startswith('http'):
        url = 'https://' + url
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        end_time = time.time()
        duration = end_time - start_time
        return f"{duration:.2f} seconds"
    except Exception as e:
        return f"Error: {str(e)}"

def calculate(expression: str) -> str:
    try:
        # Safety: limiting the scope of eval to math
        allowed_names = {
            "abs": abs, "round": round, "min": min, "max": max, "pow": pow,
            "int": int, "float": float
        }
        # A very basic safety check - in production use a safer parser
        code = compile(expression, "<string>", "eval")
        for names in code.co_names:
            if names not in allowed_names:
                raise NameError(f"Use of {names} is not allowed")
        return str(eval(code, {"__builtins__": {}}, allowed_names))
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

import wikipedia

def web_search(query: str) -> str:
    try:
        search_results = wikipedia.search(query)
        if not search_results:
            return f"No results found for '{query}'."
        
        # Iterate through search results and try to get summaries until we have 3
        combined_results = []
        
        for page_title in search_results:
            if len(combined_results) >= 3:
                break
                
            try:
                # Use fewer sentences per result to keep context short
                summary = wikipedia.summary(page_title, sentences=2, auto_suggest=False)
                combined_results.append(f"Result ('{page_title}'):\n{summary}")
            except Exception:
                # PageError, DisambiguationError, etc. - skip and try next
                continue

        if not combined_results:
             return f"No readable results found for '{query}'. Try a different keyword."

        return "\n\n".join(combined_results)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Search is ambiguous. Options: {e.options[:5]}"
    except Exception as e:
        return f"Error searching: {str(e)}"

def get_weather(city: str) -> str:
    try:
        # wttr.in format "%C %t": Condition + Temperature
        # e.g. "Partly cloudy +10°C"
        url = f"https://wttr.in/{city}?format=%C+%t"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return f"Current weather in {city}: {response.text.strip()}"
        else:
            return f"Could not get weather for {city}. Status: {response.status_code}"
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

available_actions = {
    "get_response_time": get_response_time,
    "calculate": calculate,
    "web_search": web_search,
    "get_weather": get_weather
}
