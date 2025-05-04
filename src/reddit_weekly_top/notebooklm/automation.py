"""NotebookLM UI automation module."""

import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

@dataclass
class NotebookLMConfig:
    """Configuration for NotebookLM automation.
    
    Attributes:
        base_url: Base URL for NotebookLM.
        user_profile: Chrome user profile directory.
        wait_timeout: Default timeout for WebDriverWait.
    """
    base_url: str = "https://notebooklm.google/"
    user_profile: Optional[str] = None
    wait_timeout: int = 10

class NotebookLMAutomation:
    """Class for automating NotebookLM UI interactions.
    
    This class provides methods to automate various UI interactions with NotebookLM,
    including navigation and session management.
    """
    
    def __init__(self, config: Optional[NotebookLMConfig] = None):
        """Initialize NotebookLM automation.
        
        Args:
            config: Configuration for the automation. If None, default config is used.
        """
        self.config = config or NotebookLMConfig()
        self.driver: Optional[WebDriver] = None
        
    def setup_driver(self) -> WebDriver:
        """Set up and configure Chrome WebDriver.
        
        Returns:
            Configured WebDriver instance.
            
        Raises:
            RuntimeError: If driver setup fails.
        """
        try:
            options = ChromeOptions()
            if self.config.user_profile:
                options.add_argument(f"user-data-dir={self.config.user_profile}")
            
            # Add additional options for stability and security
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--start-maximized")
            
            # Make the browser appear more like a regular session
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # Add additional security-related options
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--ignore-certificate-errors")
            
            # Set user agent to a common Chrome version
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = ChromeService()
            driver = webdriver.Chrome(service=service, options=options)
            
            # Remove navigator.webdriver flag
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """
            })
            
            driver.implicitly_wait(5)
            return driver
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            raise RuntimeError(f"WebDriver setup failed: {e}") from e
    
    def start(self) -> None:
        """Start the automation session and wait for manual login.
        
        This method opens the NotebookLM page and waits for the user to log in manually.
        
        Raises:
            RuntimeError: If session start fails.
        """
        try:
            self.driver = self.setup_driver()
            logger.info("Opening NotebookLM page...")
            self.driver.get(self.config.base_url)
            
            # Wait for user to log in manually
            input("\nPlease log in manually in the browser window.\nPress Enter when you're logged in and ready to continue: ")
            logger.info("Continuing with automation...")
            
        except Exception as e:
            logger.error(f"Failed to start automation session: {e}")
            self.cleanup()
            raise RuntimeError(f"Session start failed: {e}") from e
    
    def verify_login_success(self) -> bool:
        """Verify successful login by checking for main interface elements.
        
        Returns:
            bool: True if login was successful, False otherwise.
        """
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
            
        try:
            # Wait a moment for the new tab to open
            time.sleep(2)
            
            # Switch to the last opened tab
            logger.info("Checking for new browser tabs...")
            handles = self.driver.window_handles
            if len(handles) > 1:
                logger.info(f"Found {len(handles)} tabs, switching to the last one")
                self.driver.switch_to.window(handles[-1])
            else:
                logger.info("No new tabs found, staying on current tab")
            
            # Wait for multiple possible elements that indicate successful login
            logger.info("Waiting for interface elements...")
            WebDriverWait(self.driver, self.config.wait_timeout).until(
                lambda d: any([
                    # Check for "Lisää lähde" button
                    len(d.find_elements(By.XPATH, "//button[contains(., 'Lisää lähde')]")) > 0,
                    # Check for "Chat" section
                    len(d.find_elements(By.XPATH, "//div[text()='Chat']")) > 0,
                    # Check for "Studio" section
                    len(d.find_elements(By.XPATH, "//div[text()='Studio']")) > 0,
                    # Check for "Lähteet" section
                    len(d.find_elements(By.XPATH, "//div[text()='Lähteet']")) > 0,
                    # Check for the "+" button to add source
                    len(d.find_elements(By.XPATH, "//button[contains(@aria-label, 'Lisää')]")) > 0
                ])
            )
            logger.info("Found NotebookLM interface elements")
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify login success: {e}")
            # Log current URL and tab info for debugging
            try:
                if self.driver:
                    logger.debug(f"Current URL: {self.driver.current_url}")
                    logger.debug(f"Number of tabs: {len(self.driver.window_handles)}")
            except:
                pass
            return False
    
    def cleanup(self) -> None:
        """Clean up resources and close the browser."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Failed to cleanup driver: {e}")
            finally:
                self.driver = None 