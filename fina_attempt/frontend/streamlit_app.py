# import os, base64, requests, json
# import pandas as pd
# import streamlit as st
# from dotenv import load_dotenv

# load_dotenv()

# APP_TITLE = "🛡️ DFMEA Builder"
# API_URL_DEFAULT = os.getenv("DFMEA_API_URL", "http://localhost:8000/dfmea/generate")
# ADMIN_PASS = os.getenv("ADMIN_PASS", "")
# DEFAULT_PRODUCT = os.getenv("DEFAULT_PRODUCT", "Quasar")  # hidden default to keep backend unchanged

# # ---------------- Hardcoded unique subproduct list ----------------
# SUBPRODUCT_OPTIONS = [
#     'KEY BUTTON',
#     'CONNECTOR',
#     'DISPLAY + TP',
#     'SCREEN GUARD',
#     'MAIN BOARD',
#     'SCAN ENGINE ASSEMBLY',
#     'RECEIVER',
#     'SOFTWARE',
#     'BEZEL',
#     'SCAN ENGINE',
#     'MINOR COMPONENT',
#     'HOUSING',
#     'END CAP',
#     'SPEAKER',
#     'LAN BOARD',
#     'HOUSING + TP + DISPLAY',
#     'SENSOR',
#     'CASE',
#     'KEYPAD',
#     'LABEL',
#     'FLEX STRIP',
#     'HOLDER',
#     'TOUCH PANEL',
#     'EXIT WINDOW',
#     'PLATE',
#     'CAMERA',
#     'BRACKET',
#     'ANTENNA',
#     'CASE;HOLDER',
#     'IO BOARD',
#     'ADHESIVE',
#     'DOOR',
#     'MYLAR',
#     'DISPLAY',
#     'GRILL',
#     'RETAINER',
#     'GASKET',
#     'TRIGGER',
#     'STRAPS',
#     'COVER',
#     'FRAME',
#     'BATTERY',
#     'REAR HOUSING',
#     'SUB BOARD',
#     'WINDOW / LENS',
#     'OPTION BOARD',
#     'BUTTON CAP',
#     'RUBBER',
#     'HARD DISK',
#     'HOUSING + TP',
#     'KEYBOARD',
#     'CASE;MAIN BOARD',
#     'TOP COVER',
#     'KEY SWITCH',
#     'OVERLAY',
#     'PROTECTOR',
#     'SPEAKER MESH',
#     'LABELS',
#     'MAIN BOARD;CABLE',
#     'SPONGE',
#     'BAFFLE',
#     'POWER BUTTON ASSEMBLY',
#     'SSD DISC',
#     'PLASTCS',
#     'COAX CABLE',
#     'O-RING',
#     'BATTERY DOOR',
#     'FILTER',
#     'DISPLAY TRANSITION BOARD',
#     'COMM I/O',
#     'RETURN UNREPAIRED',
#     'POWER BOARD',
#     'THERMAL MODULE',
#     'FIRMWARE',
#     'SCREW',
#     'SUPER CAP',
#     'WHOLE UNIT',
#     'MYLAR;ADHESIVE',
#     'LENS',
#     'MAIN SEAL',
#     'SPACER',
#     'ACCESSORY',
#     'MESH',
#     'MEMBRANE',
#     'PORT - USB',
#     'FAN',
#     'HANDLE/LOWER HOUSING',
#     'FIRMWARE;TRIGGER',
#     'KEYBOARD;LABEL',
#     'MEMORY',
#     'COMM I/O;PORT - USB',
#     'LABEL;PAD',
#     'DEFECTIVE SPEAKER',
#     'SCREW;LABEL',
#     'HOUSING + TP;DISPLAY + TP',
#     'FLASH',
#     'DIAPER',
#     'CAMERA SCANNER ASSEMBLY',
#     'POWER SUPPLY',
#     'VENT',
#     'PROTECTOR;MAIN BOARD',
#     'ACCESSORY;WHOLE UNIT',
#     'MESH;DISPLAY + TP',
#     'OTHER',
#     'PAD',
#     'FRAME;MAIN BOARD',
#     'FRAME;DISPLAY',
#     'CABLE',
#     'ADHESIVE;MYLAR',
#     'GASKET;LENS',
#     'RECEIVER;SPEAKER',
#     'MAIN BOARD;WHOLE UNIT',
#     'PAD;SUPERCAP',
#     'LED DIODE',
#     'SUB BOARD;FLEX STRIP',
#     'ACCESSORY;KEY BUTTON',
#     'DISPLAY;SHIELD',
#     'CAMERA;MAIN BOARD',
#     'FRAME;MAIN BOARD;RECEIVER',
#     'CABLE;BATTERY',
#     'ADHESIVE;ADHESIVE',
#     'ADHESIVE;MYLAR;SOFTWARE',
#     'BATTERY;ADHESIVE;MYLAR',
#     'MAIN BOARD;CONNECTOR',
#     'ADHESIVE;MYLAR;MAIN BOARD',
#     'ADHESIVE;COVER',
#     'MAIN BOARD;KEY BUTTON',
#     'ADHESIVE;MYLAR;GASKET',
#     'HOUSING;ADHESIVE',
#     'CAMERA;RECEIVER',
#     'SPONGE;TAPE',
#     'FLEX STRIP;MAIN BOARD',
#     'DISPLAY + TP;GASKET',
#     'BATTERY;SPONGE;TAPE',
#     'FLEX STRIP;HOUSING',
#     'GASKET;BUTTON CAP',
#     'FLEX STRIP;HOUSING + TP + DISPLAY',
#     'SOFTWARE;MYLAR',
#     'ANTENNA;BATTERY;GASKET',
#     'ADHESIVE;MYLAR;MAIN BOARD;MAIN BOARD',
#     'SPONGE;TAPE;GASKET',
#     'RUBBER;CONNECTOR',
#     'ADHESIVE;ADHESIVE;FRAME',
#     'MAIN BOARD;TOUCH PANEL;BUTTON CAP',
#     'FLEX STRIP;HOUSING;ADHESIVE',
#     'MYLAR;IO BOARD;SPEAKER',
#     'MYLAR;ADHESIVE;END CAP',
#     'ADHESIVE;SPONGE;TAPE',
#     'KEYPAD;DISPLAY;TOUCH PANEL;GASKET',
#     'DOCK',
#     'HOUSING;HOUSING + TP + DISPLAY',
#     'CONNECTOR;HOUSING',
#     'ADHESIVE;SPONGE;TAPE;ADHESIVE',
#     'MYLAR;SPONGE;TAPE;ADHESIVE;MYLAR',
#     'CONNECTOR;DISPLAY + TP;FOIL;TAPE;SOFTWARE',
#     'CAMERA SCANNER ASSEMBLY;HOUSING + TP + DISPLAY',
#     'SCAN ENGINE;ADHESIVE;TOUCH PANEL',
#     'KEYPAD;KEYBOARD',
#     'ADHESIVE;END CAP;MAIN BOARD',
#     'SOFTWARE;SOFTWARE;FOIL;TAPE;ADHESIVE;MYLAR',
#     'MINOR COMPONENT;VENT',
#     'MAIN BOARD;ADHESIVE',
#     'SPONGE;TAPE;ADHESIVE;MYLAR',
#     'ADHESIVE;ADHESIVE;PROTECTOR;MAIN BOARD',
#     'PROTECTOR;ACCESSORY;WHOLE UNIT',
#     'CONNECTOR;ADHESIVE;PROTECTOR',
#     'TRIGGER;DISPLAY + TP;BEZEL',
#     'MESH;DISPLAY + TP;DISPLAY + TP',
#     'RUBBER;COMM I/O',
#     'POWER BUTTON ASSEMBLY;OTHER',
#     'PAD;BEZEL',
#     'HOUSING;DISPLAY + TP',
#     'FLEX STRIP;HOUSING;MAIN BOARD',
#     'FRAME;MAIN BOARD;DISPLAY',
#     'HOUSING;HOUSING;RETURN UNREPAIRED',
#     'PORT - PARALLEL',
#     'TRIGGER;SPONGE;TAPE;FLEX STRIP',
#     'MAIN BOARD;SCAN ENGINE ASSEMBLY',
#     'CABLE;SOFTWARE;PAD;SOFTWARE;MAIN BOARD;ADHESIVE;SOFTWARE',
#     'FLEX STRIP;HOUSING;HOUSING + TP + DISPLAY;FLEX STRIP;SEAL',
#     'SOFTWARE;DOOR;RUBBER;GASKET;RUBBER;SOFTWARE;SOFTWARE',
#     'DOOR;TRIGGER;GASKET;ACCESSORY;SEAL;RUBBER;BEZEL;RUBBER;ACCESSORY',
#     'KEY BUTTON;KEYPAD;RUBBER;TOUCH PANEL',
#     'SCAN ENGINE ASSEMBLY;COVER;KEY BUTTON;SPONGE;ACCESSORY',
#     'SUPERCAP;PLUG;FRAME',
#     'DOOR;END CAP;MAIN BOARD;COVER;SOFTWARE',
#     'HOUSING;CABLE;CONNECTOR;SOFTWARE;CONNECTOR;FLEX STRIP;BEZEL',
#     'THERMAL MODULE;RUBBER;COVER;HOUSING;SOFTWARE',
#     'BATTERY;OPTION BOARD',
#     'RUBBER;DISPLAY + TP;SOFTWARE;CONNECTOR;PLUG',
#     'RECEIVER;KEYBOARD;OVERLAY;GASKET;ADHESIVE',
#     'HOUSING;MAIN BOARD;HOUSING;KEY BUTTON;BEZEL',
#     'OPTION BOARD;BATTERY;PLUG;CAMERA;SPONGE;COVER',
#     'SCAN ENGINE;SUPERCAP;CAMERA;HOUSING;GASKET;DISPLAY',
#     'BRACKET;GASKET;OVERLAY;DOOR;BATTERY;SOFTWARE;SEAL;BATTERY',
#     'MAIN BOARD;DISPLAY + TP;ADHESIVE;KEY BUTTON;MAIN BOARD;SEAL;FLEX STRIP',
#     'POWER BOARD;BEZEL',
#     'KEY BUTTON;ACCESSORY;SOFTWARE;SOFTWARE;COVER;BATTERY',
#     'DISPLAY + TP;SOFTWARE;DISPLAY;BRACKET;CAMERA;DISPLAY',
#     'KEY BUTTON;KEY BUTTON;HOUSING;SOFTWARE;BEZEL;FLEX STRIP;SOFTWARE',
#     'MAIN BOARD;RUBBER;DOOR;CONNECTOR;BEZEL;SOFTWARE;MAIN BOARD;SOFTWARE;GASKET;CONNECTOR;SOFTWARE;PAD;FRAME;FRAME;SOFTWARE',
#     'ACCESSORY;MAIN BOARD;SOFTWARE;SEAL;BEZEL;SOFTWARE;OVERLAY;SEAL;FLEX STRIP;SEAL;SPONGE',
#     'HOUSING;CONNECTOR;DOOR;RETAINER;COVER;BATTERY;FLEX STRIP',
#     'HOUSING + TP;MAIN BOARD;FLEX STRIP;SOFTWARE;BUTTON CAP;CABLE',
#     'MINOR COMPONENT;HOUSING + TP;SOFTWARE;SOFTWARE;TRIGGER;MAIN BOARD;GASKET',
#     'POWER BOARD;MAIN BOARD;BATTERY;SOFTWARE;FLEX STRIP;KEY BUTTON;COVER;CONNECTOR;ACCESSORY;MAIN BOARD;BATTERY;KEY SWITCH;CAMERA;BATTERY',
#     'HOUSING;POWER BOARD;POWER BOARD;MAIN BOARD;ACCESSORY;SOFTWARE;HOUSING;FLEX STRIP;COVER;MAIN BOARD;DOOR;IO BOARD;CONNECTOR',
#     'SOFTWARE;SEAL;RETURN UNREPAIRED;SOFTWARE;SOFTWARE;SOFTWARE',
#     'RADIO - WWAN',
#     'GASKET;KEY BUTTON;CONNECTOR;ADHESIVE;FOIL;TAPE;SIM TRAY',
#     'HOUSING;FRAME;SPEAKER;SOFTWARE;MAIN BOARD;FRAME',
#     'DISPLAY + TP;ACCESSORY;HOUSING;KEY BUTTON;HOUSING;FLEX STRIP;MAIN BOARD;BRACKET;CABLE;FLEX STRIP',
#     'MAIN BOARD;HOUSING;HOUSING;OPTION BOARD;POWER BUTTON ASSEMBLY;HOUSING;MAIN BOARD;SOFTWARE;BEZEL;DOOR;MAIN BOARD;MAIN BOARD;GASKET;MAIN BOARD;FRAME;MAIN BOARD;KEY BUTTON;LABEL;LABEL;MINOR COMPONENT',
#     'COVER;SSD DISC;HOUSING;HOUSING;BATTERY;SCREW;MINOR COMPONENT;FLEX STRIP',
#     'FRAME;HOUSING - MIDDLE FRAME;FRAME;RADIO - WLAN',
#     'BATTERY DOOR;DISPLAY + TP;IO BOARD;HOUSING;HOUSING;MAIN BOARD',
#     'BATTERY DOOR;IO BOARD;DISPLAY + TP;HOUSING',
#     'HOUSING;CABLE;FLEX STRIP;FRAME',
#     'RECEIVER;FLEX STRIP;SCAN ENGINE;MAIN BOARD;KEY BUTTON',
#     'FRAME;ANTENNA;CAMERA;SOFTWARE;BRACKET;CONNECTOR;KEY BUTTON;BRACKET;HOUSING;MINOR COMPONENT',
#     'MAIN BOARD;SOFTWARE;IO BOARD;MAIN BOARD;MAIN BOARD;HOUSING;MAIN BOARD;SCREW',
#     'SCAN ENGINE;HOUSING;MAIN BOARD;CONNECTOR;HOUSING;FLEX STRIP;LABEL;LABELS;STRAP;TRIGGER;STRAP;HOUSING',
#     'MAIN BOARD;MINOR COMPONENT;MINOR COMPONENT;STRAPS;RECEIVER;MAIN BOARD;CAMERA;TAPE;IO BOARD',
#     'SCRAP;ANTENNA;BRACKET;FLEX STRIP;PLASTCS;SCAN ENGINE ASSEMBLY',
#     'SCAN ENGINE;ADHESIVE;CONNECTOR;KEYPAD;FLEX STRIP',
#     'HOUSING + TP + DISPLAY;DISPLAY + TP;SCRAP;MAIN BOARD;SCAN ENGINE;PLASTCS',
#     'MAIN BOARD;MAIN BOARD;MAIN BOARD;CONNECTOR;FLEX STRIP;SOFTWARE;TAPE;SCAN ENGINE ASSEMBLY;FLEX STRIP;COAX CABLE;TRIGGER BOARD;SOFTWARE;BATTERY;IO BOARD;MAIN BOARD',
#     'SCAN ENGINE;WHOLE UNIT;MAIN BOARD;MAIN BOARD;COAX CABLE;BRACKET;O-RING',
#     'FOIL;BATTERY;CABLE;KEY BUTTON;SCAN ENGINE;ANTENNA;MINOR COMPONENT;SOFTWARE',
#     'SCRAP;TRIGGER;HOUSING;GASKET;MAIN BOARD;WINDOW / LENS;MAIN BOARD;POWER BUTTON ASSEMBLY;CONNECTOR;FOIL;TAPE',
#     'HOUSING + TP + DISPLAY;CABLE;FLEX STRIP;FRAME;CONNECTOR;BATTERY DOOR;FLEX STRIP;MINOR COMPONENT;STRAP;KEY BUTTON;SCAN ENGINE;HOLDER;HOLDER;VIBRATOR',
#     'MAIN BOARD;SPEAKER;ADHESIVE;SPEAKER;FLEX STRIP;SOFTWARE;SCAN ENGINE ASSEMBLY;ADHESIVE',
#     'HOUSING;MAIN BOARD;KEY BUTTON;SOFTWARE;SOFTWARE;SOFTWARE;FLEX STRIP;SOFTWARE;SOFTWARE;SOFTWARE;SOFTWARE;SOFTWARE;SOFTWARE;SOFTWARE;SOFTWARE',
#     'PAD;TAPE;SOFTWARE;FLEX STRIP;SOFTWARE;SOFTWARE;SOFTWARE;BATTERY;FLEX STRIP;SOFTWARE',
#     'SCAN ENGINE ASSEMBLY;PROTECTOR;MAIN BOARD;BRACKET;SOFTWARE;MAIN BOARD;SOFTWARE;FRAME;TRIGGER;TRIGGER',
#     'CAMERA SCANNER ASSEMBLY;HOUSING;SUB BOARD;ANTENNA;MAIN BOARD;MEMORY;FLEX STRIP;MAIN BOARD;HOUSING;GRILL;MAIN BOARD;ANTENNA;FLEX STRIP;HOUSING;SUPERCAP',
#     'RUBBER;MYLAR;MYLAR;GASKET;ANTENNA;GASKET;SPONGE;TAPE;GASKET;MYLAR;GASKET;MYLAR;SEAL;KEY BUTTON;SUPERCAP;GASKET;SPONGE;TAPE;MYLAR;MYLAR;LABELS',
#     'SCAN ENGINE;ADHESIVE;LABEL;PAD;HOUSING;MYLAR;TAPE;DEFECTIVE SPEAKER',
#     'FLEX STRIP;FLEX STRIP;HOUSING;PAD;GASKET;HOUSING + TP + DISPLAY;SENSOR;PAD;SUPERCAP;PAD;SCREW;LABEL',
#     'SCAN ENGINE;HOUSING;TAPE;HOUSING;END CAP;SPONGE;PAD;ADHESIVE;TAPE;ADHESIVE;HOUSING;SHIELD;ADHESIVE;SCREW;SCREW;SCREW;TAPE;DOOR;LABEL',
#     'HOUSING;ADHESIVE;BAFFLE;MAIN BOARD;CONNECTOR;PLUG;MAIN BOARD;HOUSING;HOUSING + TP;POWER BUTTON ASSEMBLY;HOUSING + TP + DISPLAY',
#     'FLEX STRIP;LABEL;FLASH;CAMERA;BAFFLE;COVER;HOLDER;FLASH;BAFFLE;HOUSING;FRAME;CABLE;HOUSING;SPONGE;MAIN BOARD;FLEX STRIP;IO BOARD;SPONGE;FLEX STRIP;WINDOW / LENS',
#     'MAIN BOARD;HOLDER;BUTTON CAP;RUBBER;BAFFLE;RUBBER BOOT;HOUSING;RUBBER;SOFTWARE;MAIN BOARD;ADHESIVE;DIAPER;HOLDER;COVER',
#     'SCAN ENGINE ASSEMBLY;DISPLAY + TP;COVER;SCAN ENGINE;BATTERY;MYLAR;RECEIVER;KEY BUTTON;SOFTWARE;ADHESIVE;CONNECTOR',
#     'SOFTWARE;DISPLAY;MAIN BOARD;ADHESIVE;BATTERY;LABEL;LABEL;LABEL;LABEL;LABEL',
#     'HOUSING;TOUCH PANEL;SCAN ENGINE;ADHESIVE;MAIN BOARD;SOFTWARE;FLEX STRIP;MAIN SEAL',
#     'SCAN ENGINE ASSEMBLY;ADHESIVE;RECEIVER;SPEAKER;SOFTWARE;ANTENNA;DOOR;SPACER;RETAINER;END CAP;MAIN BOARD;RECEIVER;WHOLE UNIT;ACCESSORY;SOFTWARE;ANTENNA;SOFTWARE;SD CARD DOOR',
#     'GRILL;TOUCH PANEL;SENSOR;SPACER',
#     'DELAY;DAMAGE',
#     'PRINTHEAD',
#     'CHARGER',
#     'REAR CLEAT',
#     'BOOT',
#     'BATTERY PAD',
#     'HAND STRAP',
#     'SAM CARD ASSEMBLY',
#     'TURRET',
#     'CUTTER',
#     'PORT - PARALLEL',
#     'FLIPPER',
#     'PRINTER SOFTWARE',
#     'ACCESSORIES NON-REPAIRABLE',
#     'BATTERY CONN/FLEX',
#     'PORT - SERIAL'
# ]

