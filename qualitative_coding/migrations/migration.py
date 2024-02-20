from semver import Version
from qualitative_coding.helpers import read_settings
from pathlib import Path
import yaml

class QCMigration:
    """A migration specifies how to move between versions of qc.
    When migrating between version X up to version Y, all migrations
    whose semantic versions are greater than X and at least Y will be applied
    in order. 
    """

    _version = "0.0.0"

    @property
    def version(self):
        return Version.parse(self._version)

    def apply(self, settings_path):
        "Forward migration"

    def revert(self, settings_path):
        "Revert migration"
        return settings

    def set_setting(self, settings_path, key, default_value):
        """Writes a value to settings. 
        By default, only writes the value if the key is not set. 
        When force is True, always writes the value.
        """
        settings = read_settings(settings_path)
        settings[key] = default_value
        Path(settings_path).write_text(yaml.dump(settings))
        return settings

    def delete_setting(self, settings_path, key):
        """Deletes a value in settings.
        """
        settings = read_settings(settings_path)
        del settings[key]
        Path(settings_path).write_text(yaml.dump(settings))
        return settings
