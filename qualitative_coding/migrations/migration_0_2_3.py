from qualitative_coding.migrations.migration import QCMigration

class Migrate_0_2_3(QCMigration):
    _version = "0.2.3"

    def apply(self, settings):
        return settings

    def revert(self, settings):
        return settings
