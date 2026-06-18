AUTOCODE_DEFAULTS = {
    "embeddings_dir": "embeddings",
    "window": [2, 2],
    "min_examples": 5,
    "confidence_threshold": 0.6,
    "child_threshold": 0.4,
    "api_base": "http://localhost:1234/v1",
    "api_key": "",
    "api_model": "text-embedding-nomic-embed-text-v1.5",
}

def get_autocode_settings(settings):
    """Returns the effective autocode settings: AUTOCODE_DEFAULTS overridden
    by whatever is set in the `autocode` table in settings.yaml.
    """
    return {**AUTOCODE_DEFAULTS, **(settings.get("autocode") or {})}

def set_autocode_setting(settings, key, value):
    """Sets a key in the `autocode` table of an in-memory settings dict
    (does not write to disk), creating the table if needed.
    """
    if not settings.get("autocode"):
        settings["autocode"] = {}
    settings["autocode"][key] = value
