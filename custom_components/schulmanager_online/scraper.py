
"""Web scraper for Schulmanager Online."""
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .const import HOMEWORK_URL, LOGIN_URL, SCHEDULES_URL

_LOGGER = logging.getLogger(__name__)


class SchulmanagerOnlineScraperError(Exception):
    """Exception to indicate a general scraper error."""


class SchulmanagerOnlineScraperAuthError(Exception):
    """Exception to indicate an authentication error."""


class SchulmanagerOnlineScraper:
    """Web scraper for Schulmanager Online."""

    def __init__(self, username: str, password: str) -> None:
        """Initialize the scraper."""
        self._username = username
        self._password = password
        self._driver = None

    def _init_driver(self) -> webdriver.Chrome:
        """Initialize the Chrome WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    async def _login(self, driver: webdriver.Chrome) -> bool:
        """Login to Schulmanager Online."""
        _LOGGER.debug("Attempting to log in to Schulmanager Online.")
        try:
            driver.get(LOGIN_URL)
            _LOGGER.debug(f"Navigated to {LOGIN_URL}")
            
            # Wait for login form
            wait = WebDriverWait(driver, 20) # Increased timeout
            
            # Check if already logged in
            try:
                wait.until(EC.presence_of_element_located((By.ID, "accountDropdown")))
                _LOGGER.info("Already logged in.")
                return True
            except:
                _LOGGER.debug("Not already logged in, proceeding with login.")
                pass
            
            # Find and fill login form
            username_field = wait.until(
                EC.presence_of_element_located((By.ID, "emailOrUsername"))
            )
            password_field = driver.find_element(By.ID, "password")
            login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Einloggen')]") # More robust button finding
            
            _LOGGER.debug("Found username, password fields and login button.")
            username_field.send_keys(self._username)
            password_field.send_keys(self._password)
            login_button.click() # Click the button instead of pressing RETURN
            _LOGGER.debug("Entered credentials and clicked login button.")
            
            # Wait for successful login or error message
            try:
                wait.until(EC.presence_of_element_located((By.ID, "accountDropdown")))
                _LOGGER.info("Login successful.")
                return True
            except Exception as e:
                _LOGGER.debug(f"Login failed to find accountDropdown: {e}")
                # Check for invalid credentials message
                try:
                    error_message = driver.find_element(By.CLASS_NAME, "alert-danger").text
                    _LOGGER.error(f"Login failed with error message: {error_message}")
                    raise SchulmanagerOnlineScraperAuthError(f"Login failed: {error_message}")
                except:
                    _LOGGER.error("Login failed: No specific error message found on page.")
                    raise SchulmanagerOnlineScraperAuthError("Login failed: Unknown reason, possibly invalid credentials or page change.")
            
        except Exception as err:
            _LOGGER.error("Login process encountered an unexpected error: %s", err)
            raise SchulmanagerOnlineScraperAuthError(f"Login process failed: {err}") from err

    async def _scrape_homework(self, driver: webdriver.Chrome) -> List[Dict[str, Any]]:
        """Scrape homework data."""
        _LOGGER.debug("Attempting to scrape homework.")
        try:
            driver.get(HOMEWORK_URL)
            
            # Wait for homework page to load
            wait = WebDriverWait(driver, 15)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".tile")))
            
            if "Hausaufgaben" not in driver.page_source:
                _LOGGER.debug("Hausaufgaben not found on first attempt, waiting 7 seconds.")
                await asyncio.sleep(7)
                if "Hausaufgaben" not in driver.page_source:
                    _LOGGER.warning("Hausaufgaben still not found after retry. Returning empty list.")
                    return []
            
            html = driver.page_source
            blocks = html.split("tile\">")
            blocks.pop(0)
            
            if not blocks:
                _LOGGER.info("No homework blocks found.")
                return []
            
            homework_list = []
            for block in blocks:
                homework_item = self._parse_homework_block(block)
                if homework_item:
                    homework_list.extend(homework_item)
            
            _LOGGER.debug(f"Scraped {len(homework_list)} homework items.")
            return homework_list
            
        except Exception as err:
            _LOGGER.error("Failed to scrape homework: %s", err)
            return []

    def _parse_homework_block(self, block: str) -> Optional[List[Dict[str, Any]]]:
        """Parse a homework block."""
        try:
            # Extract date
            date_str = block.split(", ", 1)[1].split("\n")[0]
            
            # Extract subjects
            lessons = block.split("<h4 ")
            lessons.pop(0)
            subjects = []
            for lesson in lessons:
                subject = lesson.split(">")[1].split("<")[0]
                subjects.append(subject)
            
            # Extract tasks
            tasks = block.split("<span ")
            tasks.pop(0)
            task_list = []
            for task in tasks:
                task_text = task.split(">")[1].split("<")[0]
                task_list.append(task_text)
            
            # Format date
            day, month, year = date_str.split(".")
            formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # Create homework items
            homework_items = []
            for i, subject in enumerate(subjects):
                if i < len(task_list):
                    homework_items.append({
                        "date": formatted_date,
                        "subject": subject,
                        "task": task_list[i],
                        "description": f"{subject}: {task_list[i]}"
                    })
            
            return homework_items
            
        except Exception as err:
            _LOGGER.error("Failed to parse homework block: %s", err)
            return None

    async def _scrape_exams(self, driver: webdriver.Chrome) -> List[Dict[str, Any]]:
        """Scrape exam data."""
        _LOGGER.debug("Attempting to scrape exams.")
        try:
            # Navigate to dashboard where exams are displayed
            driver.get("https://login.schulmanager-online.de/#/")
            
            html = driver.page_source
            
            if "<table " not in html:
                _LOGGER.info("No exam table found on dashboard. Returning empty list.")
                return []
            
            table_content = html.split("<table ")[1].split("</table>")[0]
            rows = table_content.split("<tr ")
            rows.pop(0)
            
            exams = []
            for row in rows:
                exam = self._parse_exam_row(row)
                if exam:
                    exams.append(exam)
            
            _LOGGER.debug(f"Scraped {len(exams)} exam items.")
            return exams
            
        except Exception as err:
            _LOGGER.error("Failed to scrape exams: %s", err)
            return []

    def _parse_exam_row(self, row: str) -> Optional[Dict[str, Any]]:
        """Parse an exam row."""
        try:
            # Extract subject
            subject = row.split("<strong ")[1].split(">")[1].split("<")[0]
            
            # Extract date
            row_after_subject = row.split(subject)[1]
            date_str = row_after_subject.split("<td ")[1].split(">")[1].split("\n")[1].split("\n")[0].split(", ")[1].split(",")[0]
            
            # Add current year if not present
            current_year = datetime.now().year
            if str(current_year) not in date_str:
                date_str = f"{date_str}{current_year}"
            
            # Extract time
            time_section = row_after_subject.split(date_str)[1]
            begin_time = time_section.split("<br")[1].split(">")[1].split("<")[0].replace(" ", "").replace("\n", "")
            end_time = " - " + time_section.split("- ")[1].split("\n")[0]
            full_time = begin_time + end_time
            
            # Format date
            day, month, year = date_str.split(".")
            formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            return {
                "date": formatted_date,
                "subject": subject,
                "time": full_time,
                "description": f"{full_time} {subject}"
            }
            
        except Exception as err:
            _LOGGER.error("Failed to parse exam row: %s", err)
            return None

    async def _scrape_timetable(self, driver: webdriver.Chrome, start_date: str = "") -> List[List[str]]:
        """Scrape timetable data."""
        _LOGGER.debug("Attempting to scrape timetable.")
        try:
            url = f"{SCHEDULES_URL}/{start_date}"
            driver.get(url)
            
            # Wait for timetable to load
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "class-hour-calendar")))
            
            html = driver.page_source
            table_content = html.split("<table", 1)[1].split("</table>", 1)[0]
            
            rows = table_content.split("<tr>")
            del rows[0]  # Remove header
            del rows[0]  # Remove time row
            
            # Initialize days
            week_schedule = [[] for _ in range(7)]  # Mon-Sun
            
            for row in rows:
                columns = row.split("<td>")
                for i, column in enumerate(columns[1:8]):  # Skip first column (time)
                    lesson_info = self._parse_lesson_cell(column)
                    week_schedule[i].append(lesson_info)
            
            _LOGGER.debug(f"Scraped timetable for {len(week_schedule)} days.")
            return week_schedule
            
        except Exception as err:
            _LOGGER.error("Failed to scrape timetable: %s", err)
            return []

    def _parse_lesson_cell(self, cell: str) -> str:
        """Parse a lesson cell from the timetable."""
        try:
            cell_content = cell.split("</td>", 1)[0]
            
            if "span" not in cell_content:
                return ""
            
            if "lesson-cell cancelled" in cell_content:
                # Cancelled lesson
                lesson = cell_content.split("lesson-cell cancelled\">", 1)[1]
                lesson = lesson.split("timetable-left\">", 1)[1].split("timetable-right", 1)[0]
                lesson = lesson.split("</")[0]
                return f"<del>{lesson}</del>"
            
            elif "<span style=\"color" in cell_content and "Inter" not in cell_content:
                # Changed lesson
                if "red;\">" in cell_content and "green;\">" in cell_content:
                    old = cell_content.split("red;\">")[1].split("<", 1)[0].strip()
                    new = cell_content.split("green;\">")[1].split("<", 1)[0].strip()
                    return f"{old} → {new}"
            
            else:
                # Regular lesson
                try:
                    lesson = cell_content.split("timetable-left\">", 1)[1].split("timetable-right", 1)[0]
                    lesson = lesson.split(">")[2].split("<", 1)[0].replace(" ", "").replace("\n", "")
                    
                    teacher = cell_content.split("timetable-right\">", 1)[1].split("timetable-bottom", 1)[0]
                    teacher = teacher.split(">")[5].split("<")[0].replace(" ", "").replace("\n", "")
                    
                    room = cell_content.split("timetable-bottom\">", 1)[1]
                    room = room.split(">")[3].split("<")[0].replace(" ", "").replace("\n", "")
                    
                    return f"{lesson} {teacher} {room}".strip()
                except:
                    _LOGGER.debug("Could not parse regular lesson details.")
                    return ""
            
        except Exception as err:
            _LOGGER.debug("Failed to parse lesson cell: %s", err)
            return ""

    async def scrape_all_data(self) -> Dict[str, Any]:
        """Scrape all available data."""
        driver = None
        try:
            driver = self._init_driver()
            
            # Login
            login_success = await self._login(driver)
            if not login_success:
                raise SchulmanagerOnlineScraperAuthError("Login failed")
            
            # Scrape data
            homework = await self._scrape_homework(driver)
            exams = await self._scrape_exams(driver)
            timetable = await self._scrape_timetable(driver)
            
            return {
                "homework": homework,
                "exams": exams,
                "timetable": timetable,
                "appointments": [],  # Placeholder for future implementation
            }
            
        except Exception as err:
            _LOGGER.error("Scraping failed: %s", err)
            raise SchulmanagerOnlineScraperError(f"Scraping failed: {err}") from err
        
        finally:
            if driver:
                driver.quit()

    async def test_connection(self) -> bool:
        """Test the connection and authentication."""
        driver = None
        try:
            driver = self._init_driver()
            return await self._login(driver)
        except Exception as e:
            _LOGGER.error(f"Test connection failed: {e}")
            return False
        finally:
            if driver:
                driver.quit()



