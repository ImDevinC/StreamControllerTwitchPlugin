from enum import StrEnum
from typing import Any, List

from .TwitchCore import TwitchCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.PluginManager.InputBases import Input

from GtkHelper.GenerativeUI.EntryRow import EntryRow

from loguru import logger as log

from ..constants import ERROR_DISPLAY_DURATION_SECONDS


class Icons(StrEnum):
    CHAT = "chat"


class Shoutout(TwitchCore):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon_keys = [Icons.CHAT]
        self.current_icon = self.get_icon(Icons.CHAT)
        self.icon_name = Icons.CHAT
        self.has_configuration = True

    def create_event_assigners(self) -> None:
        self.event_manager.add_event_assigner(
            EventAssigner(
                id="shoutout",
                ui_label="Shoutout",
                default_event=Input.Key.Events.DOWN,
                callback=self._on_shoutout,
            )
        )

    def create_generative_ui(self) -> None:
        self.username_row = EntryRow(
            action_core=self,
            var_name="shoutout.username",
            default_value="",
            title="shoutout-username",
            auto_add=False,
            complex_var_name=True,
        )

    def get_config_rows(self) -> List[Any]:
        return [self.username_row.widget]

    def _on_shoutout(self, _: Any) -> None:
        username = self.username_row.get_value()

        if not username or username.strip() == "":
            log.error("No username configured for shoutout")
            self.show_error(ERROR_DISPLAY_DURATION_SECONDS)
            return

        try:
            self.backend.send_shoutout(username)
        except Exception as ex:
            log.error(f"Failed to send shoutout to '{username}': {ex}")
            self.show_error(ERROR_DISPLAY_DURATION_SECONDS)
