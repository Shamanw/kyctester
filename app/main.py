from fastapi import FastAPI, UploadFile, File, HTTPException
from passporteye import read_mrz
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = FastAPI()


def parse_yyMMdd(s: str) -> datetime:
    """Parse MRZ YYMMDD date format into a datetime object."""
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

    age = relativedelta(datetime.utcnow(), parse_yyMMdd(dob)).years
    return {
        "ok": True,
        "source": "MRZ",
        "sex_raw": sex,
        "is_female": sex == "F",
        "age": age,
        "is_18_plus": age >= 18,
    }
