"""
Local Suppliers Integration
============================
FREE access to local food supplier directories.

Data Sources:
- LocalHarvest (https://www.localharvest.org) - Farms, CSAs, farmers markets
- Colorado Proud (https://www.coloradoproud.org) - Colorado food producers
- MarketMaker (https://foodmarketmaker.com) - Food supplier connections

Note: These use web scraping, so results may vary.
"""

from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
import re
from .base_client import BaseClient, cached


class LocalSuppliersClient(BaseClient):
    """
    Client for local food supplier directories

    FREE web-based directories for finding local/regional suppliers.
    Focused on Colorado/Fort Collins area for The Lariat.
    """

    SUPPLIER_TYPES = [
        'farms', 'csa', 'farmers-market', 'co-op', 'restaurant',
        'bakery', 'dairy', 'meat', 'produce', 'specialty'
    ]

    def __init__(self):
        super().__init__()
        self.local_harvest_url = self.config.LOCAL_HARVEST_BASE_URL
        self.colorado_proud_url = self.config.COLORADO_PROUD_BASE_URL
        self.session.headers.update({
            'User-Agent': 'LariatBible/1.0 (restaurant supplier research)'
        })

    def health_check(self) -> Dict[str, Any]:
        """Check if local supplier directories are accessible"""
        try:
            response = self.session.get(
                f"{self.local_harvest_url}/organic-farms/",
                timeout=10
            )
            available = response.status_code == 200
        except Exception:
            available = False

        return {
            'available': available,
            'source': 'Local Suppliers (LocalHarvest, Colorado Proud)',
            'message': 'Web directories accessible' if available else 'Connection failed'
        }

    @cached(ttl=86400)
    def search(self, query: str, **kwargs) -> List[Dict]:
        """Search all local supplier directories"""
        location = kwargs.get('location', 'Fort Collins, CO')
        results = []

        # Search LocalHarvest
        lh_results = self.search_local_harvest(query, location)
        results.extend(lh_results)

        return results

    @cached(ttl=86400)
    def search_local_harvest(
        self,
        query: str,
        location: str = "Fort Collins, CO",
        radius: int = 50
    ) -> List[Dict]:
        """
        Search LocalHarvest for local farms and suppliers

        Args:
            query: Search term (e.g., 'vegetables', 'beef', 'dairy')
            location: Location to search near
            radius: Search radius in miles

        Returns:
            List of local suppliers
        """
        try:
            # LocalHarvest search URL
            search_url = f"{self.local_harvest_url}/search.jsp"
            params = {
                'jmp': 'search',
                'lat': '',
                'lon': '',
                'scale': radius,
                'ty': '0',  # All types
                'nm': query,
                'zip': location
            }

            response = self.session.get(search_url, params=params, timeout=15)

            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            suppliers = []

            # Parse search results
            listings = soup.find_all('div', class_='listing')

            for listing in listings[:20]:  # Limit to 20 results
                supplier = self._parse_local_harvest_listing(listing)
                if supplier:
                    suppliers.append(supplier)

            return suppliers

        except Exception as e:
            return []

    @cached(ttl=86400)
    def get_farms_near_location(
        self,
        city: str = "Fort Collins",
        state: str = "CO",
        radius: int = 25
    ) -> List[Dict]:
        """
        Get farms near a specific location

        Args:
            city: City name
            state: State abbreviation
            radius: Search radius in miles

        Returns:
            List of nearby farms
        """
        return self.search_local_harvest(
            query="",
            location=f"{city}, {state}",
            radius=radius
        )

    @cached(ttl=86400)
    def get_farmers_markets(
        self,
        city: str = "Fort Collins",
        state: str = "CO"
    ) -> List[Dict]:
        """
        Get farmers markets in an area

        Args:
            city: City name
            state: State abbreviation

        Returns:
            List of farmers markets
        """
        try:
            url = f"{self.local_harvest_url}/farmers-markets/{state.lower()}/{city.lower().replace(' ', '-')}"

            response = self.session.get(url, timeout=15)

            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            markets = []

            listings = soup.find_all('div', class_='listing')

            for listing in listings[:10]:
                market = self._parse_farmers_market(listing)
                if market:
                    markets.append(market)

            return markets

        except Exception:
            return []

    @cached(ttl=86400)
    def search_colorado_producers(self, category: Optional[str] = None) -> List[Dict]:
        """
        Search Colorado Proud producer directory

        Args:
            category: Product category filter

        Returns:
            List of Colorado food producers
        """
        try:
            url = f"{self.colorado_proud_url}/directory"
            if category:
                url += f"?category={category}"

            response = self.session.get(url, timeout=15)

            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            producers = []

            # Parse directory listings
            listings = soup.find_all(['div', 'article'], class_=re.compile(r'producer|listing|member'))

            for listing in listings[:20]:
                producer = self._parse_colorado_producer(listing)
                if producer:
                    producers.append(producer)

            return producers

        except Exception:
            return []

    @cached(ttl=86400)
    def get_supplier_categories(self) -> List[Dict]:
        """
        Get available supplier categories

        Returns:
            List of supplier categories
        """
        return [
            {'id': 'produce', 'name': 'Fresh Produce', 'description': 'Fruits and vegetables'},
            {'id': 'meat', 'name': 'Meat & Poultry', 'description': 'Beef, pork, chicken, lamb'},
            {'id': 'dairy', 'name': 'Dairy', 'description': 'Milk, cheese, butter, eggs'},
            {'id': 'bakery', 'name': 'Bakery', 'description': 'Bread, pastries, baked goods'},
            {'id': 'specialty', 'name': 'Specialty Foods', 'description': 'Artisan and specialty items'},
            {'id': 'herbs', 'name': 'Herbs & Spices', 'description': 'Fresh and dried herbs'},
            {'id': 'honey', 'name': 'Honey & Bee Products', 'description': 'Local honey and bee products'},
            {'id': 'beverages', 'name': 'Beverages', 'description': 'Coffee, tea, juices'},
            {'id': 'organic', 'name': 'Organic', 'description': 'Certified organic products'},
            {'id': 'sustainable', 'name': 'Sustainable', 'description': 'Sustainably produced items'}
        ]

    def get_colorado_suppliers_by_region(self) -> Dict[str, List[Dict]]:
        """
        Get Colorado suppliers organized by region

        Returns:
            Dict of regions with supplier lists
        """
        regions = {
            'front_range': ['Fort Collins', 'Boulder', 'Denver', 'Colorado Springs'],
            'western_slope': ['Grand Junction', 'Durango', 'Montrose'],
            'mountain': ['Aspen', 'Vail', 'Breckenridge'],
            'eastern_plains': ['Greeley', 'Sterling', 'Burlington']
        }

        result = {}
        for region, cities in regions.items():
            suppliers = []
            for city in cities[:2]:  # Limit API calls
                city_suppliers = self.get_farms_near_location(city, 'CO', 15)
                suppliers.extend(city_suppliers)
            result[region] = suppliers[:10]

        return result

    def _parse_local_harvest_listing(self, listing) -> Optional[Dict]:
        """Parse a LocalHarvest listing element"""
        try:
            name_elem = listing.find(['h3', 'h4', 'a'], class_=re.compile(r'name|title'))
            name = name_elem.get_text(strip=True) if name_elem else None

            if not name:
                return None

            location_elem = listing.find(['span', 'div'], class_=re.compile(r'location|address'))
            location = location_elem.get_text(strip=True) if location_elem else None

            desc_elem = listing.find(['p', 'div'], class_=re.compile(r'desc|summary'))
            description = desc_elem.get_text(strip=True)[:200] if desc_elem else None

            link_elem = listing.find('a', href=True)
            url = f"{self.local_harvest_url}{link_elem['href']}" if link_elem else None

            type_elem = listing.find(['span', 'div'], class_=re.compile(r'type|category'))
            supplier_type = type_elem.get_text(strip=True) if type_elem else 'Farm'

            return {
                'name': name,
                'type': supplier_type,
                'location': location,
                'description': description,
                'url': url,
                'source': 'LocalHarvest'
            }

        except Exception:
            return None

    def _parse_farmers_market(self, listing) -> Optional[Dict]:
        """Parse a farmers market listing"""
        try:
            name_elem = listing.find(['h3', 'h4', 'a'])
            name = name_elem.get_text(strip=True) if name_elem else None

            if not name:
                return None

            schedule_elem = listing.find(class_=re.compile(r'schedule|hours|time'))
            schedule = schedule_elem.get_text(strip=True) if schedule_elem else None

            location_elem = listing.find(class_=re.compile(r'location|address'))
            location = location_elem.get_text(strip=True) if location_elem else None

            return {
                'name': name,
                'type': 'Farmers Market',
                'schedule': schedule,
                'location': location,
                'source': 'LocalHarvest'
            }

        except Exception:
            return None

    def _parse_colorado_producer(self, listing) -> Optional[Dict]:
        """Parse a Colorado Proud producer listing"""
        try:
            name_elem = listing.find(['h3', 'h4', 'a'])
            name = name_elem.get_text(strip=True) if name_elem else None

            if not name:
                return None

            category_elem = listing.find(class_=re.compile(r'category|product'))
            category = category_elem.get_text(strip=True) if category_elem else None

            location_elem = listing.find(class_=re.compile(r'location|city'))
            location = location_elem.get_text(strip=True) if location_elem else None

            website_elem = listing.find('a', href=re.compile(r'^https?://'))
            website = website_elem['href'] if website_elem else None

            return {
                'name': name,
                'type': 'Colorado Producer',
                'category': category,
                'location': location,
                'website': website,
                'source': 'Colorado Proud'
            }

        except Exception:
            return None