# # ---------------- Page ----------------
# st.set_page_config(page_title=APP_TITLE, layout="wide")
# st.title(APP_TITLE)

# # Session defaults
# if "is_admin" not in st.session_state: st.session_state.is_admin = False
# if "admin_secret" not in st.session_state: st.session_state.admin_secret = ""
# if "focus_text" not in st.session_state: st.session_state.focus_text = ""
# if "subproducts_selected" not in st.session_state:
#     st.session_state.subproducts_selected = [SUBPRODUCT_OPTIONS[0]] if SUBPRODUCT_OPTIONS else []

# # ---------------- Sidebar ----------------
# with st.sidebar:
#     # Admin
#     st.markdown("### Admin")
#     env_admin = ADMIN_PASS or ""
#     entered = st.text_input("Admin password", type="password", value="")
#     c1, c2 = st.columns(2)
#     with c1:
#         if st.button("Login", use_container_width=True):
#             st.session_state.is_admin = (env_admin and entered == env_admin)
#             if st.session_state.is_admin:
#                 st.session_state.admin_secret = entered
#                 st.success("Admin mode enabled.")
#             else:
#                 st.session_state.admin_secret = ""
#                 st.error("Invalid password.")
#     with c2:
#         if st.button("Logout", use_container_width=True):
#             st.session_state.is_admin = False
#             st.session_state.admin_secret = ""
#             st.session_state.focus_text = ""
#             st.info("Logged out.")

