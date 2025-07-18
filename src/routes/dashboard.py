from flask import Blueprint, jsonify, request
import openpyxl
import os
from datetime import datetime, timedelta
from collections import defaultdict
from src.config import Config
from src.routes.auth import login_required

dashboard_bp = Blueprint("dashboard", __name__)

def get_sample_data():
    """Return sample data when Excel file is not available"""
    sample_data = [
        {
            "LOKASI GI / GIS / GITET": "GI Bandung",
            "STATUS": "Selesai",
            "SIFAT PEKERJAAN": "RUTIN",
            "KATEGORI": "TRAFO",
            "BAY / PHT": "BAY 1",
            "BULAN": "January",
            "TAHUN": "2024"
        },
        {
            "LOKASI GI / GIS / GITET": "GI Jakarta",
            "STATUS": "Progress",
            "SIFAT PEKERJAAN": "ANOMALI",
            "KATEGORI": "PMT",
            "BAY / PHT": "BAY 2",
            "BULAN": "February",
            "TAHUN": "2024"
        },
        {
            "LOKASI GI / GIS / GITET": "GI Surabaya",
            "STATUS": "Selesai",
            "SIFAT PEKERJAAN": "GANTI MTU",
            "KATEGORI": "CT",
            "BAY / PHT": "BAY 3",
            "BULAN": "March",
            "TAHUN": "2024"
        },
        {
            "LOKASI GI / GIS / GITET": "GI Bandung",
            "STATUS": "Progress",
            "SIFAT PEKERJAAN": "NON RUTIN",
            "KATEGORI": "IBT",
            "BAY / PHT": "BAY 4",
            "BULAN": "April",
            "TAHUN": "2024"
        },
        {
            "LOKASI GI / GIS / GITET": "GI Jakarta",
            "STATUS": "Selesai",
            "SIFAT PEKERJAAN": "RUTIN",
            "KATEGORI": "LA",
            "BAY / PHT": "BAY 5",
            "BULAN": "May",
            "TAHUN": "2024"
        },
        {
            "LOKASI GI / GIS / GITET": "GI Surabaya",
            "STATUS": "Progress",
            "SIFAT PEKERJAAN": "ANOMALI",
            "KATEGORI": "PMS",
            "BAY / PHT": "BAY 6",
            "BULAN": "June",
            "TAHUN": "2024"
        }
    ]
    
    filters = {
        "years": ["2024"],
        "months": ["January", "February", "March", "April", "May", "June"],
        "locations": ["GI Bandung", "GI Jakarta", "GI Surabaya"],
        "statuses": ["Selesai", "Progress"],
        "sifat_pekerjaan": ["RUTIN", "ANOMALI", "GANTI MTU", "NON RUTIN"],
        "kategori": ["TRAFO", "PMT", "CT", "IBT", "LA", "PMS"]
    }
    
    return sample_data, filters

def excel_date_to_datetime(excel_date):
    if isinstance(excel_date, (int, float)):
        return datetime(1899, 12, 30) + timedelta(days=excel_date)
    return None

