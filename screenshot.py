from playwright.sync_api import sync_playwright
import time
import os

def take_screenshots():
    # Ensure assets directory exists
    os.makedirs('docs/assets', exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        
        # Navigate to frontend
        print("Navigating to http://localhost:3000...")
        
        # Dashboard screenshot
        page.goto('http://localhost:3000/dashboard')
        # Wait for charts or elements to render
        page.wait_for_timeout(3000)
        page.screenshot(path='docs/assets/dashboard.png', full_page=True)
        print("Dashboard screenshot saved to docs/assets/dashboard.png")
        
        # Analytics screenshot
        page.goto('http://localhost:3000/analytics')
        page.wait_for_timeout(3000)
        page.screenshot(path='docs/assets/analytics.png', full_page=True)
        print("Analytics screenshot saved to docs/assets/analytics.png")
        
        browser.close()

if __name__ == '__main__':
    take_screenshots()
