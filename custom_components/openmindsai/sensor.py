import requests
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.core import callback

DEFAULT_NAME = "hassio_mindsdb_response"
DEFAULT_INPUT_NAME = "gpt_input"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional("input_name", default=DEFAULT_INPUT_NAME): cv.string,
    vol.Required("session_cookie"): cv.string,
    vol.Required("model"): cv.string,
})

def query_message(query, token_budget=4096 - 500):
    return query

def ask(session_cookie, model, query, token_budget=4096 - 500):
    message = query_message(query, token_budget=token_budget)

    url = f"https://cloud.mindsdb.com/api/projects/mindsdb/models/{model}/predict"
    cookies = {"session": session_cookie}
    data = {"data": [{"text": message}]}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, cookies=cookies, headers=headers)
    response_json = response.json()
    response_message = response_json[0]["response"]

    return response_message

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    name = config[CONF_NAME]
    input_name = config["input_name"]
    session_cookie = config["session_cookie"]
    model = config["model"]

    async_add_entities([MindsDBResponseSensor(hass, name, input_name, session_cookie, model)], True)

class MindsDBResponseSensor(SensorEntity):
    def __init__(self, hass, name, input_name, session_cookie, model):
        self._hass = hass
        self._name = name
        self._input_name = input_name
        self._session_cookie = session_cookie
        self._model = model
        self._state = None
        self._response_text = ""

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {"response_text": self._response_text}

    @callback
    async def async_ask(self, entity_id, old_state, new_state):
        new_query = new_state.state
        if new_query:
            response = await self._hass.async_add_executor_job(ask, self._session_cookie, self._model, new_query)
            self._response_text = response
            self._state = "query_executed"
            self.async_write_ha_state()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self._hass.helpers.event.async_track_state_change(
                f"input_text.{self._input_name}", self.async_ask
            )
        )

    async def async_update(self):
        pass
