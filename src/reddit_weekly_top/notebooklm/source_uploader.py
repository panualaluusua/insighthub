"""NotebookLM source uploader module for automating URL source uploads."""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from reddit_weekly_top.notebooklm.automation import NotebookLMAutomation, NotebookLMConfig

logger = logging.getLogger(__name__)

@dataclass
class SourceUploaderConfig(NotebookLMConfig):
    """Configuration for NotebookLM source uploader.
    
    Attributes:
        urls: List of URLs to upload as sources.
        upload_delay: Delay in seconds between URL uploads.
        max_retries: Maximum number of retries for failed uploads.
        retry_delay: Delay in seconds between retries.
        processed_urls: Set of URLs that have been processed.
        keep_browser_open: Whether to keep the browser open after completion.
    """
    urls: List[str] = field(default_factory=list)
    upload_delay: float = 2.0
    max_retries: int = 3
    retry_delay: float = 5.0
    processed_urls: Set[str] = field(default_factory=set)
    keep_browser_open: bool = True

    @classmethod
    def from_file(cls, url_file: Path, **kwargs) -> "SourceUploaderConfig":
        """Create configuration from a file containing URLs.
        
        Args:
            url_file: Path to file containing URLs (one per line).
            **kwargs: Additional configuration parameters.
            
        Returns:
            SourceUploaderConfig instance.
            
        Raises:
            FileNotFoundError: If URL file doesn't exist.
        """
        if not url_file.exists():
            raise FileNotFoundError(f"URL file not found: {url_file}")
            
        urls = [line.strip() for line in url_file.read_text().splitlines() if line.strip()]
        return cls(urls=urls, **kwargs)

