from qualitative_coding.migrations.migration import QCMigration
from pathlib import Path

class Migrate_1_4_0(QCMigration):
    _version = "1.4.0"

    def apply(self, settings_path):
        self.set_setting(settings_path, "qc_version", "1.4.0")
        self.set_setting(settings_path, "verbose", False)
        self.set_setting(settings_path, "log_file", 'qc.log')
        self.delete_setting(settings_path, "logs_dir")

    def revert(self, settings_path):
        self.set_setting(settings_path, "qc_version", "1.0.0")
        self.set_setting(settings_path, "logs_dir", "logs")
        self.delete_setting(settings_path, "log_file")
        self.delete_setting(settings_path, "verbose")
        logs_dir = Path(settings_path).parent / "logs_dir"
        if not logs_dir.exists():
            logs_dir.mkdir(parents=True)