#     # Focus Prompt (admin only)
#     if st.session_state.is_admin:
#         st.markdown("### 🔒 Focus Prompt")
#         st.caption("This guides DFMEA generation. **Samples below are examples only**.")
#         samples = [
#             "Sample: Prioritize freezer-related failures; highlight condensation/low-temp display issues; exclude cosmetic-only defects.",
#             "Sample: Emphasize sunlight readability; correlate luminance/contrast specs to field issues; focus on outdoor use.",
#             "Sample: Focus on touch sensitivity degradation vs. environmental cycling, contamination, and glove usage.",
#             "Sample: Elevate safety-critical failures; ensure detection controls reference validation test IDs.",
#         ]
#         chosen = st.selectbox("Sample prompts (examples only):", ["— choose a sample —"] + samples)
#         s1, s2 = st.columns(2)
#         with s1:
#             if st.button("Insert sample", use_container_width=True) and chosen != "— choose a sample —":
#                 st.session_state.focus_text = chosen
#         with s2:
#             if st.button("Clear", use_container_width=True):
#                 st.session_state.focus_text = ""
#         st.session_state.focus_text = st.text_area(
#             "Focus (admin only)", value=st.session_state.focus_text, height=300,
#             placeholder="Describe what to prioritize/exclude. e.g., link DFMEA to PRD requirement IDs; exclude cosmetic-only defects."
#         )

