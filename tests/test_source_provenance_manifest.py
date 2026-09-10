import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"source", "isolation_scaffold", "integration_artifact"}

def test_source_provenance_entries_are_typed_and_hash_bound():
    data = json.loads((ROOT / "SOURCE_PROVENANCE.json").read_text())
    assert data["schemaVersion"] == "1.1"
    assert data["sourceRepository"] == "knowurknottty/CAPT_core"
    assert data["sourceCommit"]
    for entry in data["files"]:
        assert entry["origin"] in ALLOWED, entry
        path = ROOT / entry["path"]
        assert path.is_file(), entry["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]

def test_isolation_owned_paths_are_not_claimed_as_source():
    data = json.loads((ROOT / "SOURCE_PROVENANCE.json").read_text())
    by_path = {e["path"]: e for e in data["files"]}
    assert by_path[".gitignore"]["origin"] == "isolation_scaffold"
    for path, entry in by_path.items():
        if path.startswith("integration/"):
            assert entry["origin"] == "integration_artifact", path
