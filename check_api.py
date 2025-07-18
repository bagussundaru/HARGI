import requests
import json

def check_dashboard_api():
    base_url = "http://localhost:5000"
    
    # Create session
    session = requests.Session()
    
    try:
        print("=== TESTING DASHBOARD API ===")
        
        # 1. Check auth status
        print("\n1. Checking authentication status...")
        auth_response = session.get(f"{base_url}/api/auth/status")
        print(f"Auth Status: {auth_response.status_code}")
        print(f"Auth Response: {auth_response.json()}")
        
        # 2. Login
        print("\n2. Attempting login...")
        login_data = {
            "username": "admin",
            "password": "0ktahermawan#"
        }
        login_response = session.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login Status: {login_response.status_code}")
        print(f"Login Response: {login_response.json()}")
        
        if login_response.status_code != 200:
            print("❌ Login failed!")
            return False
        
        # 3. Check auth status after login
        print("\n3. Checking authentication status after login...")
        auth_response = session.get(f"{base_url}/api/auth/status")
        print(f"Auth Status: {auth_response.status_code}")
        auth_data = auth_response.json()
        print(f"Auth Response: {auth_data}")
        
        if not auth_data.get('authenticated', False):
            print("❌ Authentication failed!")
            return False
        
        # 4. Get dashboard data
        print("\n4. Fetching dashboard data...")
        data_response = session.get(f"{base_url}/api/dashboard/data")
        print(f"Data Status: {data_response.status_code}")
        
        if data_response.status_code != 200:
            print(f"❌ Failed to get dashboard data: {data_response.text}")
            return False
        
        dashboard_data = data_response.json()
        
        # 5. Analyze dashboard data
        print("\n5. Analyzing dashboard data...")
        print(f"Data keys: {list(dashboard_data.keys())}")
        
        if 'data' in dashboard_data:
            data_count = len(dashboard_data['data'])
            print(f"📊 Total data records: {data_count}")
            
            if data_count > 0:
                print("✅ Dashboard has data!")
                
                # Sample first record
                sample_record = dashboard_data['data'][0]
                print(f"📝 Sample record keys: {list(sample_record.keys())}")
                
                # Check for required fields
                required_fields = ['SIFAT PEKERJAAN', 'LOKASI', 'STATUS']
                missing_fields = []
                for field in required_fields:
                    if field not in sample_record:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"⚠️  Missing fields: {missing_fields}")
                else:
                    print("✅ All required fields present")
                
                return True
            else:
                print("❌ No data records found!")
                return False
        else:
            print("❌ No 'data' key in response!")
            print(f"Response structure: {dashboard_data}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Memulai pemeriksaan API dashboard...")
    success = check_dashboard_api()
    
    if success:
        print("\n🎉 API DASHBOARD BERFUNGSI DENGAN BAIK!")
        print("Data berhasil dimuat dan siap ditampilkan di dashboard.")
    else:
        print("\n❌ API DASHBOARD BERMASALAH!")
        print("Perlu investigasi lebih lanjut.")