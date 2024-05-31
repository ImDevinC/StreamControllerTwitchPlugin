from plugins.com_imdevinc_StreamControllerTwitchPlugin.TwitchActionBase import TwitchActionBase
import os
from gi.repository import Adw

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")


class SendMessage(TwitchActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_row = Adw.EntryRow(
            title=self.plugin_base.lm.get("actions.message.message"))

    def on_ready(self):
        self.set_media(media_path=os.path.join(
            self.plugin_base.PATH, "assets", "chat.png"), size=0.85)

    def get_config_rows(self):
        super_rows = super().get_config_rows()

        self.connect_signals()

        self.load_configs()

        super_rows.append(self.message_row)
        return super_rows

    def connect_signals(self):
        self.message_row.connect("notify::text", self.on_message_change)

    def disconnect_signals(self):
        try:
            self.message_row.disconnect_by_func(self.on_message_change)
        except TypeError:
            pass

    def load_configs(self):
        self.disconnect_signals()
        settings = self.get_settings()
        if 'message' in settings:
            self.message_row.set_text(settings['message'])
        self.connect_signals()

    def on_message_change(self, entry, _):
        settings = self.get_settings()
        settings['message'] = entry.get_text()
        self.set_settings(settings)

    def on_key_down(self):
        settings = self.get_settings()
        message = settings['message'] if 'message' in settings else None
        if message:
            try:
                self.plugin_base.backend.send_message(message)
            except:
                self.show_error()
