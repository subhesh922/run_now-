# tests/test_writer.py
import io
import pandas as pd
from server.agents.writer_agent import WriterAgent

def test_writer_generates_excel():
    entries = [
        {
            "ID": "1",
            "Function": "Outdoor readability",
            "Failure Mode": "Unreadable in sunlight",
            "Effects": ["User cannot see UI"],
            "Causes": ["Insufficient backlight"],
            "Prevention Controls": ["Design for high nits"],
            "Detection Controls": ["Sunlight test"],
            "Recommendations": ["Increase LED current"],
            "citations": ["Quasar-5091"]
        }
    ]
    writer = WriterAgent()
    xlsx = writer.to_excel_bytes(entries, meta={"product":"Quasar","subproduct":"Display"})
    assert isinstance(xlsx, (bytes, bytearray)) and len(xlsx) > 0

    # Light sanity: read back and check sheet names
    bio = io.BytesIO(xlsx)
    xl = pd.ExcelFile(bio)
    assert set(xl.sheet_names) >= {"DFMEA","Evidence","Summary"}
