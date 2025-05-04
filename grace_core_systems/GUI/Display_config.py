# grace_core_systems/GUI/display_config.py

def get_display_config():
    return {
        "theme": "default",
        "layout": "standard",
        "breakpoints": {
            "mobile": 480,
            "tablet": 768,
            "desktop": 1024
        }
    }

active_config = get_display_config()