#     st.markdown("---")
#     st.markdown("### Settings")
#     api_url = st.text_input("Backend API URL", value=API_URL_DEFAULT)

#     # Subproducts multiselect (from hardcoded list)
#     st.caption(f"Subproduct options loaded: **{len(SUBPRODUCT_OPTIONS)}**")
#     st.session_state.subproducts_selected = st.multiselect(
#         "Choose one or more subproducts",
#         options=SUBPRODUCT_OPTIONS,
#         default=st.session_state.subproducts_selected if st.session_state.subproducts_selected else SUBPRODUCT_OPTIONS[:1],
#     )
#     if not st.session_state.subproducts_selected:
#         st.warning("Select at least one subproduct.")

# # ---------------- Uploaders ----------------
# st.markdown("#### 1) Upload PRDs / Specs (.docx / .csv / .xlsx)")
# prd_files = st.file_uploader(
#     "Upload one or more PRD/spec files",
#     type=["docx", "doc", "csv", "xlsx"],
#     accept_multiple_files=True,
#     key="prd_uploader",
# )

# st.markdown("#### 2) Upload Knowledge Base (.csv / .xlsx)")
# kb_files = st.file_uploader(
#     "Upload one or more Knowledge Bank files (.csv / .xlsx)",
#     type=["csv", "xlsx"],
#     accept_multiple_files=True,
#     key="kb_uploader",
# )

# st.markdown("#### 3) Upload Field Reported Issues (.csv / .xlsx)")
# fri_files = st.file_uploader(
#     "Upload one or more Field Reported Issues files (.csv / .xlsx)",
#     type=["csv", "xlsx"],
#     accept_multiple_files=True,
#     key="fri_uploader",
# )

# # ---------------- Generate DFMEA ----------------
# st.divider()
# if st.button("✨ Create DFMEA", type="primary", use_container_width=True):
#     if not (prd_files or kb_files or fri_files):
#         st.warning("Please upload at least one file in PRDs, Knowledge Base, or Field Issues.")
#     elif not st.session_state.subproducts_selected:
#         st.warning("Please select at least one subproduct.")
#     else:
#         with st.spinner("Building DFMEA…"):
#             files = []

#             # PRDs/specs
#             for f in (prd_files or []):
#                 f.seek(0)
#                 name = f.name.lower()
#                 if name.endswith(".docx"):
#                     mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
#                 elif name.endswith(".doc"):
#                     mime = "application/msword"
#                 elif name.endswith(".csv"):
#                     mime = "text/csv"
#                 elif name.endswith(".xlsx"):
#                     mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#                 else:
#                     mime = "application/octet-stream"
#                 files.append(("prds", (f.name, f, mime)))

#             # Knowledge Base
#             for f in (kb_files or []):
#                 f.seek(0)
#                 mime = "text/csv" if f.name.lower().endswith(".csv") else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#                 files.append(("knowledge_base", (f.name, f, mime)))

#             # Field Issues
#             for f in (fri_files or []):
#                 f.seek(0)
#                 mime = "text/csv" if f.name.lower().endswith(".csv") else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#                 files.append(("field_issues", (f.name, f, mime)))

#             # Payload
#             subproducts = st.session_state.subproducts_selected
#             first_sub = subproducts[0]
#             data = {
#                 "product": DEFAULT_PRODUCT,
#                 "subproduct": first_sub,                 # backward-compat with current backend
#                 "subproducts": json.dumps(subproducts),  # multi support for backend iteration
#             }
#             if st.session_state.is_admin and st.session_state.focus_text.strip():
#                 data["focus"] = st.session_state.focus_text.strip()

#             headers = {}
#             if st.session_state.is_admin and st.session_state.get("admin_secret"):
#                 headers["X-Admin-Auth"] = st.session_state["admin_secret"]

#             try:
#                 resp = requests.post(api_url, data=data, files=files, headers=headers, timeout=300)
#                 resp.raise_for_status()
#                 payload = resp.json()

#                 st.success(f"DFMEA generated for {payload.get('product', DEFAULT_PRODUCT)} / {payload.get('subproduct', first_sub)}")
#                 st.caption(f"(Requested subproducts: {', '.join(subproducts)})")

#                 st.subheader("Preview JSON entries")
#                 st.json(payload.get("entries", []))

#                 if "excel_base64" in payload:
#                     xls_bytes = base64.b64decode(payload["excel_base64"])
#                     st.download_button(
#                         "⬇️ Download DFMEA Excel",
#                         data=xls_bytes,
#                         file_name=f"DFMEA_{payload.get('product', DEFAULT_PRODUCT)}_{first_sub}.xlsx",
#                         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#                         use_container_width=True,
#                     )

#                 if payload.get("counts"):
#                     st.caption(f"Ingestion counts: {payload['counts']}")
#             except Exception as e:
#                 st.error(f"Backend error: {e}")

# # ---------------- Optional previews ----------------
# st.divider()
# c1, c2 = st.columns(2)
# with c1:
#     if kb_files:
#         st.caption("Knowledge Base (first file preview)")
#         try:
#             f0 = kb_files[0]
#             df = pd.read_csv(f0) if f0.name.lower().endswith(".csv") else pd.read_excel(f0)
#             st.dataframe(df.head(20))
#         except Exception as e:
#             st.warning(f"KB preview failed: {e}")
# with c2:
#     if fri_files:
#         st.caption("Field Issues (first file preview)")
#         try:
#             f0 = fri_files[0]
#             df = pd.read_csv(f0) if f0.name.lower().endswith(".csv") else pd.read_excel(f0)
#             st.dataframe(df.head(20))
#         except Exception as e:
#             st.warning(f"Field preview failed: {e}")

