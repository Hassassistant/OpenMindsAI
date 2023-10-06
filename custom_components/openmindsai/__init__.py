import requests
"""OpenMindsAI custom component."""

DOMAIN = "openmindsai"

ATTR_NAME = "prompt"
MODEL_NAME = "model"
SESSION_COOKIE_NAME = "session"
DEFAULT_PROMPT = "Give an example prompt for ChatGPT"
DEFAULT_MODEL = "gpt4hassio"
DEFAULT_SESSION_COOKIE = "gpt4hassio"


def setup(hass, config):

    """Set up is called when Home Assistant is loading our component."""

    def ask(call):
        """Handle the service call."""
        prompt = call.data.get(ATTR_NAME, DEFAULT_PROMPT)
        model = call.data.get(MODEL_NAME, DEFAULT_MODEL)
        session_cookie = call.data.get(SESSION_COOKIE_NAME, DEFAULT_SESSION_COOKIE)
        

        hass.states.set("openmindsai.response", "querying", {
            "response" : ""
        })

        ask_to_ia(session_cookie, model, prompt)

        return True
        
    def query_message(query, token_budget=4096 - 500):
        return query

    def ask_to_ia(session_cookie, model, query, token_budget=4096 - 500):
        message = query_message(query, token_budget=token_budget)
    
        url = f"https://cloud.mindsdb.com/api/projects/mindsdb/models/{model}/predict"
        cookies = {"session": session_cookie}
        data = {"data": [{"text": message}]}
        headers = {"Content-Type": "application/json"}
    
        response = requests.post(url, json=data, cookies=cookies, headers=headers)
        response_json = response.json()
        response_message = response_json[0]["response"]
    
        hass.states.set("openmindsai.response", "done", {
            "response" : response_message
        })

    hass.services.register(DOMAIN, "ask", ask)

    # Return boolean to indicate that initialization was successful.
    return True