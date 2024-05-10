import json
import gspread
from time import sleep
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

HEADER_COLORS = {
    "red": 0.42,
    "green": 0.62,
    "blue": 0.92
}
SUBHEADER_COLORS = {
    "red": 0.79,
    "green": 0.85,
    "blue": 0.97
}
SUPPORTED_COLORS = {
    "red": 0.85,
    "green": 0.91,
    "blue": 0.82
}
PARTIAL_SUPPORTED_COLORS = {
    "red": 1,
    "green": 0.89,
    "blue": 0.60
}
NOT_SUPPORTED_COLORS = {
    "red": 0.95,
    "green": 0.80,
    "blue": 0.80
}
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
COMPANY_COLUMNS = {
    "Avicenna (Ethica)": ("C", "D"),
    "m-Path": ("E", "F"),
    "MetricWire": ("G", "H"),
    "Movisens": ("I", "J"),
}
CREDENTIALS = None
GSPREAD_CLIENT = None
GAPI_SERVICE = None
SHEET_ID = '1zRuZIJKE9mm90asM9U07MRmoJE51giFEUMJQhXZDf3Y'
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}'

def _load_feature_data():
    with open("EMA_Feature_Comparison.json", "r") as f:
        return json.load(f)

def _get_token_data():
    with open("gsheets_token.json", "r") as f:
        return json.load(f)

def _set_credentials_obj():
    global CREDENTIALS
    CREDENTIALS = Credentials.from_authorized_user_info(
        _get_token_data(), SCOPES
    )
    if not CREDENTIALS or not CREDENTIALS.valid:
        if CREDENTIALS and CREDENTIALS.expired and CREDENTIALS.refresh_token:
            CREDENTIALS.refresh(Request())

def _get_gspread_client():
    global GSPREAD_CLIENT
    if not GSPREAD_CLIENT:
        global CREDENTIALS
        if not CREDENTIALS:
            _set_credentials_obj()
        GSPREAD_CLIENT = gspread.authorize(CREDENTIALS)
    return GSPREAD_CLIENT

def _get_gapi_service():
    global GAPI_SERVICE
    if not GAPI_SERVICE:
        global CREDENTIALS
        if not CREDENTIALS:
            _set_credentials_obj()
        GAPI_SERVICE = build('sheets', 'v4', credentials=CREDENTIALS)
    return GAPI_SERVICE

data = _load_feature_data()
gspread_client = _get_gspread_client()
spreadsheet = gspread_client.open_by_url(SHEET_URL)
current_sheet = spreadsheet.add_worksheet(
    title="Competitive Landscape - WIP", rows=400, cols=30
)
spreadsheet.del_worksheet([
    x for x in spreadsheet.worksheets()
    if x.title == 'Competitive Landscape'
][0])
current_sheet.update_title('Competitive Landscape')

#
# Update formula
#

formula_details = []
grouping_details = []
header_color_row_ids = []
subheader_color_row_ids = []
visited_headers_stack = []
overall_score_row_counter = None
first_feature_sheet_row_id = None
last_feature_sheet_row_id = None
last_visited_header_id = None
last_visited_subheader_id = None

def _pop_from_stack_and_add_to_formula(lhid, ub):
    obj = visited_headers_stack.pop()
    obj["upper_bound"] = ub
    if lhid != 0:
        formula_details.append(obj)
    if obj["visited_subheader_id"] is None:
        glb = obj["lower_bound"] - 2
    else:
        glb = obj["lower_bound"] - 1
    grouping_details.append((glb, obj["upper_bound"]))

