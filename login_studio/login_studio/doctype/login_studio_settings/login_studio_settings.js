// Copyright (c) 2026, Thinkspedia and contributors
// For license information, please see license.txt

frappe.ui.form.on("Login Studio Settings", {
	refresh(frm) {
		frm.add_custom_button(__("Preview Login Page"), () => {
			if (frm.is_dirty()) {
				frappe.msgprint(__("Save the settings first; the preview uses the saved values."));
				return;
			}
			window.open(
				`/login-studio/preview?layout=${encodeURIComponent(frm.doc.active_layout || "")}`,
				"_blank"
			);
		});
	},
});
