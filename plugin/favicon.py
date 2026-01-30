import urllib.request
import urllib.parse
from pathlib import Path
import logging

log = logging.getLogger(__name__)

class FaviconCache:
    """Cache for website favicons"""
    
    def __init__(self, cache_dir=None):
        if cache_dir is None:
            # Use plugin directory for cache
            plugin_dir = Path(__file__).parent.parent
            cache_dir = Path(plugin_dir, 'favicons')
        else:
            cache_dir = Path(cache_dir)
        
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        
    def _get_domain(self, url):
        """Extract domain from URL"""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc or parsed.path.split('/')[0]
            domain = domain.removeprefix('www.')
            return domain
        except (ValueError, AttributeError) as e:
            log.error(f"Error parsing URL {url}: {e}")
            return None
    
    def _sanitize_filename(self, domain):
        """Convert domain to safe filename"""
        # Replace invalid filename characters
        return domain.replace(':', '_').replace('/', '_').replace('\\', '_')
    
    def get_favicon_path(self, url):
        """Get favicon path for URL, downloading if necessary"""
        domain = self._get_domain(url)
        if not domain:
            return None
        
        # Check if favicon is already cached
        safe_domain = self._sanitize_filename(domain)
        favicon_path = Path(self.cache_dir, f"{safe_domain}.png")
        
        if favicon_path.exists():
            return favicon_path.as_posix()
        
        # Try to download favicon
        try:
            # Try Google's favicon service first (most reliable)
            # Using sz=32 for better compatibility
            favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=32"
            
            # Download with timeout
            req = urllib.request.Request(
                favicon_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=2) as response:
                favicon_data = response.read()
                
            # Save to cache
            with open(favicon_path, 'wb') as f:
                f.write(favicon_data)
            
            log.info(f"Downloaded favicon for {domain}")
            return favicon_path.as_posix()
            
        except (urllib.error.URLError, OSError, IOError) as e:
            log.debug(f"Could not download favicon for {domain}: {e!r}")
            return None
    
    def clear_cache(self):
        """Clear all cached favicons"""
        try:
            for file in self.cache_dir.glob('*.png'):
                file.unlink()
            log.info("Favicon cache cleared")
        except (OSError, PermissionError) as e:
            log.error(f"Error clearing favicon cache: {e}")
