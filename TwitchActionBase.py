from src.backend.PluginManager.ActionBase import ActionBase
from gi.repository import Gtk, Adw
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")


class TwitchActionBase(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_base.backend.set_auth_callback(self.auth_callback)
        self.status_label = None

    def get_config_rows(self) -> list:
        validate_token = self.plugin_base.backend.validate_token()
        if not validate_token:
            label = "actions.base.status.no-credentials"
        else:
            label = "actions.base.credentials.authenticated"
        self.status_label = Gtk.Label(
            label=self.plugin_base.lm.get(label), css_classes=["red"])
        self.client_id = Adw.EntryRow(
            title=self.plugin_base.lm.get("actions.base.twitch_client_id"))
        self.client_secret = Adw.PasswordEntryRow(
            title=self.plugin_base.lm.get("actions.base.twitch_client_secret"))
        self.auth_button = Gtk.Button(label=self.plugin_base.lm.get(
            "actions.base.credentials.validate"))
        self.auth_button.set_margin_top(10)
        self.auth_button.set_margin_bottom(10)

        self.client_id.connect("notify::text", self.on_change_client_id)
        self.client_secret.connect(
            "notify::text", self.on_change_client_secret)
        self.auth_button.connect("clicked", self.on_auth_clicked)

        group = Adw.PreferencesGroup()
        group.set_title(self.plugin_base.lm.get(
            "actions.base.credentials.title"))
        group.add(self.client_id)
        group.add(self.client_secret)
        group.add(self.status_label)
        group.add(self.auth_button)

        self.load_config_defaults()
        return [group]

    def load_config_defaults(self):
        settings = self.plugin_base.get_settings()
        client_id = settings.setdefault("client_id", "")
        client_secret = settings.setdefault("client_secret", "")

        self.client_id.set_text(client_id)
        self.client_secret.set_text(client_secret)

        self.plugin_base.set_settings(settings)

    def on_change_client_id(self, entry, _):
        settings = self.plugin_base.get_settings()
        settings["client_id"] = entry.get_text()
        self.plugin_base.set_settings(settings)

    def on_change_client_secret(self, entry, _):
        settings = self.plugin_base.get_settings()
        settings["client_secret"] = entry.get_text()
        self.plugin_base.set_settings(settings)

    def on_auth_clicked(self, _):
        settings = self.plugin_base.get_settings()
        if not 'client_id' in settings or not 'client_secret' in settings:
            self.set_status(self.plugin_base.lm.get(
                "actions.base.credentials.no-credenials"))
            return
        self.plugin_base.backend.start_auth_flow(
            settings['client_id'], settings['client_secret'])

    def set_status(self, message: str, is_error: bool = False):
        if not self.status_label:
            return
        self.status_label.set_label(message)
        if is_error:
            self.status_label.remove_css_class("green")
            self.status_label.add_css_class("red")
        else:
            self.status_label.remove_css_class("red")
            self.status_label.add_css_class("green")

    def auth_callback(self, access_token: str, refresh_token: str, message: str, error: bool):
        self.set_status(message, error)
        settings = self.plugin_base.get_settings()
        if error:
            settings['access_token'] = ''
            settings['refresh_token'] = ''
        else:
            settings['access_token'] = access_token
            settings['refresh_token'] = refresh_token
        self.plugin_base.set_settings(settings)