# # PRD/spec preview if CSV/XLSX
# if prd_files:
#     st.caption("PRD/Spec files uploaded:")
#     st.write([f.name for f in prd_files])
#     try:
#         f0 = prd_files[0]
#         fname = f0.name.lower()
#         if fname.endswith(".csv"):
#             st.caption("PRD/Spec preview (first file)")
#             st.dataframe(pd.read_csv(f0).head(20))
#         elif fname.endswith(".xlsx"):
#             st.caption("PRD/Spec preview (first file)")
#             st.dataframe(pd.read_excel(f0).head(20))
#     except Exception as e:
#         st.warning(f"PRD/Spec preview failed: {e}")

import os, base64, requests, json, io
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

APP_TITLE = "🛡️ DFMEA Builder"
API_URL_DEFAULT = os.getenv("DFMEA_API_URL", "http://localhost:8000/dfmea/generate")
ADMIN_PASS = os.getenv("ADMIN_PASS", "")
DEFAULT_PRODUCT = os.getenv("DEFAULT_PRODUCT", "Quasar")

# ---------------- Hardcoded unique subproduct list (truncated here if very long) ----------------
SUBPRODUCT_OPTIONS = [
    'KEY BUTTON','CONNECTOR','DISPLAY + TP','SCREEN GUARD','MAIN BOARD','SCAN ENGINE ASSEMBLY','RECEIVER','SOFTWARE','BEZEL','SCAN ENGINE',
    'MINOR COMPONENT','HOUSING','END CAP','SPEAKER','LAN BOARD','HOUSING + TP + DISPLAY',
    'SENSOR','CASE','KEYPAD','LABEL','FLEX STRIP','HOLDER',
    'TOUCH PANEL','EXIT WINDOW','PLATE','CAMERA','BRACKET','ANTENNA','CASE;HOLDER',
    'IO BOARD','ADHESIVE','DOOR','MYLAR','DISPLAY','GRILL',
    'RETAINER',
    'GASKET',
    'TRIGGER',
    'STRAPS',
    'COVER',
    'FRAME',
    'BATTERY',
    'REAR HOUSING',
    'SUB BOARD',
    'WINDOW / LENS',
    'OPTION BOARD',
    'BUTTON CAP',
    'RUBBER',
    'HARD DISK',
    'HOUSING + TP',
    'KEYBOARD',
    'CASE;MAIN BOARD',
    'TOP COVER',
    'KEY SWITCH',
    'OVERLAY',
    'PROTECTOR',
    'SPEAKER MESH',
    'LABELS',
    'MAIN BOARD;CABLE',
    'SPONGE',
    'BAFFLE',
    'POWER BUTTON ASSEMBLY',
    'SSD DISC',
    'PLASTCS',
    'COAX CABLE',
    'O-RING',
    'BATTERY DOOR',
    'FILTER',
    'DISPLAY TRANSITION BOARD',
    'COMM I/O',
    'RETURN UNREPAIRED',
    'POWER BOARD',
    'THERMAL MODULE',
    'FIRMWARE',
    'SCREW',
    'SUPER CAP',
    'WHOLE UNIT',
    'MYLAR;ADHESIVE',
    'LENS',
    'MAIN SEAL',
    'SPACER',
    'ACCESSORY',
    'MESH',
    'MEMBRANE',
    'PORT - USB',
    'FAN',
    'HANDLE/LOWER HOUSING',
    'FIRMWARE;TRIGGER',
    'KEYBOARD;LABEL',
    'MEMORY',
    'COMM I/O;PORT - USB',
    'LABEL;PAD',
    'DEFECTIVE SPEAKER',
    'SCREW;LABEL',
    'HOUSING + TP;DISPLAY + TP',
    'FLASH',
    'DIAPER',
    'CAMERA SCANNER ASSEMBLY',
    'POWER SUPPLY',
    'VENT',
    'PROTECTOR;MAIN BOARD',
    'ACCESSORY;WHOLE UNIT',
    'MESH;DISPLAY + TP',
    'OTHER',
    'PAD',
    'FRAME;MAIN BOARD',
    'FRAME;DISPLAY',
    'CABLE',
    'ADHESIVE;MYLAR',
    'GASKET;LENS',
    'RECEIVER;SPEAKER',
    'MAIN BOARD;WHOLE UNIT',
    'PAD;SUPERCAP',
    'LED DIODE',
    'SUB BOARD;FLEX STRIP',
    'ACCESSORY;KEY BUTTON',
    'DISPLAY;SHIELD',
    'CAMERA;MAIN BOARD',
    'FRAME;MAIN BOARD;RECEIVER',
    'CABLE;BATTERY',
    'ADHESIVE;ADHESIVE',
    'ADHESIVE;MYLAR;SOFTWARE',
    'BATTERY;ADHESIVE;MYLAR',
    'MAIN BOARD;CONNECTOR',
    'ADHESIVE;MYLAR;MAIN BOARD',
    'ADHESIVE;COVER',
    'MAIN BOARD;KEY BUTTON',
    'ADHESIVE;MYLAR;GASKET',
    'HOUSING;ADHESIVE',
    'CAMERA;RECEIVER',
    'SPONGE;TAPE',
    'FLEX STRIP;MAIN BOARD',
    'DISPLAY + TP;GASKET',
    'BATTERY;SPONGE;TAPE',
    'FLEX STRIP;HOUSING',
    'GASKET;BUTTON CAP',
    'FLEX STRIP;HOUSING + TP + DISPLAY',
    'SOFTWARE;MYLAR',
    'ANTENNA;BATTERY;GASKET',
    'ADHESIVE;MYLAR;MAIN BOARD;MAIN BOARD',
    'SPONGE;TAPE;GASKET',
    'RUBBER;CONNECTOR',
    'ADHESIVE;ADHESIVE;FRAME',
    'MAIN BOARD;TOUCH PANEL;BUTTON CAP',
    'FLEX STRIP;HOUSING;ADHESIVE',
    'MYLAR;IO BOARD;SPEAKER',
    'MYLAR;ADHESIVE;END CAP',
    'ADHESIVE;SPONGE;TAPE',
    'KEYPAD;DISPLAY;TOUCH PANEL;GASKET',
    'DOCK',
    'HOUSING;HOUSING + TP + DISPLAY',
    'CONNECTOR;HOUSING',
    'ADHESIVE;SPONGE;TAPE;ADHESIVE',
    'MYLAR;SPONGE;TAPE;ADHESIVE;MYLAR',
    'CONNECTOR;DISPLAY + TP;FOIL;TAPE;SOFTWARE',
    'CAMERA SCANNER ASSEMBLY;HOUSING + TP + DISPLAY',
    'SCAN ENGINE;ADHESIVE;TOUCH PANEL',
    'KEYPAD;KEYBOARD',
    'ADHESIVE;END CAP;MAIN BOARD',
    'SOFTWARE;SOFTWARE;FOIL;TAPE;ADHESIVE;MYLAR',
    'MINOR COMPONENT;VENT',
    'MAIN BOARD;ADHESIVE','SPONGE;TAPE;ADHESIVE;MYLAR','ADHESIVE;ADHESIVE;PROTECTOR;MAIN BOARD','PROTECTOR;ACCESSORY;WHOLE UNIT','CONNECTOR;ADHESIVE;PROTECTOR','TRIGGER;DISPLAY + TP;BEZEL','MESH;DISPLAY + TP;DISPLAY + TP','RUBBER;COMM I/O','POWER BUTTON ASSEMBLY;OTHER','PAD;BEZEL','HOUSING;DISPLAY + TP','FLEX STRIP;HOUSING;MAIN BOARD','FRAME;MAIN BOARD;DISPLAY','HOUSING;HOUSING;RETURN UNREPAIRED','PORT - PARALLEL',
    'TRIGGER;SPONGE;TAPE;FLEX STRIP',
    'MAIN BOARD;SCAN ENGINE ASSEMBLY',
    'CABLE;SOFTWARE;PAD;SOFTWARE;MAIN BOARD;ADHESIVE;SOFTWARE',
    'FLEX STRIP;HOUSING;HOUSING + TP + DISPLAY;FLEX STRIP;SEAL',
    'SOFTWARE;DOOR;RUBBER;GASKET;RUBBER;SOFTWARE;SOFTWARE',
    'DOOR;TRIGGER;GASKET;ACCESSORY;SEAL;RUBBER;BEZEL;RUBBER;ACCESSORY',
    'KEY BUTTON;KEYPAD;RUBBER;TOUCH PANEL',
    'SCAN ENGINE ASSEMBLY;COVER;KEY BUTTON;SPONGE;ACCESSORY',
    'SUPERCAP;PLUG;FRAME',
    'DOOR;END CAP;MAIN BOARD;COVER;SOFTWARE',
    'HOUSING;CABLE;CONNECTOR;SOFTWARE;CONNECTOR;FLEX STRIP;BEZEL',
    'THERMAL MODULE;RUBBER;COVER;HOUSING;SOFTWARE',
    'BATTERY;OPTION BOARD',
    'RUBBER;DISPLAY + TP;SOFTWARE;CONNECTOR;PLUG',
    'RECEIVER;KEYBOARD;OVERLAY;GASKET;ADHESIVE',
    'HOUSING;MAIN BOARD;HOUSING;KEY BUTTON;BEZEL',
    'OPTION BOARD;BATTERY;PLUG;CAMERA;SPONGE;COVER',
    'SCAN ENGINE;SUPERCAP;CAMERA;HOUSING;GASKET;DISPLAY',
    'BRACKET;GASKET;OVERLAY;DOOR;BATTERY;SOFTWARE;SEAL;BATTERY',
    'MAIN BOARD;DISPLAY + TP;ADHESIVE;KEY BUTTON;MAIN BOARD;SEAL;FLEX STRIP',
    'POWER BOARD;BEZEL',
    'KEY BUTTON;ACCESSORY;SOFTWARE;SOFTWARE;COVER;BATTERY',
    'DISPLAY + TP;SOFTWARE;DISPLAY;BRACKET;CAMERA;DISPLAY',
    'KEY BUTTON;KEY BUTTON;HOUSING;SOFTWARE;BEZEL;FLEX STRIP;SOFTWARE',
    'MAIN BOARD;RUBBER;DOOR;CONNECTOR;BEZEL;SOFTWARE;MAIN BOARD;SOFTWARE;GASKET;CONNECTOR;SOFTWARE;PAD;FRAME;FRAME;SOFTWARE',
    'ACCESSORY;MAIN BOARD;SOFTWARE;SEAL;BEZEL;SOFTWARE;OVERLAY;SEAL;FLEX STRIP;SEAL;SPONGE',
    'HOUSING;CONNECTOR;DOOR;RETAINER;COVER;BATTERY;FLEX STRIP',
    'HOUSING + TP;MAIN BOARD;FLEX STRIP;SOFTWARE;BUTTON CAP;CABLE',
    'MINOR COMPONENT;HOUSING + TP;SOFTWARE;SOFTWARE;TRIGGER;MAIN BOARD;GASKET',
    'POWER BOARD;MAIN BOARD;BATTERY;SOFTWARE;FLEX STRIP;KEY BUTTON;COVER;CONNECTOR;ACCESSORY;MAIN BOARD;BATTERY;KEY SWITCH;CAMERA;BATTERY',
    'HOUSING;POWER BOARD;POWER BOARD;MAIN BOARD;ACCESSORY;SOFTWARE;HOUSING;FLEX STRIP;COVER;MAIN BOARD;DOOR;IO BOARD;CONNECTOR',
    'SOFTWARE;SEAL;RETURN UNREPAIRED;SOFTWARE;SOFTWARE;SOFTWARE',
    'RADIO - WWAN',
    'GASKET;KEY BUTTON;CONNECTOR;ADHESIVE;FOIL;TAPE;SIM TRAY',
    'HOUSING;FRAME;SPEAKER;SOFTWARE;MAIN BOARD;FRAME',
    'DISPLAY + TP;ACCESSORY;HOUSING;KEY BUTTON;HOUSING;FLEX STRIP;MAIN BOARD;BRACKET;CABLE;FLEX STRIP',
    'MAIN BOARD;HOUSING;HOUSING;OPTION BOARD;POWER BUTTON ASSEMBLY;HOUSING;MAIN BOARD;SOFTWARE;BEZEL;DOOR;MAIN BOARD;MAIN BOARD;GASKET;MAIN BOARD;FRAME;MAIN BOARD;KEY BUTTON;LABEL;LABEL;MINOR COMPONENT',
    'COVER;SSD DISC;HOUSING;HOUSING;BATTERY;SCREW;MINOR COMPONENT;FLEX STRIP',
    'FRAME;HOUSING - MIDDLE FRAME;FRAME;RADIO - WLAN',
    'BATTERY DOOR;DISPLAY + TP;IO BOARD;HOUSING;HOUSING;MAIN BOARD',
    'BATTERY DOOR;IO BOARD;DISPLAY + TP;HOUSING',
    'HOUSING;CABLE;FLEX STRIP;FRAME',
    'RECEIVER;FLEX STRIP;SCAN ENGINE;MAIN BOARD;KEY BUTTON',
    'FRAME;ANTENNA;CAMERA;SOFTWARE;BRACKET;CONNECTOR;KEY BUTTON;BRACKET;HOUSING;MINOR COMPONENT',
    'MAIN BOARD;SOFTWARE;IO BOARD;MAIN BOARD;MAIN BOARD;HOUSING;MAIN BOARD;SCREW',
    'SCAN ENGINE;HOUSING;MAIN BOARD;CONNECTOR;HOUSING;FLEX STRIP;LABEL;LABELS;STRAP;TRIGGER;STRAP;HOUSING',
    'MAIN BOARD;MINOR COMPONENT;MINOR COMPONENT;STRAPS;RECEIVER;MAIN BOARD;CAMERA;TAPE;IO BOARD',
    'SCRAP;ANTENNA;BRACKET;FLEX STRIP;PLASTCS;SCAN ENGINE ASSEMBLY',
    'SCAN ENGINE;ADHESIVE;CONNECTOR;KEYPAD;FLEX STRIP',
    'HOUSING + TP + DISPLAY;DISPLAY + TP;SCRAP;MAIN BOARD;SCAN ENGINE;PLASTCS',
    'MAIN BOARD;MAIN BOARD;MAIN BOARD;CONNECTOR;FLEX STRIP;SOFTWARE;TAPE;SCAN ENGINE ASSEMBLY;FLEX STRIP;COAX CABLE;TRIGGER BOARD;SOFTWARE;BATTERY;IO BOARD;MAIN BOARD',
    'SCAN ENGINE;WHOLE UNIT;MAIN BOARD;MAIN BOARD;COAX CABLE;BRACKET;O-RING',
    'FOIL;BATTERY;CABLE;KEY BUTTON;SCAN ENGINE;ANTENNA;MINOR COMPONENT;SOFTWARE',
    'SCRAP;TRIGGER;HOUSING;GASKET;MAIN BOARD;WINDOW / LENS;MAIN BOARD;POWER BUTTON ASSEMBLY;CONNECTOR;FOIL;TAPE',
    'HOUSING + TP + DISPLAY;CABLE;FLEX STRIP;FRAME;CONNECTOR;BATTERY DOOR;FLEX STRIP;MINOR COMPONENT;STRAP;KEY BUTTON;SCAN ENGINE;HOLDER;HOLDER;VIBRATOR',
    'MAIN BOARD;SPEAKER;ADHESIVE;SPEAKER;FLEX STRIP;SOFTWARE;SCAN ENGINE ASSEMBLY;ADHESIVE',
    'HOUSING;MAIN BOARD;KEY BUTTON;SOFTWARE;SOFTWARE;SOFTWARE;FLEX STRIP;SOFTWARE;SOFTWARE;SOFTWARE;SOFTWARE;SOFTWARE;SOFTWARE;SOFTWARE;SOFTWARE',
    'PAD;TAPE;SOFTWARE;FLEX STRIP;SOFTWARE;SOFTWARE;SOFTWARE;BATTERY;FLEX STRIP;SOFTWARE',
    'SCAN ENGINE ASSEMBLY;PROTECTOR;MAIN BOARD;BRACKET;SOFTWARE;MAIN BOARD;SOFTWARE;FRAME;TRIGGER;TRIGGER',
    'CAMERA SCANNER ASSEMBLY;HOUSING;SUB BOARD;ANTENNA;MAIN BOARD;MEMORY;FLEX STRIP;MAIN BOARD;HOUSING;GRILL;MAIN BOARD;ANTENNA;FLEX STRIP;HOUSING;SUPERCAP',
    'RUBBER;MYLAR;MYLAR;GASKET;ANTENNA;GASKET;SPONGE;TAPE;GASKET;MYLAR;GASKET;MYLAR;SEAL;KEY BUTTON;SUPERCAP;GASKET;SPONGE;TAPE;MYLAR;MYLAR;LABELS',
    'SCAN ENGINE;ADHESIVE;LABEL;PAD;HOUSING;MYLAR;TAPE;DEFECTIVE SPEAKER',
    'FLEX STRIP;FLEX STRIP;HOUSING;PAD;GASKET;HOUSING + TP + DISPLAY;SENSOR;PAD;SUPERCAP;PAD;SCREW;LABEL',
    'SCAN ENGINE;HOUSING;TAPE;HOUSING;END CAP;SPONGE;PAD;ADHESIVE;TAPE;ADHESIVE;HOUSING;SHIELD;ADHESIVE;SCREW;SCREW;SCREW;TAPE;DOOR;LABEL',
    'HOUSING;ADHESIVE;BAFFLE;MAIN BOARD;CONNECTOR;PLUG;MAIN BOARD;HOUSING;HOUSING + TP;POWER BUTTON ASSEMBLY;HOUSING + TP + DISPLAY',
    'FLEX STRIP;LABEL;FLASH;CAMERA;BAFFLE;COVER;HOLDER;FLASH;BAFFLE;HOUSING;FRAME;CABLE;HOUSING;SPONGE;MAIN BOARD;FLEX STRIP;IO BOARD;SPONGE;FLEX STRIP;WINDOW / LENS',
    'MAIN BOARD;HOLDER;BUTTON CAP;RUBBER;BAFFLE;RUBBER BOOT;HOUSING;RUBBER;SOFTWARE;MAIN BOARD;ADHESIVE;DIAPER;HOLDER;COVER',
    'SCAN ENGINE ASSEMBLY;DISPLAY + TP;COVER;SCAN ENGINE;BATTERY;MYLAR;RECEIVER;KEY BUTTON;SOFTWARE;ADHESIVE;CONNECTOR',
    'SOFTWARE;DISPLAY;MAIN BOARD;ADHESIVE;BATTERY;LABEL;LABEL;LABEL;LABEL;LABEL',
    'HOUSING;TOUCH PANEL;SCAN ENGINE;ADHESIVE;MAIN BOARD;SOFTWARE;FLEX STRIP;MAIN SEAL',
    'SCAN ENGINE ASSEMBLY;ADHESIVE;RECEIVER;SPEAKER;SOFTWARE;ANTENNA;DOOR;SPACER;RETAINER;END CAP;MAIN BOARD;RECEIVER;WHOLE UNIT;ACCESSORY;SOFTWARE;ANTENNA;SOFTWARE;SD CARD DOOR',
    'GRILL;TOUCH PANEL;SENSOR;SPACER','DELAY;DAMAGE','PRINTHEAD','CHARGER','REAR CLEAT','BOOT','BATTERY PAD','HAND STRAP','SAM CARD ASSEMBLY','TURRET','CUTTER','PORT - PARALLEL','FLIPPER','PRINTER SOFTWARE','ACCESSORIES NON-REPAIRABLE','BATTERY CONN/FLEX','PORT - SERIAL'
]

