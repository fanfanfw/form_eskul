import io
import zipfile

from fastapi import HTTPException
from openpyxl import Workbook

from main import read_students_excel


def xlsx(sheets):
    workbook = Workbook()
    workbook.remove(workbook.active)
    for title, rows in sheets:
        sheet = workbook.create_sheet(title)
        for row in rows:
            sheet.append(row)
    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()


def ids(data):
    return {row["nama"]: row["nis"] for row in read_students_excel(data)["rows"]}


real = read_students_excel(open("DATA SISWA 2627.xlsx", "rb").read())
assert len(real["rows"]) == 728
assert len(real["sheets"]) == 26
assert not real["skipped"]

multi = read_students_excel(xlsx([
    ("Kelas 1A", [["Nama", "JK"], ["Ani", "P"]]),
    ("Data", [["Judul"], ["Nama", "JK", "Kelas"], ["Budi", "L", "2b"]]),
]))
assert [(row["nama"], row["kelas"]) for row in multi["rows"]] == [("Ani", "Kelas 1A"), ("Budi", "Kelas 2B")]

try:
    read_students_excel(xlsx([("Laporan", [["Nama", "Keterangan"], ["Ani", "Baik"], ["Kelas 3A", None]])]))
    raise AssertionError("false-positive report accepted")
except HTTPException as error:
    assert error.status_code == 400

before = xlsx([("Kelas 4A", [["Nama", "JK"], ["Ani", "P"], ["Budi", "L"]])])
after = xlsx([("Kelas 4 A", [["Judul"], ["Nama", "JK"], ["Budi", "L"], ["Ani", "P"]])])
assert ids(before) == ids(after)

duplicates_before = read_students_excel(xlsx([("Kelas 4A", [["Nama", "JK"], ["Ani", "P"], ["Ani", "P"]])]))
duplicates_after = read_students_excel(xlsx([("Kelas 4 A", [["Judul"], ["Nama", "JK"], ["Ani", "P"], ["Ani", "P"]])]))
assert {row["nis"] for row in duplicates_before["rows"]} == {row["nis"] for row in duplicates_after["rows"]}

try:
    read_students_excel(xlsx([("Kelas 2A", [["Nama", "JK"], ["Ani", ""]])]))
    raise AssertionError("missing gender accepted")
except HTTPException as error:
    assert error.status_code == 400

try:
    read_students_excel(xlsx([("Data", [["Nama", "JK", "Kelas"], ["Ani", "P", "foo Kelas 2A bar"]])]))
    raise AssertionError("invalid class accepted")
except HTTPException as error:
    assert error.status_code == 400

payload = io.BytesIO()
with zipfile.ZipFile(payload, "w") as archive:
    info = zipfile.ZipInfo("large")
    info.file_size = 51 * 1024 * 1024
    archive.writestr(info, b"")
try:
    read_students_excel(payload.getvalue())
    raise AssertionError("invalid workbook accepted")
except HTTPException as error:
    assert error.status_code == 400

print("importer audit tests passed")
