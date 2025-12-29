from enum import StrEnum, Enum
from datetime import datetime, timedelta
from threading import Thread
from time import sleep

from gi.repository import GLib
from GtkHelper.GenerativeUI.SwitchRow import SwitchRow
from .TwitchCore import TwitchCore
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.PluginManager.InputBases import Input
from src.backend.PluginManager.PluginSettings.Asset import Color

from loguru import logger as log


class Icons(StrEnum):
    DELAY = "delay"


class Colors(StrEnum):
    DEFAULT = "default"
    WARNING = "warning"
    ALERT = "alert"


class AdSchedule(TwitchCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon_keys = [Icons.DELAY]
        self.current_icon = self.get_icon(Icons.DELAY)
        self.icon_name = Icons.DELAY
        self.color_keys = [Colors.DEFAULT, Colors.WARNING, Colors.ALERT]
        self.current_color = self.get_color(Colors.DEFAULT)
        self.has_configuration = True
        self._next_ad: datetime = datetime.now()
        self._snoozes: int = -1

    def on_ready(self):
        super().on_ready()
        Thread(
            target=self._get_ad_schedule, daemon=True, name="get_ad_schedule"
        ).start()
        Thread(
            target=self._update_ad_timer, daemon=True, name="update_ad_timer"
        ).start()

    def create_event_assigners(self):
        self.event_manager.add_event_assigner(
            EventAssigner(
                id="snooze-ad",
                ui_label="Snooze Ad",
                default_event=Input.Key.Events.DOWN,
                callback=self._on_snooze_ad,
            )
        )

    def create_generative_ui(self):
        self._skip_ad_switch = SwitchRow(
            action_core=self,
            var_name="ad.snooze",
            default_value=True,
            title="ad-snooze",
            subtitle="Snoozes ad for 5 minutes when pushed",
            complex_var_name=True,
        )

    def get_config_rows(self):
        return [self._skip_ad_switch.widget]

    def _update_background_color(self, color: str):
        def _update():
            self.current_color = self.get_color(color)
            self.display_color()

        GLib.idle_add(_update)

    def _update_ad_timer(self):
        while self.get_is_present():
            self.display_color()
            now = datetime.now()
            snooze_label = (
                str(self._snoozes)
                if (self._snoozes >= 0 and self._skip_ad_switch.get_active())
                else ""
            )
            GLib.idle_add(lambda: self.set_bottom_label(snooze_label))
            try:
                if self._next_ad < now:
                    self._update_background_color(Colors.DEFAULT)
                    GLib.idle_add(lambda: self.set_center_label(""))
                    continue
                diff = (self._next_ad - now).total_seconds()
                time_label = self._convert_seconds_to_hh_mm_ss(diff)
                GLib.idle_add(lambda: self.set_center_label(time_label))
                if diff <= 60:
                    self._update_background_color(Colors.ALERT)
                    continue
                if diff <= 300:
                    self._update_background_color(Colors.WARNING)
                    continue
                self._update_background_color(Colors.DEFAULT)
            except TypeError:
                # There is a known issue where the default timestamp returned from
                # the twitch API is an invalid datetime object and causes an error.
                # Ignoring it here
                pass
            except Exception as ex:
                log.error(ex)
            sleep(1)

    def _get_ad_schedule(self):
        while self.get_is_present():
            try:
                schedule, snoozes = self.backend.get_next_ad()
                self._next_ad = schedule
                self._snoozes = snoozes
                self._update_ad_timer()
            except Exception as ex:
                log.error(ex)
                self.show_error(3)
            sleep(30)

    def _convert_seconds_to_hh_mm_ss(self, seconds) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        return f"{int(hours):02}:{int(minutes):02}:{int(remaining_seconds):02}"

    def _on_snooze_ad(self, _):
        if not self._skip_ad_switch.get_active():
            return
        try:
            self.backend.snooze_ad()
        except Exception as ex:
            log.error(ex)
            self.show_error(3)
