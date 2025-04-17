from enum import StrEnum

from loguru import logger as log

from .TwitchCore import TwitchCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.PluginManager.InputBases import Input


class Icons(StrEnum):
    CLIP = "camera"


class Clip(TwitchCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon_keys = [Icons.CLIP]
        self.current_icon = self.get_icon(Icons.CLIP)
        self.icon_name = Icons.CLIP
        self.has_configuration = False

    def create_event_assigners(self):
        self.event_manager.add_event_assigner(
            EventAssigner(
                id="clip",
                ui_label="Clip",
                default_event=Input.Key.Events.DOWN,
                callback=self._on_clip
            )
        )

    def _on_clip(self, _):
        try:
            self.backend.create_clip()
        except Exception as ex:
            log.error(ex)
            self.show_error(3)
