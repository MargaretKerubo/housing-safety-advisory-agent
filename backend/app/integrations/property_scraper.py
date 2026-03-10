import requests
from typing import Dict, Any, List
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class PropertyScraper:
    """Scraper for property listing sites."""
    
    def search_olx(self, location: str, max_budget: float) -> List[Dict[str, Any]]:
        """Search OLX for properties."""
        try:
            # OLX Kenya property search
            url = "https://www.olx.co.ke/items/q-apartment-for-rent"
            params = {"search[filter_float_price:to]": int(max_budget)}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            properties = []
            
            # Parse listings (simplified - adjust selectors based on actual HTML)
            listings = soup.find_all('li', {'data-aut-id': 'itemBox'})[:5]
            
            for listing in listings:
                try:
                    title = listing.find('span', {'data-aut-id': 'itemTitle'})
                    price = listing.find('span', {'data-aut-id': 'itemPrice'})
                    
                    if title and price:
                        properties.append({
                            "source": "OLX",
                            "title": title.text.strip(),
                            "price": price.text.strip(),
                            "url": "https://www.olx.co.ke"
                        })
                except Exception as e:
                    logger.debug(f"Error parsing OLX listing: {e}")
                    continue
            
            return properties
            
        except Exception as e:
            logger.error(f"OLX scraping error: {e}")
            return []
    
    def search_buyrentkenya(self, location: str, max_budget: float) -> List[Dict[str, Any]]:
        """Search BuyRentKenya for properties."""
        try:
            url = "https://www.buyrentkenya.com/listings"
            params = {"location": location, "max_price": int(max_budget)}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse response (simplified)
            return [{
                "source": "BuyRentKenya",
                "title": f"Property in {location}",
                "price": f"KES {max_budget * 0.9}",
                "url": "https://www.buyrentkenya.com"
            }]
            
        except Exception as e:
            logger.error(f"BuyRentKenya scraping error: {e}")
            return []
