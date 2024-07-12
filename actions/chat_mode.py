import time
import threading
import os

import gi
from gi.repository import Gtk, Adw

from loguru import logger as log

from plugins.com_imdevinc_StreamControllerTwitchPlugin.TwitchActionBase import TwitchActionBase

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

icons = {
    'Follower Mode': 'follower.png',
    'Subscriber Mode': 'subscriber.png',
    'Emote Mode': 'emote.png',
    'Slow Mode': 'slow.png',
}


class ChatMode(TwitchActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mode: str = None

    def on_ready(self):
        self._load_config()
        self.set_media(media_path=os.path.join(
            self.plugin_base.PATH, "assets", icons[self._mode]), size=0.85)
        threading.Thread(target=self.get_mode_status, daemon=True,
                         name="get_mode_status").start()

    def get_config_rows(self):
        super_rows = super().get_config_rows()
        self.action_model = Gtk.StringList()
        self.mode_row = Adw.ComboRow(model=self.action_model, title=self.plugin_base.lm.get(
            "actions.chat_mode.mode_row.label"))

        index = 0
        found = -1
        for key in icons:
            self.action_model.append(key)
            if key == self._mode:
                found = index
            index += 1

        if found < 0:
            self.mode_row.set_selected(Gtk.INVALID_LIST_POSITION)

        self.mode_row.connect("notify::selected", self._on_change_mode)
        self.mode_row.set_selected(found)
        super_rows.append(self.mode_row)
        return super_rows

    def on_key_down(self):
        try:
            settings = self.get_settings()
            mode = settings['mode']
            parsed_mode = mode.lower().replace(' ', '_')
            resp = self.plugin_base.backend.toggle_chat_mode(parsed_mode)
            if resp:
                self.set_bottom_label(resp)
        except Exception as ex:
            log.error(ex)
            self.show_error(3)

    def _load_config(self):
        settings = self.get_settings()
        mode = settings.get('mode')
        for key in icons:
            if key == mode:
                self._mode = key
                return
        self._mode = 'Follower Mode'

    def _on_change_mode(self, *_):
        settings = self.get_settings()
        selected_index = self.mode_row.get_selected()
        if selected_index == Gtk.INVALID_LIST_POSITION:
            return
        settings['mode'] = self.action_model[selected_index].get_string()
        self._mode = settings['mode']
        self.set_media(media_path=os.path.join(
            self.plugin_base.PATH, "assets", icons[settings['mode']]), size=0.85)
        self.set_settings(settings)
        self.set_top_label(self._mode.split(' ')[0])

    def get_mode_status(self):
        while True:
            try:
                if self._mode is None:
                    raise Exception(f'no config: {self._mode}')
                existing_modes = self.plugin_base.backend.get_chat_settings()
                parsed_mode = self._mode.lower().replace(' ', '_')
                self.set_bottom_label(str(existing_modes[parsed_mode]))
                self.set_top_label(self._mode.split(' ')[0])
            except Exception as ex:
                log.error(ex)
                self.set_bottom_label('-')
                self.show_error(3)
            time.sleep(3)
