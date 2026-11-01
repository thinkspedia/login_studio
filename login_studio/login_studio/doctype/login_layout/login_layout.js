// Copyright (c) 2026, Thinkspedia and contributors
// For license information, please see license.txt

frappe.ui.form.on("Login Layout", {
	refresh(frm) {
		const shipped = frm.doc.source && frm.doc.source !== "Custom";
		frm.set_df_property("template", "read_only", shipped && !frm.is_new());
		frm.set_df_property("css", "read_only", shipped && !frm.is_new());

		if (frm.is_new()) return;

		if (shipped) {
			frm.set_intro(
				__("This layout is shipped by {0} and is read-only. Duplicate it to customize.", [
					frm.doc.source_app,
				]),
				"blue"
			);
		}

		frm.add_custom_button(__("Preview"), () => login_studio_preview(frm.doc.name));
		frm.add_custom_button(__("Duplicate as Custom Layout"), () => duplicate_layout(frm));
	},
});

function duplicate_layout(frm) {
	frappe.prompt(
		[
			{
				fieldname: "layout_name",
				label: __("Layout Name"),
				fieldtype: "Data",
				reqd: 1,
				default: `${frm.doc.name}_custom`,
				description: __("Lowercase letters, numbers and underscores."),
			},
			{
				fieldname: "title",
				label: __("Title"),
				fieldtype: "Data",
				reqd: 1,
				default: __("{0} (Custom)", [frm.doc.title]),
			},
		],
		(values) => {
			frappe.call({
				method: "login_studio.login_studio.doctype.login_layout.login_layout.duplicate_layout",
				args: { source: frm.doc.name, ...values },
				freeze: true,
				callback: (r) => frappe.set_route("Form", "Login Layout", r.message),
			});
		},
		__("Duplicate Layout"),
		__("Duplicate")
	);
}

function login_studio_preview(layout) {
	const url = `/login-studio/preview?layout=${encodeURIComponent(layout)}`;
	const dialog = new frappe.ui.Dialog({
		title: __("Preview: {0}", [layout]),
		size: "extra-large",
		fields: [
			{
				fieldname: "width",
				label: __("Screen Width"),
				fieldtype: "Select",
				options: ["1440", "768", "375"],
				default: "1440",
				change: () => render(),
			},
			{ fieldname: "frame", fieldtype: "HTML" },
		],
		primary_action_label: __("Open in New Tab"),
		primary_action: () => window.open(url, "_blank"),
	});
	// Render at the chosen width, then scale down to fit the dialog so the whole page is visible
	const render = () => {
		const width = parseInt(dialog.get_value("width") || "1440", 10);
		const $wrapper = dialog.fields_dict.frame.$wrapper;
		$wrapper.html(`
			<div class="ls-preview-stage" style="height: 70vh; overflow: hidden; border: 1px solid var(--border-color);
				border-radius: var(--border-radius-md); background: var(--subtle-fg);">
				<iframe src="${url}" title="${__("Login page preview")}"
					style="display: block; border: 0; transform-origin: top left;"></iframe>
			</div>`);
		fit(width);
	};
	const fit = (width) => {
		const $wrapper = dialog.fields_dict.frame.$wrapper;
		const stage = $wrapper.find(".ls-preview-stage")[0];
		// The dialog is still animating in on first render, so wait until the stage has a size
		if (!stage || !stage.clientWidth) {
			setTimeout(() => fit(width), 50);
			return;
		}
		const scale = Math.min(1, stage.clientWidth / width);
		$wrapper.find("iframe").css({
			width: `${width}px`,
			height: `${stage.clientHeight / scale}px`,
			transform: `scale(${scale})`,
			marginLeft: `${(stage.clientWidth - width * scale) / 2}px`,
		});
	};
	dialog.show();
	render();
}
