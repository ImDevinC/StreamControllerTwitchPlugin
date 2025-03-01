import os
import gi
from gi.repository import Adw, Gtk

from loguru import logger as log

from plugins.com_imdevinc_StreamControllerTwitchPlugin.TwitchActionBase import TwitchActionBase

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

options = [30, 60, 90, 120]


class PlayAd(TwitchActionBase):
    _time: int = 30

    def on_ready(self):
        self.set_media(media_path=os.path.join(
            self.plugin_base.PATH, "assets", "money.png"), size=0.85)

    def _load_config(self):
        settings = self.get_settings()
        time = settings.get("time")
        for value in options:
            if value == time:
                self._time = value
                return
        self._time = 30

    def _on_change_time(self, *_):
        settings = self.get_settings()
        selected_index = self.time_row.get_selected()
        time = self.action_model[selected_index].get_string()
        settings["time"] = int(time)
        self.set_settings(settings)

    def get_config_rows(self):
        super_rows = super().get_config_rows()
        self.action_model = Gtk.StringList()
        self.time_row = Adw.ComboRow(
            model=self.action_model, title=self.plugin_base.lm.get("actions.play_ad.time.label"))
        self._load_config()

        index = 0
        found = -1
        for value in options:
            self.action_model.append(str(value))
            if value == self._time:
                found = index
            index += 1
        if found < 0:
            self.time_row.set_selected(0)

        self.time_row.connect("notify::selected", self._on_change_time)
        self.time_row.set_selected(found)
        super_rows.append(self.time_row)
        return super_rows

    def on_key_down(self):
        try:
            self.plugin_base.backend.play_ad(self._time)
        except Exception as ex:
            log.error(ex)
            self.show_error(3)
