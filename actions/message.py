
import os
import gi
from gi.repository import Adw

from loguru import logger as log

from src.backend.PluginManager.ActionBase import ActionBase

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")


class SendMessage(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = True

    def on_ready(self):
        self.set_media(media_path=os.path.join(
            self.plugin_base.PATH, "assets", "chat.png"), size=0.85)

    def get_config_rows(self):
        self.message_row = Adw.EntryRow(
            title=self.plugin_base.lm.get("actions.message.message"))
        self.channel_row = Adw.EntryRow(
            title=self.plugin_base.lm.get("actions.message.channel"))

        self.message_row.connect("notify::text", self._on_message_change)
        self.channel_row.connect("notify::text", self._on_channel_change)

        self._load_config()

        super_rows = super().get_config_rows()
        super_rows.append(self.message_row)
        super_rows.append(self.channel_row)
        return super_rows

    def _load_config(self):
        settings = self.get_settings()
        self.message_row.set_text(settings.get('message', ''))
        self.channel_row.set_text(settings.get('channel', ''))

    def _on_message_change(self, entry, _):
        settings = self.get_settings()
        settings['message'] = entry.get_text()
        self.set_settings(settings)

    def _on_channel_change(self, entry, _):
        settings = self.get_settings()
        settings['channel'] = entry.get_text()
        self.set_settings(settings)

    def on_key_down(self):
        settings = self.get_settings()
        message = settings.get('message', '')
        channel = settings.get('channel', '')
        try:
            self.plugin_base.backend.send_message(message, channel)
        except Exception as ex:
            log.error(ex)
            self.show_error(3)
