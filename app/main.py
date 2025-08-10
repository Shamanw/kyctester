from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from passporteye import read_mrz
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = FastAPI()

# Enable permissive CORS so the endpoint can be accessed from browsers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_yyMMdd(s: str) -> datetime:
    """Parse MRZ YYMMDD date format into a datetime object.

    The MRZ date field is expected to contain exactly six digits. If the value
    is malformed or contains non-digit characters the function raises a
    ``ValueError`` to allow the caller to react appropriately.
    """

    if len(s) != 6 or not s.isdigit():
        raise ValueError(f"Invalid date format: {s}")

    yy, mm, dd = int(s[:2]), int(s[2:4]), int(s[4:6])
    year = 1900 + yy if yy > 50 else 2000 + yy
    return datetime(year, mm, dd)


@app.post("/verify")
async def verify(file: UploadFile = File(...)):
    """Verify MRZ information from an uploaded image."""
    img = await file.read()
    with open("/tmp/_doc.jpg", "wb") as f:
        f.write(img)

    mrz = read_mrz("/tmp/_doc.jpg")
    if not mrz:
        raise HTTPException(status_code=400, detail="MRZ not found")

    data = mrz.to_dict()
    sex = (data.get("sex") or "").upper()
    dob = data.get("date_of_birth")
    if not dob:
        raise HTTPException(status_code=400, detail="DOB not found in MRZ")

    try:
        age = relativedelta(datetime.utcnow(), parse_yyMMdd(dob)).years
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid DOB format in MRZ")
    return {
        "ok": True,
        "source": "MRZ",
        "sex_raw": sex,
        "is_female": sex == "F",
        "age": age,
        "is_18_plus": age >= 18,
    }
