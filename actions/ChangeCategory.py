from .TwitchCore import TwitchCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.PluginManager.InputBases import Input

from GtkHelper.GenerativeUI.ComboRow import ComboRow

from loguru import logger as log


class ChangeCategory(TwitchCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = True

    def create_event_assigners(self):
        self.event_manager.add_event_assigner(
            EventAssigner(
                id="change-category",
                ui_label="change-category",
                default_event=Input.Key.Events.DOWN,
                callback=self._on_change_category
            )
        )

    def create_generative_ui(self):
        self.message_row = ComboRow(
            action_core=self,
            var_name="category",
            title="category-title",
            auto_add=False,
            enable_search=True,
            complex_var_name=False,
            on_change=self._on_change_category,
            items=[],
            default_value=0,
            can_reset=False
        )

    def get_config_rows(self):
        return [self.message_row.widget]

    def _on_change_category(self, _, new, __):
        log.debug(new)
