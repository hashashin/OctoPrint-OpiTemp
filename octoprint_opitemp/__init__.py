# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import sys
import re
from octoprint.util import RepeatedTimer
import platform

class OpitempPlugin(octoprint.plugin.SettingsPlugin,
                    octoprint.plugin.StartupPlugin,
                    octoprint.plugin.AssetPlugin,
                    octoprint.plugin.TemplatePlugin):
    temp = 0

    def on_after_startup(self):
        t = RepeatedTimer(10.0, self.check_temp)
        t.start()
        self._logger.info("OpiTemp READY")

    def get_template_vars(self):
        return dict(soctemp=self.temp)

    def get_settings_defaults(self):
        return dict(type="navbar", custom_bindings=True)

    def check_temp(self):
        from sarge import run, Capture
        try:
            p = run("cat /etc/armbianmonitor/datasources/soctemp", stdout=Capture())
            p = p.stdout.text
            match = re.search('(\d+)', p)
            # lazy fix for #3, yeah I known...
            if platform.release().startswith("4"):
                self.temp = "{0:.1f}".format(float(match.group(1))/1000)
            elif platform.release().startswith("3"):
                self.temp = match.group(1)
            else :
                self._logger.warning("OpiTemp: unknown kernel version!")
                self.temp = 0
            self._plugin_manager.send_plugin_message(self._identifier,
                                                     dict(soctemp=self.temp))
            self._logger.debug("OpiTemp REFRESH")
        except Exception as e:
            self._logger.warning("OpiTemp REFRESH FAILED: %s" % e)

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
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }

