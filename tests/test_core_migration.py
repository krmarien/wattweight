import subprocess
from unittest.mock import MagicMock, patch

import pytest

from wattweight.core.migration import MigrationCore


@patch("subprocess.run")
def test_upgrade_success(mock_subprocess_run):
    mock_subprocess_run.return_value = MagicMock(
        returncode=0, stdout="Upgrade successful", stderr=""
    )

    migration_core = MigrationCore()
    result = migration_core.upgrade()

    assert result is True
    mock_subprocess_run.assert_called_once()
    call_kwargs = mock_subprocess_run.call_args.kwargs
    assert call_kwargs["check"] is True
    assert call_kwargs["env"]["SQLALCHEMY_URL"] == "sqlite:///:memory:"


@patch("subprocess.run")
def test_upgrade_failure(mock_subprocess_run):
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        1, "cmd", output="Upgrade failed", stderr="error"
    )
    migration_core = MigrationCore()

    with pytest.raises(RuntimeError) as context:
        migration_core.upgrade()
    assert "Migration failed: Upgrade failed\\nerror" in str(context.value)


@patch("subprocess.run")
def test_create_migration_success(mock_subprocess_run):
    mock_subprocess_run.return_value = MagicMock(
        returncode=0, stdout="Migration created", stderr=""
    )
    migration_core = MigrationCore()

    message = "test migration"
    migration_core.create_migration(message)

    mock_subprocess_run.assert_called_once()
    call_args_list = mock_subprocess_run.call_args.args[0]
    assert call_args_list[-1] == message
    call_kwargs = mock_subprocess_run.call_args.kwargs
    assert call_kwargs["check"] is True
    assert call_kwargs["env"]["SQLALCHEMY_URL"] == "sqlite:///:memory:"


@patch("subprocess.run")
def test_create_migration_failure(mock_subprocess_run):
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        1, "cmd", output="Migration creation failed", stderr="error"
    )
    migration_core = MigrationCore()

    with pytest.raises(RuntimeError) as context:
        migration_core.create_migration("test migration")
    assert "Migration creation failed: Migration creation failed\nerror" in str(
        context.value
    )
