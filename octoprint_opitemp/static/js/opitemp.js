$(function() {
    function OpitempViewModel(parameters) {
        var self = this;
        var text = "";
        self.opitempModel = parameters[0];
        self.global_settings = parameters[1];
        self.Temp = ko.observable();
        self.Temp(text);
        self.Color = ko.observable();

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "opitemp") {
                return;
            }
            text = data.emoji + data.soctemp;
            self.Temp(text);
            self.Color(data.color);
        };
    }
    ADDITIONAL_VIEWMODELS.push([
        OpitempViewModel,
        ["navigationViewModel"],
        ["#navbar_plugin_opitemp"]
    ]);

});