class NotebookLMSourceUploader(NotebookLMAutomation):
    """Class for automating URL source uploads in NotebookLM.
    
    This class extends the base NotebookLM automation to handle batch uploading
    of URL sources to a specified notebook.
    """
    
    def __init__(self, config: Optional[SourceUploaderConfig] = None):
        """Initialize source uploader.
        
        Args:
            config: Source uploader configuration. If None, default config is used.
        """
        super().__init__(config or SourceUploaderConfig())
        self.config = self.config if isinstance(self.config, SourceUploaderConfig) else SourceUploaderConfig()
    
    def verify_notebook_page(self) -> bool:
        """Verify that we are on a valid NotebookLM notebook page.
        
        Returns:
            bool: True if we are on a valid notebook page, False otherwise.
        """
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
            
        try:
            # Only check for the "Lisää lähde" button
            WebDriverWait(self.driver, self.config.wait_timeout).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Lisää lähde')]"))
            )
            logger.info("Successfully verified NotebookLM notebook page - 'Lisää lähde' button found")
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify notebook page - 'Lisää lähde' button not found: {e}")
            return False

    def try_click_verkkosivusto(self, url_option_xpath: str) -> bool:
        """Try different strategies to click the Verkkosivusto option.
        
        Args:
            url_option_xpath: XPath to the Verkkosivusto element.
            
        Returns:
            bool: True if any strategy succeeded, False otherwise.
        """
        try:
            # First find the element using the provided XPath
            url_option = WebDriverWait(self.driver, self.config.wait_timeout).until(
                EC.presence_of_element_located((By.XPATH, url_option_xpath))
            )
            
            # Strategy 1: Direct mat-chip click
            logger.info("Trying Strategy 1: Direct mat-chip click...")
            try:
                chip_xpath = "//mat-chip[contains(@class, 'mat-mdc-chip') and .//span[contains(text(), 'Verkkosivusto')]]"
                chip = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, chip_xpath))
                )
                chip.click()
                return True
            except Exception as e:
                logger.info(f"Strategy 1 failed: {e}")

            # Strategy 2: Move and click using Actions
            logger.info("Trying Strategy 2: Move and click using Actions...")
            try:
                actions = ActionChains(self.driver)
                actions.move_to_element(url_option).pause(1).click().perform()
                return True
            except Exception as e:
                logger.info(f"Strategy 2 failed: {e}")

            # Strategy 3: Click by coordinates
            logger.info("Trying Strategy 3: Click by coordinates...")
            try:
                location = url_option.location
                size = url_option.size
                x = location['x'] + size['width']//2
                y = location['y'] + size['height']//2
                actions = ActionChains(self.driver)
                actions.move_by_offset(x, y).click().perform()
                return True
            except Exception as e:
                logger.info(f"Strategy 3 failed: {e}")

            # Strategy 4: Multiple JS click methods
            logger.info("Trying Strategy 4: Multiple JS click methods...")
            try:
                self.driver.execute_script("""
                    arguments[0].dispatchEvent(new MouseEvent('click', {
                        'bubbles': true,
                        'cancelable': true
                    }));
                """, url_option)
                return True
            except Exception as e:
                logger.info(f"Strategy 4 failed: {e}")

            # Strategy 5: Double wait condition
            logger.info("Trying Strategy 5: Double wait condition...")
            try:
                element = WebDriverWait(self.driver, 3).until(
                    lambda d: d.find_element(By.XPATH, url_option_xpath) if 
                    EC.presence_of_element_located((By.XPATH, url_option_xpath))(d) and
                    EC.element_to_be_clickable((By.XPATH, url_option_xpath))(d) else False
                )
                element.click()
                return True
            except Exception as e:
                logger.info(f"Strategy 5 failed: {e}")

            # Strategy 6: Click by role and text
            logger.info("Trying Strategy 6: Click by role and text...")
            try:
                option = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    '[role="option"], [role="button"], [role="menuitem"]'
                ).find_element(By.XPATH, ".//*[contains(text(), 'Verkkosivusto')]")
                option.click()
                return True
            except Exception as e:
                logger.info(f"Strategy 6 failed: {e}")

            # Strategy 7: Force visibility and click
            logger.info("Trying Strategy 7: Force visibility and click...")
            try:
                self.driver.execute_script("""
                    arguments[0].style.opacity = '1';
                    arguments[0].style.display = 'block';
                    arguments[0].style.visibility = 'visible';
                """, url_option)
                time.sleep(0.5)
                url_option.click()
                return True
            except Exception as e:
                logger.info(f"Strategy 7 failed: {e}")

            # Strategy 8: Click parent chain
            logger.info("Trying Strategy 8: Click parent chain...")
            try:
                element = url_option
                for _ in range(3):  # Try clicking up to 3 parent levels
                    try:
                        element.click()
                        return True
                    except:
                        element = element.find_element(By.XPATH, "./..")
            except Exception as e:
                logger.info(f"Strategy 8 failed: {e}")

            # Strategy 9: Multiple selectors with overlay check
            logger.info("Trying Strategy 9: Multiple selectors with overlay check...")
            try:
                selectors = [
                    "//mat-chip[.//span[contains(text(), 'Verkkosivusto')]]",
                    "//div[contains(@class, 'mat-chip') and contains(., 'Verkkosivusto')]",
                    "//div[@role='option' and contains(., 'Verkkosivusto')]"
                ]
                for selector in selectors:
                    try:
                        # Wait for any overlays to disappear
                        WebDriverWait(self.driver, 3).until_not(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".cdk-overlay-backdrop"))
                        )
                        element = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        element.click()
                        return True
                    except:
                        continue
            except Exception as e:
                logger.info(f"Strategy 9 failed: {e}")

            # Strategy 10: Scroll and click
            logger.info("Trying Strategy 10: Scroll and click...")
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", url_option)
                time.sleep(0.5)
                self.driver.execute_script("""
                    var evt = new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    arguments[0].dispatchEvent(evt);
                """, url_option)
                return True
            except Exception as e:
                logger.info(f"Strategy 10 failed: {e}")

            logger.error("All click strategies failed")
            return False

        except Exception as e:
            logger.error(f"Error in try_click_verkkosivusto: {e}")
            return False

    def click_at_coordinates(self, x: int, y: int) -> None:
        """Click at specific coordinates on the page.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        actions = ActionChains(self.driver)
        actions.move_by_offset(x, y).click().perform()
        # Reset mouse position
        actions.move_by_offset(-x, -y).perform()

    def upload_url(self, url: str) -> bool:
        """Upload a single URL as a source.
        
        Args:
            url: URL to upload.
            
        Returns:
            bool: True if upload was successful, False otherwise.
        """
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
            
        if url in self.config.processed_urls:
            logger.info(f"URL already processed, skipping: {url}")
            return True
            
        try:
            # Step 1: Find and click "Lisää lähde" button
            logger.info("Looking for 'Lisää lähde' button...")
            add_source_button = WebDriverWait(self.driver, self.config.wait_timeout).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Lisää lähde')]"))
            )
            
            # Wait a moment for any overlays to disappear
            time.sleep(1)
            
            # Try to click using JavaScript if normal click fails
            logger.info("Clicking 'Lisää lähde' button...")
            try:
                add_source_button.click()
            except Exception as e:
                logger.info("Regular click failed, trying JavaScript click...")
                self.driver.execute_script("arguments[0].click();", add_source_button)
            
            # Wait a moment for the dialog to fully appear
            time.sleep(2)
            
            # Step 2: Click the Verkkosivusto option using precise selectors
            logger.info("Looking for 'Verkkosivusto' option...")
            try:
                # Try multiple selector strategies
                selectors = [
                    # Strategy 1: Direct text match with specific class structure
                    "//span[contains(@class, 'mdc-evolution-chip__text-label')]//span[text()='Verkkosivusto']",
                    # Strategy 2: Match by icon and text
                    "//mat-icon[text()='web']/ancestor::span[contains(@class, 'mdc-evolution-chip__action')]",
                    # Strategy 3: Full class path
                    "//span[contains(@class, 'mdc-evolution-chip__action')]//span[contains(@class, 'mdc-evolution-chip__text-label')]//span[text()='Verkkosivusto']"
                ]
                
                option_element = None
                for selector in selectors:
                    try:
                        logger.info(f"Trying selector: {selector}")
                        option_element = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        if option_element:
                            break
                    except Exception:
                        continue
                
                if not option_element:
                    raise Exception("Could not find Verkkosivusto option with any selector")
                
                # Try clicking the element and its parents
                clicked = False
                current_element = option_element
                for _ in range(3):  # Try up to 3 parent levels
                    try:
                        logger.info("Attempting direct click...")
                        current_element.click()
                        clicked = True
                        break
                    except Exception:
                        try:
                            logger.info("Direct click failed, trying JavaScript click...")
                            self.driver.execute_script("""
                                var element = arguments[0];
                                var clickEvent = new MouseEvent('click', {
                                    bubbles: true,
                                    cancelable: true,
                                    view: window
                                });
                                element.dispatchEvent(clickEvent);
                            """, current_element)
                            clicked = True
                            break
                        except Exception:
                            logger.info("JavaScript click failed, trying parent element...")
                            current_element = current_element.find_element(By.XPATH, "./..")
                
                if not clicked:
                    raise Exception("Failed to click element or any of its parents")
                    
                time.sleep(1)
            except Exception as e:
                logger.error(f"Failed to click Verkkosivusto option: {e}")
                return False
            
            # Wait a moment for the URL input to appear
            time.sleep(1)
            
            # Step 3: Enter the URL in the input field using the exact CSS selector
            logger.info("Looking for URL input field...")
            try:
                # Use the exact class structure from the HTML
                url_input = WebDriverWait(self.driver, self.config.wait_timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 
                        "input.mat-mdc-input-element[formcontrolname='newUrl']"))
                )
                logger.info(f"Entering URL: {url}")
                url_input.clear()
                url_input.send_keys(url)
            except Exception as e:
                logger.error(f"Failed to enter URL: {e}")
                return False
            
            # Step 4: Click the "Lisää" button using the exact button selector
            logger.info("Looking for 'Lisää' button...")
            try:
                # Try multiple selector strategies for the button
                button_selectors = [
                    # Strategy 1: Exact button with all classes and attributes
                    "button[type='submit'][mat-flat-button][color='primary'].mdc-button.mdc-button--unelevated.mat-mdc-unelevated-button.mat-primary",
                    # Strategy 2: Button with essential attributes
                    "button[type='submit'][mat-flat-button][color='primary']",
                    # Strategy 3: Button with specific text
                    "button.mat-mdc-unelevated-button:has(span.mdc-button__label:contains('Lisää'))"
                ]
                
                add_button = None
                for selector in button_selectors:
                    try:
                        logger.info(f"Trying button selector: {selector}")
                        add_button = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        if add_button:
                            break
                    except Exception:
                        continue
                
                if not add_button:
                    # Fallback to XPath if CSS selectors fail
                    logger.info("Trying XPath selector as fallback...")
                    add_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, 
                            "//button[@type='submit']//span[contains(@class, 'mdc-button__label') and text()='Lisää']/ancestor::button"))
                    )
                
                if not add_button:
                    raise Exception("Could not find Lisää button with any selector")
                
                # Try multiple click methods
                try:
                    logger.info("Attempting direct click...")
                    add_button.click()
                except Exception:
                    logger.info("Direct click failed, trying JavaScript click...")
                    self.driver.execute_script("""
                        var element = arguments[0];
                        var clickEvent = new MouseEvent('click', {
                            'view': window,
                            'bubbles': true,
                            'cancelable': true
                        });
                        element.dispatchEvent(clickEvent);
                        
                        // If the first click doesn't work, try submitting the form
                        var form = element.closest('form');
                        if (form) {
                            form.submit();
                        }
                    """, add_button)
                
                # Wait a moment to ensure the click is processed
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to click Lisää button: {e}")
                return False
            
            # Wait for upload to complete and dialog to close
            logger.info("Waiting for upload to complete...")
            time.sleep(2)  # Give more time for the upload to complete
            
            # Mark URL as processed
            self.config.processed_urls.add(url)
            logger.info(f"Successfully uploaded URL: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload URL {url}: {e}")
            return False
    
    def upload_urls(self) -> None:
        """Upload all configured URLs as sources.
        
        This method handles batch uploading with retries and progress tracking.
        
        Raises:
            RuntimeError: If upload process fails.
        """
        if not self.config.urls:
            logger.warning("No URLs configured for upload")
            return
            
        try:
            logger.info(f"Starting batch upload of {len(self.config.urls)} URLs")
            
            for i, url in enumerate(self.config.urls, 1):
                logger.info(f"Processing URL {i}/{len(self.config.urls)}: {url}")
                retries = 0
                success = False
                
                while not success and retries < self.config.max_retries:
                    if retries > 0:
                        logger.info(f"Retrying upload of URL (attempt {retries + 1}): {url}")
                        time.sleep(self.config.retry_delay)
                    
                    success = self.upload_url(url)
                    if not success:
                        retries += 1
                
                if not success:
                    logger.error(f"Failed to upload URL after {retries} attempts: {url}")
                
                # Add delay between uploads
                if success and self.config.upload_delay > 0 and i < len(self.config.urls):
                    logger.info(f"Waiting {self.config.upload_delay} seconds before next upload...")
                    time.sleep(self.config.upload_delay)
            
            logger.info(f"Batch upload completed. Successfully processed {len(self.config.processed_urls)} URLs")
            
        except Exception as e:
            logger.error(f"Batch upload process failed: {e}")
            raise RuntimeError(f"Batch upload failed: {e}") from e
    
    def click_muokkaa_button(self) -> bool:
        """Click the 'Muokkaa' button after processing all URLs.
        
        Returns:
            bool: True if button was clicked successfully, False otherwise.
        """
        logger.info("Attempting to click 'Muokkaa' button...")
        try:
            # Try multiple strategies to find and click the button
            button_selectors = [
                "//button[contains(@class, 'customize-button') and .//span[contains(text(), 'Muokkaa')]]",
                "//button[contains(@class, 'call-to-action-button-wide') and .//span[contains(text(), 'Muokkaa')]]",
                "//button[contains(@class, 'mat-mdc-unelevated-button') and .//span[contains(text(), 'Muokkaa')]]"
            ]
            
            for selector in button_selectors:
                try:
                    button = WebDriverWait(self.driver, self.config.wait_timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    # Try multiple click strategies
                    try:
                        # Direct click
                        button.click()
                        logger.info("Successfully clicked 'Muokkaa' button using direct click")
                        return True
                    except:
                        try:
                            # JavaScript click
                            self.driver.execute_script("arguments[0].click();", button)
                            logger.info("Successfully clicked 'Muokkaa' button using JavaScript")
                            return True
                        except:
                            try:
                                # Action chains click
                                ActionChains(self.driver).move_to_element(button).click().perform()
                                logger.info("Successfully clicked 'Muokkaa' button using Action Chains")
                                return True
                            except:
                                continue
                except:
                    continue
            
            logger.warning("Failed to click 'Muokkaa' button with all selectors")
            return False
            
        except Exception as e:
            logger.error(f"Error clicking 'Muokkaa' button: {e}")
            return False

    def input_characterization(self) -> bool:
        """Input characterization for the podcast and create it.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Wait for the textarea to be present and interactable
            logger.info("Waiting for characterization input field...")
            textarea = WebDriverWait(self.driver, self.config.wait_timeout).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    "textarea.episode-focus-input[formcontrolname='episodeFocus']"
                ))
            )
            
            # Prepare the characterization text
            characterization = (
                "Data Engineer's Deep Dive After Dark (18+ only)\n"
                "FOCUS: Practical AI/data eng, dev tools, AI-assisted coding, real-world apps, top comments \n"
                "STYLE: Raw as fuck, unhinged & hilarious. Genius AI hosts who swear freely (esp. 'fuck'/'shit'). "
                "No corporate BS, no censorship, no 'exactly'. Just pure tech talk with attitude. "
                "Minimum podcast lenght 30 minutes, maximum 60 minutes. "
                "WARNING: Explicit content, zero filter. FUCK YEAH!"
            )
            
            # Clear existing text and input new characterization
            textarea.clear()
            textarea.send_keys(characterization)
            
            # Wait a moment for the input to be processed
            time.sleep(1)
            
            # Click the "Luo" button
            logger.info("Clicking 'Luo' button...")
            create_button = WebDriverWait(self.driver, self.config.wait_timeout).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(@class, 'generate-button') and .//span[contains(text(), 'Luo')]]"
                ))
            )
            
            # Try multiple click strategies for the Luo button
            try:
                # Direct click
                create_button.click()
            except:
                try:
                    # JavaScript click
                    self.driver.execute_script("arguments[0].click();", create_button)
                except:
                    # Action chains click
                    ActionChains(self.driver).move_to_element(create_button).click().perform()
            
            logger.info("Waiting for more_vert icon to become available...")
            # Wait for the more_vert icon to appear and be clickable
            more_vert_icon = WebDriverWait(self.driver, 60).until(  # Longer timeout as content generation might take time
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//mat-icon[contains(@class, 'mat-icon') and text()='more_vert']"
                ))
            )
            
            # Click the more_vert icon to open the menu
            logger.info("Clicking more_vert icon...")
            try:
                more_vert_icon.click()
            except:
                self.driver.execute_script("arguments[0].click();", more_vert_icon)
            
            # Wait for the Lataa link to appear in the menu
            logger.info("Waiting for Lataa option...")
            download_link = WebDriverWait(self.driver, self.config.wait_timeout).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//a[contains(@mat-menu-item, '') and .//mat-icon[text()='download']]"
                ))
            )
            
            # Click the Lataa link
            logger.info("Clicking Lataa...")
            try:
                download_link.click()
            except:
                self.driver.execute_script("arguments[0].click();", download_link)
            
            # Wait for 3 minutes
            logger.info("Waiting for 3 minutes...")
            time.sleep(180)  # 3 minutes in seconds
            
            logger.info("Successfully completed podcast creation and download process")
            return True
            
        except Exception as e:
            logger.error(f"Failed to input characterization or create podcast: {e}")
            return False

    def process_urls(self) -> None:
        """Process all configured URLs.
        
        This method handles the main workflow of uploading multiple URLs
        and retrying failed uploads as needed.
        """
        if not self.config.urls:
            logger.warning("No URLs configured for processing")
            return
            
        try:
            # Verify we're on a valid notebook page
            if not self.verify_notebook_page():
                raise RuntimeError("Not on a valid NotebookLM notebook page")
                
            self.upload_urls()
            
            # After all URLs are processed, click the Muokkaa button
            if self.click_muokkaa_button():
                logger.info("Successfully clicked 'Muokkaa' button")
                
                # Input characterization and create podcast
                if self.input_characterization():
                    logger.info("Successfully completed URL processing and podcast creation")
                else:
                    logger.warning("Failed to input characterization or create podcast")
            else:
                logger.warning("Failed to click 'Muokkaa' button")
                
        except Exception as e:
            logger.error(f"Error during URL processing: {e}")
            raise
    
    def cleanup(self) -> None:
        """Clean up resources and optionally keep browser open."""
        if not self.config.keep_browser_open:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception as e:
                    logger.error(f"Failed to cleanup driver: {e}")
                finally:
                    self.driver = None
        else:
            logger.info("Browser window kept open as requested")
            # Don't set driver to None or quit it when keep_browser_open is True 