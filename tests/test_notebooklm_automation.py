"""Tests for NotebookLM automation module."""

from typing import TYPE_CHECKING

import pytest
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from reddit_weekly_top.notebooklm.automation import NotebookLMAutomation, NotebookLMConfig

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture

@pytest.fixture
def mock_webdriver(mocker: "MockerFixture") -> WebDriver:
    """Create a mock WebDriver instance.
    
    Args:
        mocker: pytest-mock fixture.
        
    Returns:
        Mock WebDriver instance.
    """
    mock_driver = mocker.Mock(spec=WebDriver)
    mock_driver.find_element.return_value = mocker.Mock(spec=WebElement)
    return mock_driver

@pytest.fixture
def mock_config() -> NotebookLMConfig:
    """Create a test configuration.
    
    Returns:
        Test NotebookLMConfig instance.
    """
    return NotebookLMConfig(
        username="test_user",
        password="test_pass",
        user_profile="/path/to/profile"
    )

@pytest.fixture
def automation(mock_config: NotebookLMConfig, mocker: "MockerFixture") -> NotebookLMAutomation:
    """Create a NotebookLMAutomation instance with mocked dependencies.
    
    Args:
        mock_config: Test configuration fixture.
        mocker: pytest-mock fixture.
        
    Returns:
        NotebookLMAutomation instance.
    """
    mocker.patch("selenium.webdriver.Chrome", autospec=True)
    automation = NotebookLMAutomation(mock_config)
    return automation

def test_init_with_default_config() -> None:
    """Test initialization with default configuration."""
    automation = NotebookLMAutomation()
    assert automation.config is not None
    assert automation.config.base_url == "https://notebooklm.google/"
    assert automation.driver is None

def test_init_with_custom_config(mock_config: NotebookLMConfig) -> None:
    """Test initialization with custom configuration.
    
    Args:
        mock_config: Test configuration fixture.
    """
    automation = NotebookLMAutomation(mock_config)
    assert automation.config == mock_config
    assert automation.driver is None

def test_setup_driver_success(automation: NotebookLMAutomation) -> None:
    """Test successful WebDriver setup.
    
    Args:
        automation: NotebookLMAutomation fixture.
    """
    driver = automation.setup_driver()
    assert driver is not None

def test_setup_driver_failure(automation: NotebookLMAutomation, mocker: "MockerFixture") -> None:
    """Test WebDriver setup failure.
    
    Args:
        automation: NotebookLMAutomation fixture.
        mocker: pytest-mock fixture.
    """
    mocker.patch("selenium.webdriver.Chrome", side_effect=WebDriverException("Failed to start"))
    with pytest.raises(RuntimeError, match="WebDriver setup failed"):
        automation.setup_driver()

def test_navigate_to_landing_page_success(
    automation: NotebookLMAutomation,
    mock_webdriver: WebDriver,
    mocker: "MockerFixture"
) -> None:
    """Test successful navigation to landing page.
    
    Args:
        automation: NotebookLMAutomation fixture.
        mock_webdriver: Mock WebDriver fixture.
        mocker: pytest-mock fixture.
    """
    automation.driver = mock_webdriver
    mock_wait = mocker.patch("selenium.webdriver.support.wait.WebDriverWait")
    mock_wait.return_value.until.return_value = True
    
    automation.navigate_to_landing_page()
    mock_webdriver.get.assert_called_once_with(automation.config.base_url)

def test_navigate_to_landing_page_failure(
    automation: NotebookLMAutomation,
    mock_webdriver: WebDriver,
    mocker: "MockerFixture"
) -> None:
    """Test navigation failure to landing page.
    
    Args:
        automation: NotebookLMAutomation fixture.
        mock_webdriver: Mock WebDriver fixture.
        mocker: pytest-mock fixture.
    """
    automation.driver = mock_webdriver
    mock_wait = mocker.patch("selenium.webdriver.support.wait.WebDriverWait")
    mock_wait.return_value.until.side_effect = TimeoutException()
    
    with pytest.raises(RuntimeError, match="Navigation failed"):
        automation.navigate_to_landing_page()

def test_click_try_notebooklm_success(
    automation: NotebookLMAutomation,
    mock_webdriver: WebDriver,
    mocker: "MockerFixture"
) -> None:
    """Test successful click on Try NotebookLM button.
    
    Args:
        automation: NotebookLMAutomation fixture.
        mock_webdriver: Mock WebDriver fixture.
        mocker: pytest-mock fixture.
    """
    automation.driver = mock_webdriver
    mock_wait = mocker.patch("selenium.webdriver.support.wait.WebDriverWait")
    mock_button = mocker.Mock()
    mock_wait.return_value.until.return_value = mock_button
    
    automation.click_try_notebooklm()
    mock_button.click.assert_called_once()

def test_select_user_account_success(
    automation: NotebookLMAutomation,
    mock_webdriver: WebDriver,
    mocker: "MockerFixture"
) -> None:
    """Test successful user account selection.
    
    Args:
        automation: NotebookLMAutomation fixture.
        mock_webdriver: Mock WebDriver fixture.
        mocker: pytest-mock fixture.
    """
    automation.driver = mock_webdriver
    mock_wait = mocker.patch("selenium.webdriver.support.wait.WebDriverWait")
    mock_account = mocker.Mock()
    mock_wait.return_value.until.return_value = mock_account
    
    automation.select_user_account("test_user")
    mock_account.click.assert_called_once()

def test_enter_password_success(
    automation: NotebookLMAutomation,
    mock_webdriver: WebDriver,
    mocker: "MockerFixture"
) -> None:
    """Test successful password entry.
    
    Args:
        automation: NotebookLMAutomation fixture.
        mock_webdriver: Mock WebDriver fixture.
        mocker: pytest-mock fixture.
    """
    automation.driver = mock_webdriver
    mock_wait = mocker.patch("selenium.webdriver.support.wait.WebDriverWait")
    mock_input = mocker.Mock()
    mock_wait.return_value.until.return_value = mock_input
    mock_webdriver.find_element.return_value = mocker.Mock()
    
    automation.enter_password("test_pass")
    mock_input.send_keys.assert_called_once_with("test_pass")

def test_verify_login_success(
    automation: NotebookLMAutomation,
    mock_webdriver: WebDriver,
    mocker: "MockerFixture"
) -> None:
    """Test successful login verification.
    
    Args:
        automation: NotebookLMAutomation fixture.
        mock_webdriver: Mock WebDriver fixture.
        mocker: pytest-mock fixture.
    """
    automation.driver = mock_webdriver
    mock_wait = mocker.patch("selenium.webdriver.support.wait.WebDriverWait")
    mock_wait.return_value.until.return_value = True
    
    assert automation.verify_login_success() is True

def test_cleanup(
    automation: NotebookLMAutomation,
    mock_webdriver: WebDriver
) -> None:
    """Test cleanup process.
    
    Args:
        automation: NotebookLMAutomation fixture.
        mock_webdriver: Mock WebDriver fixture.
    """
    automation.driver = mock_webdriver
    automation.cleanup()
    mock_webdriver.quit.assert_called_once()
    assert automation.driver is None 