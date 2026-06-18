from qualitative_coding.migrations.migration import QCMigration
from qualitative_coding.helpers import read_settings

AUTOCODE_KEY_MAP = {
    "autocode_embeddings_dir": "embeddings_dir",
    "autocode_window": "window",
    "autocode_min_examples": "min_examples",
    "autocode_confidence_threshold": "confidence_threshold",
    "autocode_child_threshold": "child_threshold",
    "autocode_api_base": "api_base",
    "autocode_api_key": "api_key",
    "autocode_api_model": "api_model",
}

class Migrate_2_0_0(QCMigration):
    """Introduces the `autocode` settings table, grouping the flat
    `autocode_*` settings keys (added ad hoc as the autocode feature was
    developed) under a single nested table. Every project gets an
    `autocode` table, whether or not autocode is in use, so that the
    settings structure is consistent across all projects.
    """

    _version = "2.0.0"

    def apply(self, settings_path):
        settings = read_settings(settings_path)
        autocode = dict(settings.get("autocode") or {})
        for old_key, new_key in AUTOCODE_KEY_MAP.items():
            if old_key in settings:
                autocode[new_key] = settings[old_key]
        self.set_setting(settings_path, "autocode", autocode)
        for old_key in AUTOCODE_KEY_MAP:
            if old_key in settings:
                self.delete_setting(settings_path, old_key)
        self.set_setting(settings_path, "qc_version", self._version)

    def revert(self, settings_path):
        settings = read_settings(settings_path)
        autocode = settings.get("autocode") or {}
        for old_key, new_key in AUTOCODE_KEY_MAP.items():
            if new_key in autocode:
                self.set_setting(settings_path, old_key, autocode[new_key])
        self.delete_setting(settings_path, "autocode")
        self.set_setting(settings_path, "qc_version", "1.4.1")