st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)

# session state
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "admin_secret" not in st.session_state: st.session_state.admin_secret = ""
if "focus_text" not in st.session_state: st.session_state.focus_text = ""
if "subproducts_selected" not in st.session_state:
    st.session_state.subproducts_selected = [SUBPRODUCT_OPTIONS[0]] if SUBPRODUCT_OPTIONS else []

# ===== Sidebar =====
with st.sidebar:
    st.markdown("### Admin")
    env_admin = ADMIN_PASS or ""
    entered = st.text_input("Admin password", type="password", value="")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Login", use_container_width=True):
            st.session_state.is_admin = (env_admin and entered == env_admin)
            if st.session_state.is_admin:
                st.session_state.admin_secret = entered
                st.success("Admin mode enabled.")
            else:
                st.session_state.admin_secret = ""
                st.error("Invalid password.")
    with c2:
        if st.button("Logout", use_container_width=True):
            st.session_state.is_admin = False
            st.session_state.admin_secret = ""
            st.session_state.focus_text = ""
            st.info("Logged out.")

    if st.session_state.is_admin:
        st.markdown("### 🔒 Focus Prompt")
        st.caption("This guides DFMEA generation. **Samples are examples only.**")
        samples = [
            "Sample: Prioritize freezer-related failures; highlight condensation/low-temp display issues; exclude cosmetic-only defects.",
            "Sample: Emphasize sunlight readability; correlate luminance/contrast specs to field issues; focus on outdoor use.",
            "Sample: Focus on touch sensitivity degradation vs. environmental cycling, contamination, and glove usage.",
            "Sample: Elevate safety-critical failures; ensure detection controls reference validation test IDs.",
        ]
        chosen = st.selectbox("Sample prompts (examples only):", ["— choose a sample —"] + samples)
        s1, s2 = st.columns(2)
        with s1:
            if st.button("Insert sample", use_container_width=True) and chosen != "— choose a sample —":
                st.session_state.focus_text = chosen
        with s2:
            if st.button("Clear", use_container_width=True):
                st.session_state.focus_text = ""
        st.session_state.focus_text = st.text_area(
            "Focus (admin only)", value=st.session_state.focus_text, height=300,
            placeholder="Describe what to prioritize/exclude. e.g., link DFMEA to PRD requirement IDs; exclude cosmetic-only defects."
        )

    st.markdown("---")
    st.markdown("### Settings")
    api_url = st.text_input("Backend API URL", value=API_URL_DEFAULT)

    st.caption(f"Subproduct options loaded: **{len(SUBPRODUCT_OPTIONS)}**")
    st.session_state.subproducts_selected = st.multiselect(
        "Choose one or more subproducts",
        options=SUBPRODUCT_OPTIONS,
        default=st.session_state.subproducts_selected if st.session_state.subproducts_selected else SUBPRODUCT_OPTIONS[:1],
    )
    if not st.session_state.subproducts_selected:
        st.warning("Select at least one subproduct.")

