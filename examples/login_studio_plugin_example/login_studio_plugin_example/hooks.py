app_name = "login_studio_plugin_example"
app_title = "Login Studio Plugin Example"
app_publisher = "Thinkspedia"
app_description = "Example plugin for Login Studio: a layout, a context hook, a slot and a stylesheet"
app_email = "helpdesk@thinkspedia.com"
app_license = "mit"

required_apps = ["login_studio"]

# Folders inside this package; each sub-folder with a layout.json is one layout
login_studio_layouts = ["login_layouts"]

# Called with the ls dict before rendering; add your own data under ls["extra"]
login_studio_context = ["login_studio_plugin_example.login.add_context"]

# slot name -> function(ls) returning HTML
login_studio_slots = {
	"below_form": "login_studio_plugin_example.login.help_notice",
}

# Same-site paths or https URLs, added to the login page
login_studio_assets = {
	"css": ["/assets/login_studio_plugin_example/css/login_studio_plugin_example.css"],
}
