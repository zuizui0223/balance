import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
TEST_PATH = re.compile(r"tests/[A-Za-z0-9_./-]+\.py")


def test_workflows_reference_only_existing_pytest_files():
    missing = []
    for workflow in sorted(WORKFLOWS.glob("*.yml")):
        text = workflow.read_text(encoding="utf-8")
        for rel in sorted(set(TEST_PATH.findall(text))):
            if not (ROOT / rel).exists():
                missing.append((workflow.name, rel))

    assert missing == []
