from enum import StrEnum, Enum
from threading import Thread
from time import sleep
from typing import Any, List, Optional

from gi.repository import GLib
from .TwitchCore import TwitchCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.PluginManager.InputBases import Input
from GtkHelper.GenerativeUI.ComboRow import ComboRow
from GtkHelper.ComboRow import SimpleComboRowItem, BaseComboRowItem

from loguru import logger as log

from ..constants import (
    CHAT_MODE_UPDATE_INTERVAL_SECONDS,
    ERROR_DISPLAY_DURATION_SECONDS,
)


class Icons(StrEnum):
    FOLLOWER = "follower_mode"
    SUBSCRIBER = "subscriber_mode"
    EMOTE = "emote_mode"
    SLOW = "slow_mode"


class ChatModeOptions(Enum):
    FOLLOWER = SimpleComboRowItem("follower_mode", "Follower Only")
    SUBSCRIBER = SimpleComboRowItem("subscriber_mode", "Subscriber Only")
    EMOTE = SimpleComboRowItem("emote_mode", "Emote Only")
    SLOW = SimpleComboRowItem("slow_mode", "Slow Mode")


class ChatMode(TwitchCore):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.icon_keys = [Icons.FOLLOWER, Icons.SUBSCRIBER, Icons.EMOTE, Icons.SLOW]
        self.current_icon = self.get_icon(Icons.FOLLOWER)
        self.icon_name = Icons.FOLLOWER

    def create_event_assigners(self) -> None:
        self.event_manager.add_event_assigner(
            EventAssigner(
                id="chat-toggle",
                ui_label="Chat Toggle",
                default_event=Input.Key.Events.DOWN,
                callback=self._on_toggle_chat,
            )
        )

    def create_generative_ui(self) -> None:
        self._chat_select_row = ComboRow(
            action_core=self,
            var_name="chat.mode",
            default_value=ChatModeOptions.FOLLOWER.value,
            items=[
                ChatModeOptions.FOLLOWER.value,
                ChatModeOptions.SUBSCRIBER.value,
                ChatModeOptions.EMOTE.value,
                ChatModeOptions.SLOW.value,
            ],
            title="chat-toggle-dropdown",
            complex_var_name=True,
            on_change=self._change_chat_mode,
        )

    def on_ready(self) -> None:
        Thread(
            target=self._update_chat_mode, daemon=True, name="update_chat_mode"
        ).start()

    def get_config_rows(self) -> List[Any]:
        return [self._chat_select_row.widget]

    def _change_chat_mode(self, _: Any, new: str, __: Any) -> None:
        self.icon_name = Icons(new)
        self.current_icon = self.get_icon(self.icon_name)
        self.display_icon()

    def _update_icon(self, mode: str, enabled: bool) -> None:
        # TODO: Custom icons for enabled/disabled
        label = "Enabled" if enabled else "Disabled"
        GLib.idle_add(lambda: self.set_center_label(label))

    def _update_chat_mode(self) -> None:
        while self.get_is_present():
            mode: Optional[str] = None
            try:
                chat_settings = self.backend.get_chat_settings()
                mode = self._chat_select_row.get_selected_item().get_value()
                if mode:
                    enabled = chat_settings.get(mode)
                    self._update_icon(mode, enabled)
            except Exception as ex:
                log.error(
                    f"Failed to update chat mode status{f' for {mode}' if mode else ''}: {ex}"
                )
                self.show_error(ERROR_DISPLAY_DURATION_SECONDS)
            sleep(CHAT_MODE_UPDATE_INTERVAL_SECONDS)

    def _on_toggle_chat(self, _: Any) -> None:
        item = self._chat_select_row.get_selected_item().get_value()
        try:
            resp = self.backend.toggle_chat_mode(item)
            self._update_icon(item, resp)
        except Exception as ex:
            log.error(f"Failed to toggle chat mode '{item}': {ex}")
            self.show_error(ERROR_DISPLAY_DURATION_SECONDS)
