import requests
import json
from bs4 import BeautifulSoup

def debug_dashboard():
    base_url = 'http://localhost:5000'
    
    # Create session
    session = requests.Session()
    
    print("=== DEBUGGING DASHBOARD ===")
    
    # 1. Test login
    print("\n1. Testing login...")
    login_data = {
        'username': 'admin',
        'password': '0ktahermawan#'
    }
    
    login_response = session.post(f'{base_url}/api/auth/login', json=login_data)
    print(f"Login status: {login_response.status_code}")
    if login_response.status_code == 200:
        print("✓ Login successful")
    else:
        print(f"✗ Login failed: {login_response.text}")
        return
    
    # 2. Test dashboard page
    print("\n2. Testing dashboard page...")
    dashboard_response = session.get(f'{base_url}/dashboard')
    print(f"Dashboard page status: {dashboard_response.status_code}")
    
    if dashboard_response.status_code == 200:
        print("✓ Dashboard page accessible")
        
        # Parse HTML to check for required elements
        soup = BeautifulSoup(dashboard_response.text, 'html.parser')
        
        # Check for KPI elements
        kpi_elements = [
            'header-anomali', 'header-ganti-mtu', 'header-rutin', 
            'header-non-rutin', 'header-total-har', 'header-total'
        ]
        
        print("\n3. Checking KPI elements in HTML...")
        missing_elements = []
        for element_id in kpi_elements:
            element = soup.find(id=element_id)
            if element:
                print(f"✓ Found element: {element_id}")
            else:
                print(f"✗ Missing element: {element_id}")
                missing_elements.append(element_id)
        
        if missing_elements:
            print(f"\nMissing elements: {missing_elements}")
        else:
            print("\n✓ All KPI elements found in HTML")
            
        # Check for JavaScript files
        print("\n4. Checking JavaScript includes...")
        scripts = soup.find_all('script', src=True)
        dashboard_js_found = False
        for script in scripts:
            src = script.get('src')
            print(f"Found script: {src}")
            if 'dashboard.js' in src:
                dashboard_js_found = True
        
        if dashboard_js_found:
            print("✓ dashboard.js included")
        else:
            print("✗ dashboard.js not found")
            
    else:
        print(f"✗ Dashboard page failed: {dashboard_response.text}")
        return
    
    # 3. Test API data
    print("\n5. Testing API data...")
    api_response = session.get(f'{base_url}/api/dashboard/data')
    print(f"API data status: {api_response.status_code}")
    
    if api_response.status_code == 200:
        data = api_response.json()
        print(f"✓ API data received: {len(data.get('data', []))} records")
        
        # Check first record structure
        if data.get('data'):
            first_record = data['data'][0]
            print("\n6. Sample record structure:")
            for key, value in first_record.items():
                print(f"  {key}: {value}")
                
            # Check for required fields
            required_fields = ['SIFAT PEKERJAAN', 'STATUS', 'LOKASI GI / GIS / GITET']
            print("\n7. Checking required fields...")
            for field in required_fields:
                if field in first_record:
                    print(f"✓ Found field: {field}")
                else:
                    print(f"✗ Missing field: {field}")
        else:
            print("✗ No data records found")
    else:
        print(f"✗ API data failed: {api_response.text}")
    
    print("\n=== DEBUG COMPLETE ===")

if __name__ == '__main__':
    debug_dashboard()