def load_excel_data():
    # Try to find Excel file dynamically
    file_path = Config.find_excel_file()
    
    print(f"Looking for Excel file...")
    print(f"Found file path: {file_path}")
    
    # If no file found, return sample data for demo
    if not file_path:
        print("No Excel file found, using sample data")
        return get_sample_data()
    
    try:
        print(f"Attempting to load Excel file: {file_path}")
        workbook = openpyxl.load_workbook(file_path)
        print(f"Successfully loaded Excel file")
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        print(f"Using sample data instead")
        return get_sample_data()

    realisasi_sheet = workbook["REALISASI HAR GI"]
    realisasi_data = []

    header_row = 5
    headers = [cell.value for cell in realisasi_sheet[header_row]]

    for row_idx, row in enumerate(realisasi_sheet.iter_rows(min_row=header_row + 1, values_only=True)):
        if row[0] is not None:
            row_data = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    value = row[i]
                    if header == "BULAN" or header == "TAHUN":
                        # Assuming RENCANA (index 6) is the date source for BULAN/TAHUN
                        date_value = row[6] # RENCANA column
                        dt_obj = excel_date_to_datetime(date_value)
                        if dt_obj:
                            if header == "BULAN":
                                value = dt_obj.strftime("%B") # Full month name
                            elif header == "TAHUN":
                                value = str(dt_obj.year)
                        else:
                            value = None # Or some default like 'Unknown'
                    row_data[header] = value
            # Add URAIAN PEKERJAAN if available (assuming column index, adjust if needed)
            uraian_index = headers.index('URAIAN PEKERJAAN') if 'URAIAN PEKERJAAN' in headers else -1
            if uraian_index != -1 and uraian_index < len(row):
                row_data['URAIAN PEKERJAAN'] = row[uraian_index]
            realisasi_data.append(row_data)

    drop_list_sheet = workbook["drop list"]
    drop_list_data = {}
    
    # Extracting unique values for filters from the actual data
    # This is a more robust way than relying on the 'drop list' sheet structure
    years = sorted(list(set([item.get("TAHUN") for item in realisasi_data if item.get("TAHUN")]))) # New filter
    months = sorted(list(set([item.get("BULAN") for item in realisasi_data if item.get("BULAN")]))) # New filter
    locations = sorted(list(set([item.get("LOKASI GI / GIS / GITET") for item in realisasi_data if item.get("LOKASI GI / GIS / GITET")]))) # New filter
    statuses = sorted(list(set([item.get("STATUS") for item in realisasi_data if item.get("STATUS")]))) # New filter
    sifat_pekerjaan = sorted(list(set([item.get("SIFAT PEKERJAAN") for item in realisasi_data if item.get("SIFAT PEKERJAAN")]))) # New filter
    kategori = sorted(list(set([item.get("KATEGORI") for item in realisasi_data if item.get("KATEGORI")]))) # New filter

    return realisasi_data, {
        "years": years,
        "months": months,
        "locations": locations,
        "statuses": statuses,
        "sifat_pekerjaan": sifat_pekerjaan,
        "kategori": kategori
    }

def apply_filters(data, filters):
    filtered_data = data
    if filters.get("year") and filters["year"] != "Semua":
        filtered_data = [item for item in filtered_data if item.get("TAHUN") == filters["year"]]
    if filters.get("month") and filters["month"] != "Semua":
        filtered_data = [item for item in filtered_data if item.get("BULAN") == filters["month"]]
    if filters.get("location") and filters["location"] != "Semua":
        filtered_data = [item for item in filtered_data if item.get("LOKASI GI / GIS / GITET") == filters["location"]]
    if filters.get("status") and filters["status"] != "Semua":
        filtered_data = [item for item in filtered_data if item.get("STATUS") == filters["status"]]
    if filters.get("sifat_pekerjaan") and filters["sifat_pekerjaan"] != "Semua":
        filtered_data = [item for item in filtered_data if item.get("SIFAT PEKERJAAN") == filters["sifat_pekerjaan"]]
    if filters.get("kategori") and filters["kategori"] != "Semua":
        filtered_data = [item for item in filtered_data if item.get("KATEGORI") == filters["kategori"]]
    
    # Filter by Sub Bid
    if filters.get("sub_bid") and filters["sub_bid"] != "":
        def get_sub_bid_from_item(item):
            lokasi = item.get("LOKASI GI / GIS / GITET", "")
            sifat = item.get("SIFAT PEKERJAAN", "")
            
            if "Bandung" in lokasi or sifat == "RUTIN":
                return "HARGI"
            elif "Jakarta" in lokasi or sifat == "ANOMALI":
                return "HARJAR"
            elif "Surabaya" in lokasi or sifat in ["GANTI MTU", "NON RUTIN"]:
                return "HARPRO"
            
            # Default assignment based on hash of location
            hash_val = sum(ord(c) for c in lokasi) if lokasi else 0
            sub_bids = ["HARGI", "HARJAR", "HARPRO"]
            return sub_bids[hash_val % 3]
        
        filtered_data = [item for item in filtered_data if get_sub_bid_from_item(item) == filters["sub_bid"]]
    
    return filtered_data

