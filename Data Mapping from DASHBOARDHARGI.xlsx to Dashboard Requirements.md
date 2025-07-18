
## Data Mapping from DASHBOARDHARGI.xlsx to Dashboard Requirements

### REALISASI HAR GI Sheet

**Excel Column** | **Dashboard Requirement** | **Notes**
-----------------|-------------------------|----------
NO               | No                      | Direct match
URAIAN PEKERJAAN | Uraian Pekerjaan        | Direct match
BAY / PHT        | ULTG                    | Needs clarification: `BAY / PHT` seems to be a specific location within a `GI`. The requirement asks for `ULTG`. I will assume `BAY / PHT` maps to `ULTG` for now, but this might need adjustment.
LOKASI GI / GIS / GITET | GI                   | Direct match
SIFAT PEKERJAAN  | Jenis Pekerjaan         | Direct match
KATEGORI         | UPT                     | Needs clarification: `KATEGORI` seems to be a type of equipment (e.g., BAY, TRAFO), while `UPT` is a regional unit. This is a significant mismatch and needs to be addressed.
RENCANA          | RAB (Rp)                | `RENCANA` seems to be a numerical value, likely representing the budget (RAB). Need to confirm if it's in Rupiah.
BULAN            | Bulan                   | Direct match, but contains Excel formulas. Data will need to be extracted as actual month names.
TAHUN            | (Implicit in Bulan)     | Not explicitly requested as a separate column, but useful for filtering. Contains Excel formulas.
REALISASI        | Realisasi (Rp)          | Direct match, numerical value.
STATUS           | Status                  | Direct match.

**Missing from Excel, present in requirements:**
- Keterangan: This column is not present in the Excel sheet but is listed in the requirements. I will assume it's not critical for the initial dashboard and can be added later if needed.

### drop list Sheet

**Excel Column** | **Dashboard Requirement** | **Notes**
-----------------|-------------------------|----------
Column 2 (e.g., 'BAY', 'CT') | Bulan, UPT, ULTG, Status | This sheet seems to contain various dropdown options. The `pasted_content.txt` specifies that `drop list` contains `Bulan, UPT, ULTG, Status`. However, the Excel sheet shows values like 'BAY', 'CT', 'ANOMALI', 'GANTI MTU', 'NON RUTIN', 'RUTIN'. This needs further investigation to correctly map to the required filters.

**Initial Data Cleaning/Transformation Needs:**
1. **Date Extraction:** The `BULAN` and `TAHUN` columns in `REALISASI HAR GI` contain Excel formulas. These will need to be parsed to extract the actual month and year values.
2. **Column Mapping Discrepancies:** The `BAY / PHT` to `ULTG` and `KATEGORI` to `UPT` mappings are problematic and require clarification from the user or a re-evaluation of the data source.
3. **`drop list` Sheet Interpretation:** The structure of the `drop list` sheet does not directly align with the expected `Bulan, UPT, ULTG, Status` columns. I need to understand how these values are intended to be used for filtering.


