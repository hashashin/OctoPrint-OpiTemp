$(function() {
    function OpitempViewModel(parameters) {
        var self = this;
        var text = "";
        self.opitempModel = parameters[0];
        self.global_settings = parameters[1];
        self.Temp = ko.observable();
        self.Temp(text);

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "opitemp") {
                return;
            }
            text = "&#127818;" + data.soctemp+ "&#8451;";
            self.Temp(text);
        };
    }

    ADDITIONAL_VIEWMODELS.push([
        OpitempViewModel,
        ["navigationViewModel"],
        ["#navbar_plugin_opitemp"]
    ]);
});
