"""
Browser Controller Module

This module handles browser automation for CRM updates.
"""
import time
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager


class BrowserController:
    def __init__(self, config=None):
        """
        Initialize the browser controller
        
        Args:
            config: Dictionary containing configuration options
        """
        self.config = config or {}
        self.driver = None
        self.timeout = self.config.get('timeout', 10)  # Default timeout for waits
        self.logger = logging.getLogger(__name__)
    
    def __del__(self):
        """Ensure driver is closed when object is destroyed"""
        self.close()
    
    def start_browser(self, headless=False):
        """
        Start the browser session
        
        Args:
            headless: Boolean indicating if browser should run in headless mode
            
        Returns:
            Boolean indicating if browser was started successfully
        """
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless=new")  # Updated for newer Chrome versions
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            try:
                # First try using the WebDriver Manager for automatic driver management
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as driver_error:
                self.logger.warning(f"Failed to use WebDriverManager: {str(driver_error)}")
                
                # Fallback to the default Chrome driver path
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                except Exception as fallback_error:
                    self.logger.error(f"Failed to start Chrome with default path: {str(fallback_error)}")
                    return False
            
            self.driver.maximize_window()
            return True
        except Exception as e:
            self.logger.error(f"Error starting browser: {str(e)}")
            return False
    
    def close(self):
        """Close the browser session"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"Error closing browser: {str(e)}")
            finally:
                self.driver = None
    
    def navigate_to(self, url):
        """
        Navigate to a specific URL
        
        Args:
            url: URL to navigate to
            
        Returns:
            Boolean indicating if navigation was successful
        """
        if not self.driver:
            return False
            
        try:
            self.driver.get(url)
            return True
        except Exception as e:
            self.logger.error(f"Error navigating to {url}: {str(e)}")
            return False
    
    def wait_for_element(self, locator_type, locator_value, timeout=None):
        """
        Wait for an element to be visible on the page
        
        Args:
            locator_type: Type of locator (e.g., By.ID, By.XPATH)
            locator_value: Value of the locator
            timeout: Timeout in seconds (defaults to self.timeout)
            
        Returns:
            WebElement if found, None otherwise
        """
        if not self.driver:
            return None
            
        timeout = timeout or self.timeout
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(
                EC.visibility_of_element_located((locator_type, locator_value))
            )
            return element
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for element: {locator_type}={locator_value}")
            return None
        except Exception as e:
            self.logger.error(f"Error waiting for element: {str(e)}")
            return None
    
    def find_element(self, locator_type, locator_value):
        """
        Find an element on the page
        
        Args:
            locator_type: Type of locator (e.g., By.ID, By.XPATH)
            locator_value: Value of the locator
            
        Returns:
            WebElement if found, None otherwise
        """
        if not self.driver:
            return None
            
        try:
            return self.driver.find_element(locator_type, locator_value)
        except NoSuchElementException:
            self.logger.warning(f"Element not found: {locator_type}={locator_value}")
            return None
        except Exception as e:
            self.logger.error(f"Error finding element: {str(e)}")
            return None
    
    def click_element(self, locator_type, locator_value, wait_time=0):
        """
        Click on an element
        
        Args:
            locator_type: Type of locator (e.g., By.ID, By.XPATH)
            locator_value: Value of the locator
            wait_time: Time to wait after clicking (in seconds)
            
        Returns:
            Boolean indicating if click was successful
        """
        if not self.driver:
            return False
            
        element = self.wait_for_element(locator_type, locator_value)
        if not element:
            return False
            
        try:
            element.click()
            if wait_time > 0:
                time.sleep(wait_time)
            return True
        except ElementClickInterceptedException:
            # Try with JavaScript if normal click fails
            try:
                self.driver.execute_script("arguments[0].click();", element)
                if wait_time > 0:
                    time.sleep(wait_time)
                return True
            except Exception as e:
                self.logger.error(f"Error clicking element with JavaScript: {str(e)}")
                return False
        except Exception as e:
            self.logger.error(f"Error clicking element: {str(e)}")
            return False
    
    def input_text(self, locator_type, locator_value, text, clear_first=True):
        """
        Input text into an element
        
        Args:
            locator_type: Type of locator (e.g., By.ID, By.XPATH)
            locator_value: Value of the locator
            text: Text to input
            clear_first: Boolean indicating if field should be cleared first
            
        Returns:
            Boolean indicating if input was successful
        """
        if not self.driver:
            return False
            
        element = self.wait_for_element(locator_type, locator_value)
        if not element:
            return False
            
        try:
            if clear_first:
                element.clear()
            element.send_keys(text)
            return True
        except Exception as e:
            self.logger.error(f"Error inputting text: {str(e)}")
            return False
    
    def get_text(self, locator_type, locator_value):
        """
        Get text from an element
        
        Args:
            locator_type: Type of locator (e.g., By.ID, By.XPATH)
            locator_value: Value of the locator
            
        Returns:
            Text of the element if found, empty string otherwise
        """
        if not self.driver:
            return ""
            
        element = self.wait_for_element(locator_type, locator_value)
        if not element:
            return ""
            
        try:
            return element.text
        except Exception as e:
            self.logger.error(f"Error getting text: {str(e)}")
            return ""
    
    def execute_script(self, script, *args):
        """
        Execute JavaScript on the page
        
        Args:
            script: JavaScript to execute
            *args: Arguments to pass to the script
            
        Returns:
            Result of the script execution, or None if there was an error
        """
        if not self.driver:
            return None
            
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self.logger.error(f"Error executing script: {str(e)}")
            return None
    
    def take_screenshot(self, file_path):
        """
        Take a screenshot of the current page
        
        Args:
            file_path: Path to save the screenshot
            
        Returns:
            Boolean indicating if screenshot was taken successfully
        """
        if not self.driver:
            return False
            
        try:
            self.driver.save_screenshot(file_path)
            return True
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            return False