sheet_row_id = None
for row_counter, entry in enumerate(data):
    sheet_row_id = row_counter + 2
    row_id = entry["Row ID"]
    tokens = row_id.split(".")
    current_header_id = int(tokens[0])
    current_subheader_id = int(tokens[1]) if len(tokens) > 1 else None
    feature_name = entry["Feature Name"]
    print(f"Working on row {sheet_row_id} for {row_id} for {feature_name}")

    if feature_name == "Overall Score":
        overall_score_row_counter = row_counter # will be used in future itrs.

    if len(tokens) == 1:
        header_color_row_ids.append((current_header_id, sheet_row_id))
    elif len(tokens) == 2:
        subheader_color_row_ids.append((current_header_id, sheet_row_id))
    if row_id == "1.1.1":
        first_feature_sheet_row_id = sheet_row_id

    if (
        last_visited_header_id is None
        or last_visited_header_id != current_header_id
    ):
        if last_visited_header_id is not None: # Should pop previous ones
            # The last subheader finished 3 rows above
            _pop_from_stack_and_add_to_formula(
                last_visited_header_id, sheet_row_id - 1
            )
            # The last header also finished 3 rows above
            _pop_from_stack_and_add_to_formula(
                last_visited_header_id, sheet_row_id - 1
            )
        visited_headers_stack.append({
            "row_counter": row_counter,
            "visited_header_id": current_header_id,
            "visited_subheader_id": current_subheader_id,
            "lower_bound": sheet_row_id + 2,
            "upper_bound": None
        })
    elif (
        last_visited_subheader_id is None
        or last_visited_subheader_id != current_subheader_id
    ):
        # If current shid = 1, the pop happened when visiting the header.
        should_pop = (
            last_visited_subheader_id is not None
            and current_subheader_id != 1
        )
        if should_pop:
            # The last subheader finished 3 rows above
            _pop_from_stack_and_add_to_formula(
                last_visited_header_id, sheet_row_id - 1
            )
        visited_headers_stack.append({
            "row_counter": row_counter,
            "visited_header_id": current_header_id,
            "visited_subheader_id": current_subheader_id,
            "lower_bound": sheet_row_id + 1,
            "upper_bound": None
        })

    last_visited_header_id = current_header_id
    last_visited_subheader_id = current_subheader_id

while visited_headers_stack:
    obj = visited_headers_stack.pop()
    obj['upper_bound'] = sheet_row_id
    formula_details.append(obj)

formula_details.append({
    "row_counter": overall_score_row_counter,
    "lower_bound": first_feature_sheet_row_id,
    "upper_bound": sheet_row_id
})

for fd in formula_details:
    for company_name, company_columns in COMPANY_COLUMNS.items():
        lb = fd["lower_bound"]
        ub = fd["upper_bound"]
        sc = score_column = company_columns[0]
        data[fd["row_counter"]][f"{company_name} - Score"] = f"""=IFERROR(
            SUMPRODUCT(
                (REGEXMATCH(ARRAYFORMULA(
                    TO_TEXT({sc}{lb}:{sc}{ub})), \"^Supported$\") * 1) +
                (REGEXMATCH(ARRAYFORMULA(
                    TO_TEXT({sc}{lb}:{sc}{ub})), \"^Partial Support$\") * 0.5) +
                (REGEXMATCH(ARRAYFORMULA(
                    TO_TEXT({sc}{lb}:{sc}{ub})), \"^Not Supported$\") * 0)
            ) /
            (
                COUNTIF(ARRAYFORMULA(
                    TO_TEXT({sc}{lb}:{sc}{ub})), \"Supported\") +
                COUNTIF(ARRAYFORMULA(
                    TO_TEXT({sc}{lb}:{sc}{ub})), \"Partial Support\") +
                COUNTIF(ARRAYFORMULA(
                    TO_TEXT({sc}{lb}:{sc}{ub})), \"Not Supported\")
            ),
            \"No Public Content\"
        )"""

#
# Insert Data
#
keys = data[0].keys()
cells = []
for i, key in enumerate(keys):
    cells.append(gspread.Cell(row=1, col=i + 1, value=key))

for row_counter, entry in enumerate(data):
    for clm_counter, value in enumerate(entry.values()):
        cells.append(gspread.Cell(
            row=row_counter + 2, col=clm_counter + 1, value=value
        ))

current_sheet.update_cells(cells, value_input_option='USER_ENTERED')

sleep(5)
#
# Format them
#

# Freeze the first row.
current_sheet.freeze(rows=1, cols=2)
current_sheet.format("A:B",{
    "horizontalAlignment": "LEFT",
})
current_sheet.format("C:ZZ",{
    "horizontalAlignment": "CENTER",
})
current_sheet.format("A:ZZ", {"wrapStrategy": "CLIP"})
sleep(5)

# Group them
for gd in grouping_details:
    print(f'From {gd[0]} to {gd[1]}')
    current_sheet.add_dimension_group_rows(gd[0], gd[1])
    sleep(0.5)

