from qualitative_coding.migrations.migration import QCMigration

class Migrate_1_4_1(QCMigration):
    _version = "1.4.1"

    def apply(self, settings_path):
        self.set_setting(settings_path, "qc_version", self._version)
        self.set_setting(settings_path, "unit", "line")

    def revert(self, settings_path):
        self.set_setting(settings_path, "qc_version", "1.4.0")
        self.delete_setting(settings_path, "unit")
