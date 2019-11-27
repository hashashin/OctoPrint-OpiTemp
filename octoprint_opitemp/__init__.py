# coding=utf-8
from __future__ import absolute_import

import sys
import re
import platform
import octoprint.plugin
from octoprint.util import RepeatedTimer

class OpitempPlugin(octoprint.plugin.SettingsPlugin,
                    octoprint.plugin.StartupPlugin,
                    octoprint.plugin.AssetPlugin,
                    octoprint.plugin.TemplatePlugin):
    temp = 0
    color = "black"

    def get_settings_defaults(self):
        return dict(rate=10.0,
                    emoji="&#127818;",
                    tsp1=50,
                    tsp2=65,
                    socfile="/etc/armbianmonitor/datasources/soctemp")

    def interval(self):
        return float(self._settings.get(['rate']))

    def on_after_startup(self):
        t = RepeatedTimer(self.interval, self.check_temp)
        t.start()
        self._logger.info("OpiTemp READY")

    def get_template_configs(self):
        return [
            dict(type='navbar', custom_bindings=True),
            dict(type='settings', custom_bindings=False)
        ]

    def set_text_color(self):
        atemp = float(self.temp)
        tsp1 = float(self._settings.get(['tsp1']))
        tsp2 = float(self._settings.get(['tsp2']))
        if tsp1 == 0 or tsp2 == 0:
            self.color = "inherit"
            return
        if atemp < tsp1:
            self.color = "green"
        elif atemp >= tsp1 and atemp < tsp2:
            self.color = "orange"
        elif atemp >= tsp2:
            self.color = "red"

    def check_temp(self):
        from sarge import run, Capture
        import os.path
        try:
            soc_file = self._settings.get(["socfile"])
            if os.path.isfile(soc_file):
                p = run("cat " + soc_file, stdout=Capture())
                p = p.stdout.text
                match = re.search(r"(\d+)", p)
            else:
                self._logger.error("OpiTemp: can't determine the temperature,"
                                   + " are you sure you're using Armbian?")
                return
            # lazy fix for #3, yeah I known...
            if platform.release().startswith("4") or platform.release().startswith("5"):
                self.temp = "{0:.1f}".format(float(match.group(1))/1000)
            elif platform.release().startswith("3"):
                self.temp = match.group(1)
            else:
                self._logger.warning("OpiTemp: unknown kernel version!")
                self.temp = 0
            self.set_text_color()
            self._plugin_manager.send_plugin_message(self._identifier,
                                                     dict(soctemp=self.temp,
                                                          emoji=self._settings.get(["emoji"]),
                                                          color=self.color
                                                         )
                                                    )
            self._logger.debug("OpiTemp REFRESH")
        except Exception as e:
            self._logger.warning("OpiTemp REFRESH FAILED: {0}".format(e))

    def get_assets(self):
        return dict(
            js=["js/opitemp.js"]
        )

    def get_update_information(self):
        return dict(
            opitemp=dict(
                displayName="Opitemp Plugin",
                displayVersion=self._plugin_version,

                type="github_release",
                user="hashashin",
                repo="OctoPrint-OpiTemp",
                current=self._plugin_version,

                pip="https://github.com/hashashin/OctoPrint-OpiTemp/archive/{target_version}.zip"
            )
        )


__plugin_name__ = "Opitemp Plugin"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = OpitempPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config":
            __plugin_implementation__.get_update_information
    }
