import click
from pathlib import Path
import yaml
from semver import Version
from qualitative_coding.views.styles import info
from qualitative_coding.exceptions import QCError
from qualitative_coding.migrations.migration_0_2_3 import Migrate_0_2_3
from qualitative_coding.migrations.migration_1_0_0 import Migrate_1_0_0
from qualitative_coding.helpers import read_settings

migrations = [
    Migrate_0_2_3(),
    Migrate_1_0_0(),
]

def migrate(settings_path, target=None):
    settings = read_settings(settings_path)
    if 'qc_version' not in settings:
        raise QCError("qc_version not specified in settings.")
    current_version = Version.parse(settings['qc_version'])
    target_version = Version.parse(target) if target else migrations[-1].version
    if target_version not in [m.version for m in migrations]:
        raise QCError(f"{target} is not a recognized migration")
    if current_version < target_version:
        for migration in migrations:
            current_version = Version.parse(settings['qc_version'])
            if current_version < migration.version and migration.version <= target_version:
                click.echo(info(f"Applying migration {migration.version}"))
                migration.apply(settings_path)
    elif target_version < current_version:
        for migration in reversed(migrations):
            current_version = Version.parse(settings['qc_version'])
            if migration.version < current_version:
                if target_version < migration.version:
                    click.echo(info(f"Reverting migration {migration.version}"))
                    migration.revert(settings_path)
                else:
                    settings['qc_version'] = migration._version
                    break
