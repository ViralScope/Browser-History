from flox import Flox, ICON_HISTORY, ICON_BROWSER

import browsers
from favicon import FaviconCache

HISTORY_GLYPH = ''
DEFAULT_BROWSER = 'chrome'

class BrowserHistory(Flox):

    def __init__(self):
        super().__init__()
        self.default_browser = self.settings.get('default_browser', DEFAULT_BROWSER)
        self.browser = browsers.get(self.default_browser.lower())
        self.favicon_cache = FaviconCache()

    def _query(self, query):
        try:
            self.query(query)
        except FileNotFoundError:
            self.add_item(
                title='History not found!',
                subtitle='Check your logs for more information.',
            )
        return self._results

    def query(self, query):
        history = self.browser.history(limit=10000)
        query_lower = query.lower()
        for idx, item in enumerate(history):
            if query_lower in item.title.lower() or query_lower in item.url.lower():
                subtitle = f"{idx}. {item.url}"
                
                # Try to get favicon for the website
                favicon_path = self.favicon_cache.get_favicon_path(item.url)
                
                # Use favicon if available, otherwise use default icon and glyph
                if favicon_path:
                    icon, glyph = favicon_path, None
                else:
                    icon, glyph = ICON_HISTORY, HISTORY_GLYPH
                
                self.add_item(
                    title=item.title,
                    subtitle=subtitle,
                    icon=icon,
                    glyph=glyph,
                    method=self.browser_open,
                    parameters=[item.url],
                    context=[item.title, item.url]
                )

    def context_menu(self, data):
        self.add_item(
            title='Open in browser',
            subtitle=data[0],
            icon=ICON_BROWSER,
            method=self.browser_open,
            parameters=[data[1]],
        )

if __name__ == "__main__":
    BrowserHistory()
