from gi.repository import Gtk, Adw
import gi

from src.backend.PluginManager.ActionBase import ActionBase

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")


class TwitchActionBase(ActionBase):
    def get_config_rows(self) -> list:
        authed = self.plugin_base.backend.is_authed()
        if not authed:
            label = "actions.base.credentials.no-credentials"
            css_style = "twitch-controller-red"
        else:
            label = "actions.base.credentials.authenticated"
            css_style = "twitch-controller-green"

        self.status_label = Gtk.Label(
            label=self.plugin_base.lm.get(label), css_classes=[css_style])
        self.client_id = Adw.EntryRow(
            title=self.plugin_base.lm.get("actions.base.twitch_client_id"))
        self.client_secret = Adw.PasswordEntryRow(
            title=self.plugin_base.lm.get("actions.base.twitch_client_secret"))
        self.auth_button = Gtk.Button(label=self.plugin_base.lm.get(
            "actions.base.credentials.validate"))
        self.auth_button.set_margin_top(10)
        self.auth_button.set_margin_bottom(10)

        self.client_id.connect("notify::text", self._on_change_client_id)
        self.client_secret.connect(
            "notify::text", self._on_change_client_secret)
        self.auth_button.connect("clicked", self._on_auth_clicked)

        group = Adw.PreferencesGroup()
        group.set_title(self.plugin_base.lm.get(
            "actions.base.credentials.title"))
        group.add(self.client_id)
        group.add(self.client_secret)
        group.add(self.status_label)
        group.add(self.auth_button)

        self.load_config()
        return [group]

    def get_custom_config_area(self):
        label = Gtk.Label(
            use_markup=True,
            label=f"{self.plugin_base.lm.get('actions.info.link.label')} <a href=\"https://github.com/ImDevinC/StreamControllerTwitchPlugin\">{self.plugin_base.lm.get('actions.info.link.text')}</a>")
        return label

    def load_config(self):
        settings = self.plugin_base.get_settings()
        client_id = settings.setdefault("client_id", "")
        client_secret = settings.setdefault("client_secret", "")

        self.client_id.set_text(client_id)
        self.client_secret.set_text(client_secret)

        self.plugin_base.set_settings(settings)

    def _on_change_client_id(self, entry, _):
        settings = self.plugin_base.get_settings()
        settings["client_id"] = entry.get_text()
        self.plugin_base.set_settings(settings)

    def _on_change_client_secret(self, entry, _):
        settings = self.plugin_base.get_settings()
        settings["client_secret"] = entry.get_text()
        self.plugin_base.set_settings(settings)

    def _on_auth_clicked(self, _):
        settings = self.plugin_base.get_settings()
        client_id = settings.get('client_id')
        client_secret = settings.get('client_secret')
        if not client_id or not client_secret:
            self._set_status(self.plugin_base.lm.get(
                "actions.base.credentials.no-credentials"), True)
            return
        self.plugin_base.backend.update_client_credentials(
            client_id, client_secret, self.on_auth_completed)

    def _set_status(self, message: str, is_error: bool = False):
        print(f'updating message: {message}')
        self.status_label.set_label(message)
        if is_error:
            self.status_label.remove_css_class("twitch-controller-green")
            self.status_label.add_css_class("twitch-controller-red")
        else:
            self.status_label.remove_css_class("twitch-controller-red")
            self.status_label.add_css_class("twitch-controller-green")

    def on_auth_completed(self, success: bool) -> None:
        print(f'on_auth_completed: {success}')
        if success:
            self._set_status(self.plugin_base.lm.get(
                "actions.base.credentials.authenticated"), False)
        else:
            self._set_status(self.plugin_base.lm.get(
                "actions.base.credentials.failed"), True)
