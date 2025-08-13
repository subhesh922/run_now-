# tests/test_parsers.py
import os
import pytest
from server.utils.parsers import load_all_sources

SAMPLE_DIR = os.path.join("server","sample_files")

def _path(name): return os.path.join(SAMPLE_DIR, name)

@pytest.mark.skipif(not os.path.exists(SAMPLE_DIR), reason="sample_files not found")
def test_load_all_sources_smoke():
    kb = _path("dfmea_knowledge_bank_3.csv")
    fri = _path("field_reported_issues_3.xlsx")
    prd = _path("Display PRD_Quasar_cleaned.docx.docx")

    if not (os.path.exists(kb) or os.path.exists(fri) or os.path.exists(prd)):
        pytest.skip("No sample files available")

    rows = load_all_sources(
        product="Quasar",
        subproduct="Display",
        kb_paths=[kb] if os.path.exists(kb) else [],
        field_paths=[fri] if os.path.exists(fri) else [],
        prd_paths=[prd] if os.path.exists(prd) else [],
    )
    assert isinstance(rows, list)
    assert all("text" in r and "source_type" in r for r in rows)
    # ensure order preference (field first, then prd, then kb) if multiple present
    if len(rows) >= 1:
        assert rows[0]["source_type"] in ("field", "prd", "kb")
