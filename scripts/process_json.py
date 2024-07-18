# TODO:
# 1. If value of a "Coverage" is anything other than "Supported", "Not Supported",
#   and "Partial Support", raise an exception.
# 2. Create a tool to set the value of IDs. 
import json
import gspread
import os
from time import sleep
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

CATEGORY_COLORS = {
    "red": 0.42,
    "green": 0.62,
    "blue": 0.92
}
SUBCATEGORY_COLORS = {
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
    "ExpiWell": ("E", "F"),
    "m-Path": ("G", "H"),
    "mEMA": ("I", "J"),
    "MetricWire": ("K", "L"),
    "Movisens": ("M", "N"),
}
CREDENTIALS = None
GSPREAD_CLIENT = None
GAPI_SERVICE = None
SHEET_ID = os.getenv('GSHEET_ID')
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}'

def _load_feature_data():
    with open("EMA_Feature_Map.json", "r") as f:
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
spreadsheet.del_worksheet([
    x for x in spreadsheet.worksheets()
    if x.title == 'Feature Map'
][0])
current_sheet = spreadsheet.add_worksheet(
    title="Feature Map", rows=400, cols=30
)

#
# Update formula
#

formula_details = []
grouping_details = []
category_color_row_ids = []
subcategory_color_row_ids = []
overall_coverage_row_index = None
row_id = 1 # ID of the row in spreadsheet (starts from 1)
feature_start = float("inf")

flat_data = []
for ic, cat in enumerate(data["categories"]):
    cat_id = int(cat["Row ID"])
    row_id += 1
    cur_cat_row_id = row_id
    print(f"Working on row {row_id} - {cat['Feature Name']}")
    category_color_row_ids.append((cat_id, cur_cat_row_id))
    flat_data.append({k: v for k, v in cat.items() if k != "subcategories"})
    cat_feature_start = float("inf")
    cat_feature_end = float("-inf")

    for isc, subcat in enumerate(cat["subcategories"]):
        subcat_id = int(subcat["Row ID"].split(".")[1])
        row_id += 1
        cur_subcat_row_id = row_id
        print(f"Working on row {row_id} - {subcat['Feature Name']}")
        subcategory_color_row_ids.append((cat_id, cur_subcat_row_id))
        flat_data.append({k: v for k, v in subcat.items() if k != "features"})

        subcat_feature_start = float("inf")
        subcat_feature_end = float("-inf")
        for ifr, feature in enumerate(subcat["features"]):
            row_id += 1
            feature_name = feature["Feature Name"]
            print(f"Working on row {row_id} - {feature_name}")
            cat_feature_start = min(cat_feature_start, row_id)
            cat_feature_end = max(cat_feature_end, row_id)
            subcat_feature_start = min(subcat_feature_start, row_id)
            subcat_feature_end = max(subcat_feature_end, row_id)

            if feature_name == "Overall Coverage":
                # Save the address of "Overall Coverage" feature
                overall_coverage_row_index = row_id
            if feature["Row ID"] == "1.1.1":
                feature_start = row_id
            flat_data.append(feature)

        formula_details.append({
            "row_index": cur_subcat_row_id - 2,
            "lower_bound": subcat_feature_start,
            "upper_bound": subcat_feature_end
        })
        grouping_details.append((cur_subcat_row_id, row_id))
    formula_details.append({
        "row_index": cur_cat_row_id - 2,
        "lower_bound": cat_feature_start,
        "upper_bound": cat_feature_end
    })
    grouping_details.append((cur_cat_row_id, row_id))
formula_details.append({
    "row_index": overall_coverage_row_index - 2,
    "lower_bound": feature_start,
    "upper_bound": row_id
})

for fd in formula_details:
    for company_name, company_columns in COMPANY_COLUMNS.items():
        lb = fd["lower_bound"]
        ub = fd["upper_bound"]
        sc = coverage_column = company_columns[0]
        flat_data[fd["row_index"]][f"{company_name} - Coverage"] = f"""=IFERROR(
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
keys = flat_data[0].keys()
cells = []
for i, key in enumerate(keys):
    cells.append(gspread.Cell(row=1, col=i + 1, value=key))

for row_counter, entry in enumerate(flat_data):
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
    print(f'Grouping from {gd[0]} to {gd[1]}')
    current_sheet.add_dimension_group_rows(gd[0], gd[1])
    sleep(1)

# Color categories and subcategories, and mark the % rows as PercentNumberFormat
body_requests = [{
    "repeatCell": {
        "range": {
            "sheetId": current_sheet.id,
            "startRowIndex": overall_coverage_row_index - 1,
            "endRowIndex": overall_coverage_row_index,
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
                "format": {"backgroundColor": CATEGORY_COLORS,}
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
                "format": {"backgroundColor": SUBCATEGORY_COLORS,}
            }
        },
    }
},
]
for rid in category_color_row_ids:
    category_id = rid[0]
    sheet_row_id = rid[1]
    if category_id != 0:
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
for rid in subcategory_color_row_ids:
    category_id = rid[0]
    sheet_row_id = rid[1]
    if category_id != 0:
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