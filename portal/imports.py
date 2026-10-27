"""Bounded XLSX preview. No database mutations occur here."""
from io import BytesIO
from zipfile import BadZipFile, ZipFile
from openpyxl import load_workbook, Workbook

HEADERS = ('nis', 'kelas', 'nama_murid', 'email_wali', 'jenis_tagihan', 'nominal', 'denda', 'deskripsi', 'tahun_ajaran', 'periode', 'jatuh_tempo', 'referensi_tagihan', 'referensi_rekening', 'nomor_va')
MAX_BYTES = 2 * 1024 * 1024
MAX_EXPANDED = 10 * 1024 * 1024
MAX_ROWS = 2000

class ImportErrorDetail(ValueError):
    pass

def template_bytes():
    book = Workbook()
    sheet = book.active
    sheet.title = 'Tagihan'
    sheet.append(HEADERS)
    for column in ('A', 'B', 'D', 'L', 'M', 'N'):
        sheet.column_dimensions[column].width = 24
    output = BytesIO()
    book.save(output)
    return output.getvalue()

def preview_xlsx(data):
    if not data or len(data) > MAX_BYTES:
        raise ImportErrorDetail('Ukuran file maksimal 2 MB.')
    try:
        with ZipFile(BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) > 1000 or sum(x.file_size for x in entries) > MAX_EXPANDED:
                raise ImportErrorDetail('Isi file terlalu besar.')
        book = load_workbook(BytesIO(data), read_only=True, data_only=False, keep_links=False)
        try:
            sheet = book.active
            if sheet.max_column > 50 or sheet.max_row > MAX_ROWS + 1:
                raise ImportErrorDetail('File melebihi batas 2.000 baris atau 50 kolom.')
            rows = sheet.iter_rows()
            header = tuple(str(c.value or '').strip().lower() for c in next(rows))
            if header[:len(HEADERS)] != HEADERS:
                raise ImportErrorDetail('Kolom tidak sesuai template.')
            results = []
            for row_number, cells in enumerate(rows, start=2):
                cells = cells[:len(HEADERS)]
                if all(c.value is None for c in cells):
                    continue
                errors = []
                if any(c.data_type == 'f' for c in cells):
                    errors.append('Formula tidak diperbolehkan.')
                values = [c.value for c in cells]
                for i in (0, 1, 2, 3, 4, 8, 9, 10, 11):
                    if values[i] is None or not str(values[i]).strip():
                        errors.append(f'{HEADERS[i]} wajib diisi.')
                for i in (0, 11, 12, 13):
                    if values[i] is not None and not isinstance(values[i], str):
                        errors.append(f'{HEADERS[i]} harus berupa teks untuk menjaga nol di depan.')
                for i in (5, 6):
                    v = values[i]
                    if i == 6 and v is None:
                        continue
                    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
                        errors.append(f'{HEADERS[i]} harus bilangan bulat rupiah nonnegatif.')
                results.append({'row':row_number,'nis':str(values[0] or ''),'errors':errors})
            return results
        finally:
            book.close()
    except ImportErrorDetail:
        raise
    except (BadZipFile, ValueError, KeyError, IndexError, StopIteration, OSError):
        raise ImportErrorDetail('File XLSX tidak valid.') from None
