import time
import threading
import gi
from gi.repository import Gtk, Adw

from loguru import logger as log

from plugins.com_imdevinc_StreamControllerTwitchPlugin.TwitchActionBase import TwitchActionBase

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")


class ChatMode(TwitchActionBase):
    def on_ready(self):
        threading.Thread(target=self.get_mode_status, daemon=True,
                         name="get_mode_status").start()

    def get_config_rows(self):
        super_rows = super().get_config_rows()
        self.action_model = Gtk.StringList()
        self.mode_row = Adw.ComboRow(model=self.action_model, title=self.plugin_base.lm.get(
            "actions.chat_mode.mode_row.label"))

        self.action_model.append('Follower Mode')
        self.action_model.append('Subscriber Mode')
        self.action_model.append('Emote Mode')
        self.action_model.append('Slow Mode')

        self.mode_row.connect("notify::selected", self._on_change_mode)
        self._load_config()
        super_rows.append(self.mode_row)
        return super_rows

    def on_key_down(self):
        settings = self.get_settings()
        mode = settings['mode']
        parsed_mode = mode.lower().replace(' ', '_')
        resp = self.plugin_base.backend.toggle_chat_mode(parsed_mode)
        if resp:
            self.set_bottom_label(resp)

    def _load_config(self):
        settings = self.get_settings()
        for i, name in enumerate(self.action_model):
            if name.get_string() == settings.get('mode'):
                self.mode_row.set_selected(i)
                return

        self.mode_row.set_selected(Gtk.INVALID_LIST_POSITION)

    def _on_change_mode(self, *_):
        settings = self.get_settings()
        selected_index = self.mode_row.get_selected()
        if not selected_index:
            return
        settings['mode'] = self.action_model[selected_index].get_string()
        self.set_settings(settings)
        self.set_top_label(
            self.action_model[selected_index].get_string().split(' ')[0])

    def get_mode_status(self):
        while True:
            try:
                settings = self.get_settings()
                mode = settings['mode']
                existing_modes = self.plugin_base.backend.get_chat_settings()
                parsed_mode = mode.lower().replace(' ', '_')
                self.set_bottom_label(str(existing_modes[parsed_mode]))
                self.set_top_label(mode.split(' ')[0])
            except:
                self.set_bottom_label('-')
                pass
            time.sleep(3)
