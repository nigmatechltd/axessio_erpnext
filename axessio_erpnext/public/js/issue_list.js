
// Copyright (c) 2025, Nigma Tech Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.listview_settings["Issue"] = {
	
	get_indicator: function (doc) {
		const status_colors = {
            beauftragt: "darkgrey",
            "nicht begonnen": "darkgrey",
            "erledigt": "green",
           "angefangen": "darkgrey",
            "wiederkehrend": "darkgrey",
			
		};
		return [__(doc.status), status_colors[doc.status], "status,=," + doc.status];
	},

};