@dashboard_bp.route("/data", methods=["GET"])
@login_required
def get_dashboard_data():
    try:
        realisasi_data, filters = load_excel_data()
        # Aggregate uraian data
        uraian_counts = defaultdict(int)
        for item in realisasi_data:
            uraian = item.get('URAIAN PEKERJAAN', 'Unknown')
            uraian_counts[uraian] += 1
        uraian_data = [{'uraian': k, 'count': v} for k, v in sorted(uraian_counts.items(), key=lambda x: x[1], reverse=True)]
        return jsonify({"data": realisasi_data, "filters": filters, "uraian_data": uraian_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/kpi", methods=["GET"])
@login_required
def get_kpi_data():
    try:
        realisasi_data, _ = load_excel_data()
        
        filters = {
            "year": request.args.get("year"),
            "month": request.args.get("month"),
            "location": request.args.get("location"),
            "status": request.args.get("status"),
            "sifat_pekerjaan": request.args.get("sifat_pekerjaan"),
            "kategori": request.args.get("kategori"),
            "sub_bid": request.args.get("sub_bid")
        }
        filtered_data = apply_filters(realisasi_data, filters)

        anomali_count = len([item for item in filtered_data if item.get("SIFAT PEKERJAAN", "").upper() == "ANOMALI"])
        ganti_mtu_count = len([item for item in filtered_data if item.get("SIFAT PEKERJAAN", "").upper() == "GANTI MTU"])
        rutin_count = len([item for item in filtered_data if item.get("SIFAT PEKERJAAN", "").upper() == "RUTIN"])
        non_rutin_count = len([item for item in filtered_data if item.get("SIFAT PEKERJAAN", "").upper() == "NON RUTIN"])
        
        total_har = len(filtered_data)
        total_gi_gitet = len(set([item.get("LOKASI GI / GIS / GITET") for item in filtered_data if item.get("LOKASI GI / GIS / GITET")]))
        # Assuming ULTG is derived from LOKASI GI / GIS / GITET for now, or needs a separate mapping
        # For simplicity, let's assume each unique LOKASI GI / GIS / GITET corresponds to an ULTG for now
        total_ultg = total_gi_gitet # Placeholder, needs actual ULTG data if available

        return jsonify({
            "anomali_count": anomali_count,
            "ganti_mtu_count": ganti_mtu_count,
            "rutin_count": rutin_count,
            "non_rutin_count": non_rutin_count,
            "total_har": total_har,
            "total_gi_gitet": total_gi_gitet,
            "total_ultg": total_ultg
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/charts/sifat-pekerjaan", methods=["GET"])
@login_required
def get_sifat_pekerjaan_chart_data():
    try:
        realisasi_data, _ = load_excel_data()
        filters = {
            "year": request.args.get("year"),
            "month": request.args.get("month"),
            "location": request.args.get("location"),
            "status": request.args.get("status"),
            "kategori": request.args.get("kategori"),
            "sub_bid": request.args.get("sub_bid")
        }
        filtered_data = apply_filters(realisasi_data, filters)

        sifat_counts = defaultdict(int)
        for item in filtered_data:
            sifat = item.get("SIFAT PEKERJAAN", "Unknown")
            sifat_counts[sifat] += 1
        
        return jsonify(sifat_counts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/charts/status-pekerjaan", methods=["GET"])
@login_required
def get_status_pekerjaan_chart_data():
    try:
        realisasi_data, _ = load_excel_data()
        filters = {
            "year": request.args.get("year"),
            "month": request.args.get("month"),
            "location": request.args.get("location"),
            "sifat_pekerjaan": request.args.get("sifat_pekerjaan"),
            "kategori": request.args.get("kategori"),
            "sub_bid": request.args.get("sub_bid")
        }
        filtered_data = apply_filters(realisasi_data, filters)

        status_counts = defaultdict(int)
        for item in filtered_data:
            status = item.get("STATUS", "Unknown")
            status_counts[status] += 1
        
        return jsonify(status_counts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/charts/lokasi-distribusi", methods=["GET"])
@login_required
def get_lokasi_distribusi_chart_data():
    try:
        realisasi_data, _ = load_excel_data()
        filters = {
            "year": request.args.get("year"),
            "month": request.args.get("month"),
            "status": request.args.get("status"),
            "sifat_pekerjaan": request.args.get("sifat_pekerjaan"),
            "kategori": request.args.get("kategori"),
            "sub_bid": request.args.get("sub_bid")
        }
        filtered_data = apply_filters(realisasi_data, filters)

        location_sifat_counts = defaultdict(lambda: defaultdict(int))
        for item in filtered_data:
            location = item.get("LOKASI GI / GIS / GITET", "Unknown")
            sifat = item.get("SIFAT PEKERJAAN", "Unknown")
            location_sifat_counts[location][sifat] += 1
        
        return jsonify(location_sifat_counts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/charts/equipment-distribution", methods=["GET"])
@login_required
def get_equipment_distribution_data():
    try:
        realisasi_data, _ = load_excel_data()
        filters = {
            "year": request.args.get("year"),
            "month": request.args.get("month"),
            "location": request.args.get("location"),
            "status": request.args.get("status"),
            "sifat_pekerjaan": request.args.get("sifat_pekerjaan"),
            "sub_bid": request.args.get("sub_bid")
        }
        filtered_data = apply_filters(realisasi_data, filters)

        equipment_counts = defaultdict(int)
        for item in filtered_data:
            # Try multiple possible field names for equipment data
            kategori = item.get("KATEGORI") or item.get("BAY / PHT") or "Unknown"
            if kategori and kategori != "Unknown":
                equipment_counts[kategori] += 1
        
        return jsonify(equipment_counts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/charts/sub-bid-distribution", methods=["GET"])
@login_required
def get_sub_bid_distribution_data():
    try:
        realisasi_data, _ = load_excel_data()
        filters = {
            "year": request.args.get("year"),
            "month": request.args.get("month"),
            "location": request.args.get("location"),
            "status": request.args.get("status"),
            "sifat_pekerjaan": request.args.get("sifat_pekerjaan"),
            "sub_bid": request.args.get("sub_bid")
        }
        filtered_data = apply_filters(realisasi_data, filters)

        # Simulate Sub Bid assignment based on location or work type
        def get_sub_bid_from_item(item):
            lokasi = item.get("LOKASI GI / GIS / GITET", "")
            sifat = item.get("SIFAT PEKERJAAN", "")
            
            if "Bandung" in lokasi or sifat == "RUTIN":
                return "HARGI"
            elif "Jakarta" in lokasi or sifat == "ANOMALI":
                return "HARJAR"
            elif "Surabaya" in lokasi or sifat in ["GANTI MTU", "NON RUTIN"]:
                return "HARPRO"
            
            # Default assignment based on hash of location
            hash_val = sum(ord(c) for c in lokasi) if lokasi else 0
            sub_bids = ["HARGI", "HARJAR", "HARPRO"]
            return sub_bids[hash_val % 3]

        sub_bid_counts = defaultdict(int)
        for item in filtered_data:
            sub_bid = get_sub_bid_from_item(item)
            sub_bid_counts[sub_bid] += 1
        
        return jsonify(sub_bid_counts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/file-info", methods=["GET"])
@login_required
def get_file_info():
    """Get current Excel file information"""
    try:
        current_file = Config.find_excel_file()
        return jsonify({
            "current_file": current_file,
            "configured_path": Config.EXCEL_FILE_PATH,
            "file_exists": current_file is not None,
            "using_sample_data": current_file is None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/set-file-path", methods=["POST"])
@login_required
def set_file_path():
    """Set new Excel file path"""
    try:
        data = request.get_json()
        new_path = data.get('file_path')
        
        if not new_path:
            return jsonify({"error": "file_path is required"}), 400
        
        success = Config.set_excel_path(new_path)
        if success:
            return jsonify({
                "message": "File path updated successfully",
                "new_path": new_path,
                "success": True
            })
        else:
            return jsonify({
                "error": "File not found at specified path",
                "path": new_path,
                "success": False
            }), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/search-files", methods=["GET"])
@login_required
def search_excel_files():
    """Search for Excel files in common locations"""
    try:
        search_locations = [
            'D:\\',
            'C:\\',
            os.path.dirname(os.path.dirname(__file__)),  # Project root
            os.getcwd(),  # Current working directory
        ]
        
        found_files = []
        
        for location in search_locations:
            try:
                if os.path.exists(location):
                    for file in os.listdir(location):
                        if file.lower().startswith('dashboard') and file.lower().endswith('.xlsx'):
                            full_path = os.path.join(location, file)
                            found_files.append({
                                "filename": file,
                                "full_path": full_path,
                                "location": location,
                                "size": os.path.getsize(full_path) if os.path.exists(full_path) else 0
                            })
            except (PermissionError, OSError):
                continue
        
        return jsonify({
            "found_files": found_files,
            "total_found": len(found_files)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