# ===== Uploaders =====
st.markdown("#### 1) Upload PRDs / Specs (.docx / .csv / .xlsx)")
# (No legacy .doc — python-docx can’t parse it)
prd_files = st.file_uploader(
    "Upload one or more PRD/spec files",
    type=["docx", "csv", "xlsx"],
    accept_multiple_files=True,
    key="prd_uploader",
)

st.markdown("#### 2) Upload Knowledge Base (.csv / .xlsx)")
kb_files = st.file_uploader(
    "Upload one or more Knowledge Bank files (.csv / .xlsx)",
    type=["csv", "xlsx"],
    accept_multiple_files=True,
    key="kb_uploader",
)

st.markdown("#### 3) Upload Field Reported Issues (.csv / .xlsx)")
fri_files = st.file_uploader(
    "Upload one or more Field Reported Issues files (.csv / .xlsx)",
    type=["csv", "xlsx"],
    accept_multiple_files=True,
    key="fri_uploader",
)

def _mime_for(name_lower: str) -> str:
    if name_lower.endswith(".docx"):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if name_lower.endswith(".csv"):
        return "text/csv"
    if name_lower.endswith(".xlsx"):
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return "application/octet-stream"

def _preview_df(upload_file):
    """Robust preview: reset pointer; try csv then excel, then reverse."""
    try:
        upload_file.seek(0)
    except Exception:
        pass
    name = upload_file.name.lower()
    try:
        if name.endswith(".csv"):
            upload_file.seek(0)
            return pd.read_csv(upload_file).head(20)
        elif name.endswith(".xlsx"):
            upload_file.seek(0)
            return pd.read_excel(upload_file).head(20)
        else:
            return None
    except Exception:
        # fallback (in case extension mismatches content)
        try:
            upload_file.seek(0)
            return pd.read_excel(upload_file).head(20)
        except Exception:
            try:
                upload_file.seek(0)
                return pd.read_csv(upload_file).head(20)
            except Exception:
                return None

