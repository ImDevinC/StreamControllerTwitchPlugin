from enum import StrEnum, Enum

from loguru import logger as log

from .TwitchCore import TwitchCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.PluginManager.InputBases import Input
from GtkHelper.GenerativeUI.ComboRow import ComboRow
from GtkHelper.ComboRow import SimpleComboRowItem, BaseComboRowItem


class Icons(StrEnum):
    AD = "money"


class PlayAd(TwitchCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon_keys = [Icons.AD]
        self.current_icon = self.get_icon(Icons.AD)
        self.icon_name = Icons.AD
        self.has_configuration = True

    def create_generative_ui(self):
        options = [SimpleComboRowItem(str(x), f"{x} seconds")
                   for x in [30, 60, 90, 120]]
        self._time_row = ComboRow(
            action_core=self,
            var_name="ad.duration",
            default_value=options[0],
            items=options,
            title="ad-options-dropdown",
            complex_var_name=True
        )

    def get_config_rows(self):
        return [self._time_row.widget]

    def create_event_assigners(self):
        self.event_manager.add_event_assigner(
            EventAssigner(
                id="play-ad",
                ui_label="Play Ad",
                default_event=Input.Key.Events.DOWN,
                callback=self._on_play_ad
            )
        )

    def _on_play_ad(self, _):
        try:
            time = self._time_row.get_selected_item().get_value()
            self.backend.play_ad(int(time))
        except Exception as ex:
            log.error(ex)
            self.show_error(3)
