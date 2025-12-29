from enum import StrEnum

from .TwitchCore import TwitchCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.PluginManager.InputBases import Input

from GtkHelper.GenerativeUI.EntryRow import EntryRow

from loguru import logger as log

from constants import ERROR_DISPLAY_DURATION_SECONDS


class Icons(StrEnum):
    CHAT = "chat"


class SendMessage(TwitchCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon_keys = [Icons.CHAT]
        self.current_icon = self.get_icon(Icons.CHAT)
        self.icon_name = Icons.CHAT
        self.has_configuration = True

    def create_event_assigners(self):
        self.event_manager.add_event_assigner(
            EventAssigner(
                id="chat",
                ui_label="Message",
                default_event=Input.Key.Events.DOWN,
                callback=self._on_chat,
            )
        )

    def create_generative_ui(self):
        self.message_row = EntryRow(
            action_core=self,
            var_name="chat.message_text",
            default_value="",
            title="chat-message-text",
            auto_add=False,
            complex_var_name=True,
        )
        self.channel_row = EntryRow(
            action_core=self,
            var_name="chat.channel_id",
            default_value="",
            title="chat-channel-id",
            auto_add=False,
            complex_var_name=True,
        )

    def get_config_rows(self):
        return [self.message_row.widget, self.channel_row.widget]

    def _on_chat(self, _):
        message = self.message_row.get_value()
        channel = self.channel_row.get_value()
        try:
            self.backend.send_message(message, channel)
        except Exception as ex:
            log.error(f"Failed to send chat message to channel '{channel}': {ex}")
            self.show_error(ERROR_DISPLAY_DURATION_SECONDS)
