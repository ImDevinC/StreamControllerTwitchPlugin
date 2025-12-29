from enum import StrEnum
from typing import Any

from loguru import logger as log

from .TwitchCore import TwitchCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.PluginManager.InputBases import Input

from ..constants import ERROR_DISPLAY_DURATION_SECONDS


class Icons(StrEnum):
    MARKER = "bookmark"


class Marker(TwitchCore):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon_keys = [Icons.MARKER]
        self.current_icon = self.get_icon(Icons.MARKER)
        self.icon_name = Icons.MARKER
        self.has_configuration = False

    def create_event_assigners(self) -> None:
        self.event_manager.add_event_assigner(
            EventAssigner(
                id="marker",
                ui_label="Marker",
                default_event=Input.Key.Events.DOWN,
                callback=self._on_marker,
            )
        )

    def _on_marker(self, _: Any) -> None:
        try:
            self.backend.create_marker()
        except Exception as ex:
            log.error(f"Failed to create stream marker: {ex}")
            self.show_error(ERROR_DISPLAY_DURATION_SECONDS)
