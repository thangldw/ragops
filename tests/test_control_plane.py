import sqlite3

import pytest

from ragops.control_plane import ControlPlane


def test_workspaces_have_isolated_stores_and_hashed_keys(tmp_path) -> None:
    plane = ControlPlane(tmp_path / "control")
    alpha_key = plane.create_workspace("alpha-team", "Alpha")
    beta_key = plane.create_workspace("beta-team", "Beta")

    alpha_store = plane.workspace_store("alpha-team", alpha_key)
    beta_store = plane.workspace_store("beta-team", beta_key)

    assert alpha_store.path != beta_store.path
    assert plane.authenticate("alpha-team", alpha_key) is True
    assert plane.authenticate("alpha-team", beta_key) is False
    with sqlite3.connect(plane.index) as connection:
        stored = connection.execute(
            "SELECT key_digest FROM workspaces WHERE id = 'alpha-team'"
        ).fetchone()[0]
    assert alpha_key not in stored


def test_key_rotation_invalidates_previous_key(tmp_path) -> None:
    plane = ControlPlane(tmp_path)
    old_key = plane.create_workspace("alpha-team", "Alpha")

    new_key = plane.rotate_key("alpha-team", old_key)

    assert plane.authenticate("alpha-team", old_key) is False
    assert plane.authenticate("alpha-team", new_key) is True
    assert plane.audit_events("alpha-team")[0]["action"] == "workspace.key_rotated"


def test_workspace_validation_and_authentication(tmp_path) -> None:
    plane = ControlPlane(tmp_path)

    with pytest.raises(ValueError, match="lowercase slug"):
        plane.create_workspace("../escape", "Invalid")
    with pytest.raises(PermissionError, match="invalid workspace"):
        plane.workspace_store("missing", "wrong")