# ===== Create DFMEA =====
st.divider()
if st.button("✨ Create DFMEA", type="primary", use_container_width=True):
    if not (prd_files or kb_files or fri_files):
        st.warning("Please upload at least one file in PRDs, Knowledge Base, or Field Issues.")
    elif not st.session_state.subproducts_selected:
        st.warning("Please select at least one subproduct.")
    else:
        with st.spinner("Building DFMEA…"):
            files = []

            # Read into BYTES (no stream pointer problems)
            for f in (prd_files or []):
                content = f.getvalue()
                files.append(("prds", (f.name, content, _mime_for(f.name.lower()))))

            for f in (kb_files or []):
                content = f.getvalue()
                files.append(("knowledge_base", (f.name, content, _mime_for(f.name.lower()))))

            for f in (fri_files or []):
                content = f.getvalue()
                files.append(("field_issues", (f.name, content, _mime_for(f.name.lower()))))

            # Payload (fields)
            subproducts = st.session_state.subproducts_selected
            first_sub = subproducts[0]
            data = {
                "product": DEFAULT_PRODUCT,
                "subproduct": first_sub,                 # backward-compat
                "subproducts": json.dumps(subproducts),  # multi support
            }
            if st.session_state.is_admin and st.session_state.focus_text.strip():
                data["focus"] = st.session_state.focus_text.strip()

            headers = {}
            if st.session_state.is_admin and st.session_state.get("admin_secret"):
                headers["X-Admin-Auth"] = st.session_state["admin_secret"]

            try:
                resp = requests.post(api_url, data=data, files=files, timeout=300, headers=headers)

                # If server returned 4xx/5xx, show the server's message
                if not resp.ok:
                    try:
                        err = resp.json()
                        msg = err.get("detail") or err
                    except Exception:
                        msg = resp.text
                    raise RuntimeError(f"Backend returned {resp.status_code}: {msg}")

                payload = resp.json()

                st.success(f"DFMEA generated for {payload.get('product', DEFAULT_PRODUCT)} / {payload.get('subproduct', first_sub)}")
                st.caption(f"(Requested subproducts: {', '.join(subproducts)})")

                st.subheader("Preview JSON entries")
                st.json(payload.get("entries", []))

                if "excel_base64" in payload and payload["excel_base64"]:
                    xls_bytes = base64.b64decode(payload["excel_base64"])
                    st.download_button(
                        "⬇️ Download DFMEA Excel",
                        data=xls_bytes,
                        file_name=f"DFMEA_{payload.get('product', DEFAULT_PRODUCT)}_{first_sub}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )

                if payload.get("counts"):
                    st.caption(f"Ingestion counts: {payload['counts']}")
            except Exception as e:
                st.error(f"{e}")

# ===== Optional previews (robust) =====
st.divider()
c1, c2 = st.columns(2)
with c1:
    if kb_files:
        st.caption("Knowledge Base (first file preview)")
        df = _preview_df(kb_files[0])
        if df is not None:
            st.dataframe(df)
        else:
            st.warning("KB preview failed (format not recognized).")

with c2:
    if fri_files:
        st.caption("Field Issues (first file preview)")
        df = _preview_df(fri_files[0])
        if df is not None:
            st.dataframe(df)
        else:
            st.warning("Field preview failed (format not recognized).")

if prd_files:
    st.caption("PRD/Spec files uploaded:")
    st.write([f.name for f in prd_files])
    df = _preview_df(prd_files[0])
    if df is not None:
        st.caption("PRD/Spec preview (first file)")
        st.dataframe(df)

