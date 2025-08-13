# server/prompts/dfmea_prompt.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
import json

SYSTEM_MSG = (
    "You are a DFMEA analyst.\n"
    "- Use ONLY the provided CONTEXT.\n"
    "- If evidence is insufficient, return an empty JSON array [].\n"
    "- Every DFMEA entry you return must include a 'citations' array with the kb_id(s) used.\n"
    "- Do NOT compute RPN; numeric ranks will be computed downstream.\n"
    "- Return pure JSON (array) with no markdown or commentary."
)

def build_user_msg(
    *,
    field_issue: Dict[str, Any],
    context_lines: List[str],
    focus: Optional[str] = None
) -> str:
    """
    context_lines should already be prefixed with bracketed kb_ids, e.g.:
      [Quasar-5091] The display shall be readable at 20,000 lux...
    """
    fi_block = json.dumps(
        {
            "Product": field_issue.get("product"),
            "Subsystem": field_issue.get("subsystem"),
            "Component": field_issue.get("component"),
            "Fault_Code": field_issue.get("fault_code") or None,
            "Fault_Type": field_issue.get("fault_type") or None,
        },
        indent=2,
    )
    ctx_block = "\n".join(context_lines)

    task = (
        "FIELD_ISSUE:\n" + fi_block + "\n\n"
        "CONTEXT:\n" + ctx_block + "\n\n"
        "TASK:\n"
        "Using ONLY the CONTEXT above, return DFMEA entries as a pure JSON array ([] if insufficient).\n"
        "Each entry MUST include:\n"
        '  - "Function"\n'
        '  - "Failure Mode"\n'
        '  - "Effects" (list)\n'
        '  - "Causes" (list)\n'
        '  - "Prevention Controls" (list)\n'
        '  - "Detection Controls" (list)\n'
        '  - "Recommendations" (list)\n'
        '  - "citations" (list of kb_ids you actually used)\n'
        "Do NOT include Severity/Occurrence/Detection/RPN; the system will compute these.\n"
    )

    if focus and str(focus).strip():
        task += "\nADMIN_FOCUS:\n" + str(focus).strip() + "\n"

    return task
