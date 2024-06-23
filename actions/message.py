
import os
import gi
from gi.repository import Adw

from loguru import logger as log

from plugins.com_imdevinc_StreamControllerTwitchPlugin.TwitchActionBase import TwitchActionBase

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")


class SendMessage(TwitchActionBase):

    def on_ready(self):
        self.set_media(media_path=os.path.join(
            self.plugin_base.PATH, "assets", "chat.png"), size=0.85)

    def get_config_rows(self):
        self.message_row = Adw.EntryRow(
            title=self.plugin_base.lm.get("actions.message.message"))

        self.message_row.connect("notify::text", self._on_message_change)

        self._load_config()

        super_rows = super().get_config_rows()
        super_rows.append(self.message_row)
        return super_rows

    def _load_config(self):
        settings = self.get_settings()
        self.message_row.set_text(settings.get('message', ''))

    def _on_message_change(self, entry, _):
        settings = self.get_settings()
        settings['message'] = entry.get_text()
        self.set_settings(settings)

    def on_key_down(self):
        settings = self.get_settings()
        message = settings.get('message', '')
        try:
            self.plugin_base.backend.send_message(message)
        except Exception as ex:
            log.error(ex)
            self.show_error(3)
