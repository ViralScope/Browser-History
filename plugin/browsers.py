import shutil
import sqlite3
from tempfile import gettempdir
import os
from pathlib import Path
from datetime import datetime
import logging

log = logging.getLogger(__name__)

LOCAL_DATA = os.getenv('LOCALAPPDATA')
ROAMING = os.getenv('APPDATA')
CHROME_DIR = Path(LOCAL_DATA, 'Google', 'Chrome', 'User Data', 'Default', 'History')
FIREFOX_DIR = Path(ROAMING, 'Mozilla', 'Firefox', 'Profiles')
EDGE_DIR = Path(LOCAL_DATA, 'Microsoft', 'Edge', 'User Data', 'Default', 'History')
BRAVE_DIR = Path(LOCAL_DATA, 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default', 'History')
OPERA_DIR = Path(ROAMING, 'Opera Software', 'Opera Stable', 'Default', 'History')
VIVALDI_DIR = Path(LOCAL_DATA, 'Vivaldi', 'User Data', 'Default', 'History')
ARC_DIR = Path(LOCAL_DATA, 'Packages', 'TheBrowserCompany.Arc_ttt1ap7aakyb4', 'LocalCache', 'Local', 'Arc', 'User Data', 'Default', 'History')
ZEN_DIR = Path(ROAMING, 'zen', 'Profiles')

def get(browser_name):
    """Get browser instance by name using dictionary dispatch for O(1) lookup"""
    browsers = {
        'chrome': Chrome,
        'firefox': Firefox,
        'edge': Edge,
        'brave': Brave,
        'opera': Opera,
        'vivaldi': Vivaldi,
        'arc': Arc,
        'zen': Zen,
    }
    
    browser_class = browsers.get(browser_name)
    if browser_class is None:
        raise ValueError(
            f"Invalid browser name: '{browser_name}'. "
            f"Valid options: {', '.join(browsers.keys())}"
        )
    return browser_class()

class Base(object):
    
    def __del__(self):
        if hasattr(self, 'temp_path'):
            # Probably best we don't leave browser history in the temp directory
            # This deletes the temporary database file after the object is destroyed
            try:
                os.remove(self.temp_path)
            except (OSError, FileNotFoundError):
                pass  # Silently ignore if file already deleted

    def _copy_database(self, database_path):
        """
        Copies the database to a temporary location and returns the path to the
        copy.
        """
        temp_dir = gettempdir()
        temp_path = shutil.copy(database_path, temp_dir)
        self.temp_path = temp_path
        return temp_path

    def query_history(self, database_path, query, limit=10):
        """
        Query Browser history SQL Database.
        """
        # Copy the database to a temporary location.
        temp_path = self._copy_database(database_path)

        # Open the database.
        connection = sqlite3.connect(temp_path)
        
        try:
            cursor = connection.cursor()
            cursor.execute(f'{query} LIMIT {limit}')
            recent = cursor.fetchall()
            return recent
        finally:
            connection.close()

    def get_history_items(self, results):
        """
        Converts the tuple returned by the query to a HistoryItem object.
        """
        return [HistoryItem(self, *result) for result in results]


class Chrome(Base):
    """Google Chrome History"""

    def __init__(self, database_path=CHROME_DIR):
        self.database_path = database_path

    def history(self, limit=10):
        """
        Returns a list of the most recently visited sites in Chrome's history.
        """
        recents = self.query_history(self.database_path, 'SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC', limit)
        return self.get_history_items(recents)

class Firefox(Base):
    """Firefox Browser History"""

    def __init__(self, database_path=FIREFOX_DIR):
        # Firefox database is not in a static location, so we need to find it
        self.database_path = self.find_database(database_path)

    def find_database(self, path):
        """Find database in path"""
        # Try different profile patterns in order of preference
        patterns = [
            '*.default-release',  # Standard Firefox release profile
            '*Default (release)',  # Zen browser pattern
            '*.default',           # Older Firefox pattern
            '*Default Profile',    # Alternative default pattern
        ]
        
        for pattern in patterns:
            release_folder = next(Path(path).glob(pattern), None)
            if release_folder:
                return Path(path, release_folder, 'places.sqlite')
        
        # If no profile found, raise a more descriptive error
        raise FileNotFoundError(f"No Firefox/Zen profile found in {path}")

    def history(self, limit=10):
        """Most recent Firefox history"""
        recents = self.query_history(self.database_path, 'SELECT url, title, visit_date FROM moz_places INNER JOIN moz_historyvisits on moz_historyvisits.place_id = moz_places.id ORDER BY visit_date DESC', limit)
        return self.get_history_items(recents)

class Edge(Base):
    """Microsoft Edge History"""

    def __init__(self, database_path=EDGE_DIR):
        self.database_path = database_path

    def history(self, limit=10):
        """
        Returns a list of the most recently visited sites in Chrome's history.
        """
        recents = self.query_history(self.database_path, 'SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC', limit)
        return self.get_history_items(recents)

class Brave(Base):
    """Brave Browser History"""

    def __init__(self, database_path=BRAVE_DIR):
        self.database_path = database_path

    def history(self, limit=10):
        """
        Returns a list of the most recently visited sites in Brave's history.
        """
        recents = self.query_history(self.database_path, 'SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC', limit)
        return self.get_history_items(recents)
        
class Opera(Base):
    """Opera Browser History"""

    def __init__(self, database_path=OPERA_DIR):
        self.database_path = database_path

    def history(self, limit=10):
        """
        Returns a list of the most recently visited sites in Opera's history.
        """
        recents = self.query_history(self.database_path, 'SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC', limit)
        return self.get_history_items(recents)

class Vivaldi(Base):
    """Vivaldi Browser History"""

    def __init__(self, database_path=VIVALDI_DIR):
        self.database_path = database_path

    def history(self, limit=10):
        """
        Returns a list of the most recently visited sites in Vivaldi's history.
        """
        recents = self.query_history(self.database_path, 'SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC', limit)
        return self.get_history_items(recents)

class Arc(Base):
    """Arc Browser History"""

    def __init__(self, database_path=ARC_DIR):
        self.database_path = database_path

    def history(self, limit=10):
        """
        Returns a list of the most recently visited sites in Arc's history.
        """
        recents = self.query_history(self.database_path, 'SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC', limit)
        return self.get_history_items(recents)

class Zen(Firefox):
    """Zen Browser History"""

    def __init__(self, database_path=ZEN_DIR):
        super().__init__(database_path)

class HistoryItem(object):
    """Representation of a history item"""

    def __init__(self, browser, url, title, last_visit_time):
        self.browser = browser
        self.url = url
        if not title or not title.strip():
            self.title = url
        else:
            self.title = title
        self.last_visit_time = last_visit_time

    def timestamp(self):
        """Convert browser-specific timestamp to Python datetime"""
        # Chromium-based browsers use WebKit timestamp
        chromium_browsers = (Chrome, Edge, Brave, Opera, Vivaldi, Arc)
        # Firefox-based browsers use Unix timestamp in microseconds
        firefox_browsers = (Firefox, Zen)
        
        if isinstance(self.browser, chromium_browsers):
            return datetime((self.last_visit_time/1000000)-11644473600, 'unixepoch', 'localtime')
        elif isinstance(self.browser, firefox_browsers):
            return datetime.fromtimestamp(self.last_visit_time / 1000000.0)
        else:
            # Fallback for unknown browser types
            log.warning(f"Unknown browser type: {type(self.browser).__name__}")
            return datetime.fromtimestamp(self.last_visit_time / 1000000.0)