# Color headers and subheaders, and mark the % rows as PercentNumberFormat
body_requests = [{
    "repeatCell": {
        "range": {
            "sheetId": current_sheet.id,
            "startRowIndex": overall_score_row_counter + 2 - 1,
            "endRowIndex": overall_score_row_counter + 2,
            "startColumnIndex": 2,
            "endColumnIndex": 50,
        },
        "cell": {
            "userEnteredFormat": {
                "numberFormat": {
                    "type": "PERCENT",
                    "pattern": "0.00%"
                }
            }
        },
        "fields": "userEnteredFormat.numberFormat"
    }
},
{
    "addConditionalFormatRule": {
        "index": 0,
        "rule": {
            "ranges": [
                {
                    "sheetId": current_sheet.id,
                    "startRowIndex": 0,
                    "endRowIndex": 500,
                }
            ],
            "booleanRule": {
                "condition": {
                    "type": "TEXT_EQ",
                    "values": [{"userEnteredValue": "Supported"}]
                },
                "format": {"backgroundColor": SUPPORTED_COLORS,}
            }
        },
    }
},
{
    "addConditionalFormatRule": {
        "index": 1,
        "rule": {
            "ranges": [
                {
                    "sheetId": current_sheet.id,
                    "startRowIndex": 0,
                    "endRowIndex": 500,
                }
            ],
            "booleanRule": {
                "condition": {
                    "type": "TEXT_EQ",
                    "values": [{"userEnteredValue": "Partial Support"}]
                },
                "format": {"backgroundColor": PARTIAL_SUPPORTED_COLORS,}
            }
        },
    }
},
{
    "addConditionalFormatRule": {
        "index": 2,
        "rule": {
            "ranges": [
                {
                    "sheetId": current_sheet.id,
                    "startRowIndex": 0,
                    "endRowIndex": 500,
                }
            ],
            "booleanRule": {
                "condition": {
                    "type": "TEXT_EQ",
                    "values": [{"userEnteredValue": "Not Supported"}]
                },
                "format": {"backgroundColor": NOT_SUPPORTED_COLORS,}
            }
        },
    }
},
{
    "addConditionalFormatRule": {
        "index": 2,
        "rule": {
            "ranges": [
                {
                    "sheetId": current_sheet.id,
                    "startRowIndex": 0,
                    "endRowIndex": 500,
                }
            ],
            "booleanRule": {
                "condition": {
                    "type": "CUSTOM_FORMULA",
                    "values": [{"userEnteredValue": "=REGEXMATCH(TO_TEXT(INDIRECT(\"A\" & ROW())), \"^\d+$\")"}]
                },
                "format": {"backgroundColor": HEADER_COLORS,}
            }
        },
    }
},
{
    "addConditionalFormatRule": {
        "index": 2,
        "rule": {
            "ranges": [
                {
                    "sheetId": current_sheet.id,
                    "startRowIndex": 0,
                    "endRowIndex": 500,
                }
            ],
            "booleanRule": {
                "condition": {
                    "type": "CUSTOM_FORMULA",
                    "values": [{"userEnteredValue": "=REGEXMATCH(TO_TEXT(INDIRECT(\"A\" & ROW())), \"^\d+\.\d+$\")"}]
                },
                "format": {"backgroundColor": SUBHEADER_COLORS,}
            }
        },
    }
},
]
for rid in header_color_row_ids:
    header_id = rid[0]
    sheet_row_id = rid[1]
    if header_id != 0:
        body_requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": current_sheet.id,
                    "startRowIndex": sheet_row_id - 1,
                    "endRowIndex": sheet_row_id,
                    "startColumnIndex": 2,
                    "endColumnIndex": 50,
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {
                            "type": "PERCENT",
                            "pattern": "0.00%"
                        }
                    }
                },
                "fields": "userEnteredFormat.numberFormat"
            }
        })
for rid in subheader_color_row_ids:
    header_id = rid[0]
    sheet_row_id = rid[1]
    if header_id != 0:
        body_requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": current_sheet.id,
                    "startRowIndex": sheet_row_id - 1,
                    "endRowIndex": sheet_row_id,
                    "startColumnIndex": 2,
                    "endColumnIndex": 50,
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {
                            "type": "PERCENT",
                            "pattern": "0.00%"
                        }
                    }
                },
                "fields": "userEnteredFormat.numberFormat"
            }
        })
gapi = _get_gapi_service()
response = gapi.spreadsheets().batchUpdate(
    spreadsheetId=SHEET_ID, body={ 'requests': body_requests }
).execute()