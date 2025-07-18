from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def check_dashboard_values():
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        # Initialize Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        
        print("Mengakses dashboard...")
        driver.get("http://localhost:5000/dashboard")
        
        # Wait for page to load
        time.sleep(3)
        
        # Check if we're redirected to login
        current_url = driver.current_url
        if "login" in current_url:
            print("Dashboard memerlukan login. Melakukan login...")
            
            # Login first
            driver.get("http://localhost:5000/login")
            time.sleep(2)
            
            # Find and fill login form
            username_field = driver.find_element(By.NAME, "username")
            password_field = driver.find_element(By.NAME, "password")
            
            username_field.send_keys("admin")
            password_field.send_keys("admin123")
            
            # Submit form
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for redirect
            time.sleep(3)
            
            # Go to dashboard
            driver.get("http://localhost:5000/dashboard")
            time.sleep(5)  # Wait longer for dashboard to load
        
        # Take screenshot
        screenshot_path = os.path.join(os.getcwd(), "dashboard_screenshot.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot disimpan di: {screenshot_path}")
        
        # Check KPI values
        kpi_elements = {
            'ANOMALI': 'header-anomali',
            'GANTI MTU': 'header-ganti-mtu', 
            'RUTIN': 'header-rutin',
            'NON RUTIN': 'header-non-rutin',
            'TOTAL HAR': 'header-total-har',
            'TOTAL LOK': 'header-total'
        }
        
        print("\n=== HASIL PEMERIKSAAN KPI VALUES ===")
        all_values_ok = True
        
        for kpi_name, element_id in kpi_elements.items():
            try:
                element = driver.find_element(By.ID, element_id)
                value = element.text.strip()
                
                if value.lower() == 'error' or value == '':
                    print(f"❌ {kpi_name}: {value} (MASIH ERROR)")
                    all_values_ok = False
                else:
                    print(f"✅ {kpi_name}: {value}")
            except Exception as e:
                print(f"❌ {kpi_name}: Element tidak ditemukan - {str(e)}")
                all_values_ok = False
        
        print("\n=== RINGKASAN ===")
        if all_values_ok:
            print("🎉 SEMUA KPI VALUES SUDAH MUNCUL DENGAN BENAR!")
        else:
            print("⚠️  MASIH ADA KPI VALUES YANG ERROR")
        
        # Check if charts are loaded
        try:
            charts = driver.find_elements(By.TAG_NAME, "canvas")
            print(f"\n📊 Ditemukan {len(charts)} chart canvas elements")
            
            for i, chart in enumerate(charts):
                chart_id = chart.get_attribute('id')
                if chart_id:
                    print(f"   - Chart ID: {chart_id}")
        except Exception as e:
            print(f"Error checking charts: {str(e)}")
        
        return all_values_ok
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Memulai pemeriksaan dashboard...")
    success = check_dashboard_values()
    
    if success:
        print("\n✅ Dashboard berfungsi dengan baik!")
    else:
        print("\n❌ Dashboard masih memiliki masalah.")