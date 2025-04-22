
// Copyright (c) 2025, Nigma Tech Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.listview_settings["HD Ticket"] = {
	
	get_indicator: function (doc) {
		const status_colors = {
            beauftragt: "darkgrey",
            "nicht begonnen": "darkgrey",
            "erledigt": "green",
           "angefangen": "darkgrey",
            "wiederkehrend": "darkgrey",
            "Open": "orange"
			
		};
		return [__(doc.status), status_colors[doc.status], "status,=," + doc.status];
	},

};
