import logging
import numpy as np
from typing import Callable

_LOGGER = logging.getLogger(__name__)

class Event:
    """Base for events"""

    LEDFX_SHUTDOWN = 'shutdown'
    DEVICE_UPDATE = 'device_update'
    GRAPH_UPDATE = 'graph_update'

    def __init__(self, type : str):
        self.event_type = type

    def to_dict(self):
        return self.__dict__

class DeviceUpdateEvent(Event):
    """Event emmitted when a device's pixels are updated"""

    def __init__(self, device_id : str, pixels : np.ndarray):
        super().__init__(Event.DEVICE_UPDATE)
        self.device_id = device_id
        self.pixels = pixels.T.tolist()

class GraphUpdateEvent(Event):
    """Event emmitted when a device's pixels are updated"""

    def __init__(self, graph_id : str, melbank : np.ndarray, frequencies : np.ndarray):
        super().__init__(Event.GRAPH_UPDATE)
        self.graph_id = graph_id
        self.melbank = melbank.tolist()
        self.frequencies = frequencies.tolist()

class LedFxShutdownEvent(Event):
    """Event emmitted when LedFx is shutting down"""

    def __init__(self):
        super().__init__(Event.LEDFX_SHUTDOWN)
        
class EventListener:
    def __init__(self, callback: Callable, event_filter: dict={}):
        self.callback = callback
        self.filter = event_filter

    def filter_event(self, event):
        event_dict = event.to_dict() 
        for filter_key in self.filter:
            if event_dict.get(filter_key) != self.filter[filter_key]:
                return True
        
        return False

class Events:

    def __init__(self, ledfx):
        self._ledfx = ledfx
        self._listeners = {}

    def fire_event(self, event : Event) -> None:

        listeners = self._listeners.get(event.event_type, [])
        if not listeners:
            return

        for listener in listeners:
            if not listener.filter_event(event):
                self._ledfx.loop.call_soon(listener.callback, event)

    def add_listener(self, callback: Callable, event_type: str, event_filter: dict={}) -> None:

        listener = EventListener(callback, event_filter)
        if event_type in self._listeners:
            self._listeners[event_type].append(listener)
        else:
            self._listeners[event_type] = [listener]

        def remove_listener() -> None:
            self._remove_listener(event_type, listener)

        return remove_listener

    def _remove_listener(self, event_type: str, listener: Callable) -> None:

        try:
            self._listeners[event_type].remove(listener)
            if not self._listeners[event_type]:
                self._listeners.pop(event_type)
        except (KeyError, ValueError):
            _LOGGER.warning("Failed to remove event listener %s", listener)
