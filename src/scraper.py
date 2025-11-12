import requests
from bs4 import BeautifulSoup
import time
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import os
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BankOfMaharashtraScraper:
    
    def __init__(self, base_url: str, delay: float = 1.5, max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.delay = delay
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Loan product URLs to scrape (44 URLs total - All verified from sitemap)
        self.loan_urls = [
            # Home/Housing Loans (7 URLs)
            '/personal-banking/loans/home-loan',
            '/maha-super-housing-loan-scheme-for-construction-acquiring',
            '/maha-super-flexi-housing-loan-scheme',
            '/maha-super-housing-loan-scheme-for-purchase-plot-construction-thereon',
            '/maha-super-housing-loan-scheme-for-repairs',
            '/maha-super-green-housing-loan-scheme-green-building',
            '/topup-home-loan',
            
            # Vehicle Loans (8 URLs)
            '/personal-banking/loans/car-loan',
            '/mahabank-vehicle-loan-scheme-for-two-wheelers-loans',
            '/mahabank-vehicle-loan-scheme-for-second-hand-car',
            '/maha-super-car-loan-scheme',
            '/maha-super-green-car-loan-scheme-electric-car',
            '/farmer-vehicle-loan-for-two-three-wheelers',
            '/four-wheelers-farmer-vehicle-loan',
            '/vehicle-loan-for-small-road-transport-operator',
            
            # Personal Loans (6 URLs)
            '/personal-banking/loans/personal-loan',
            '/personal-loan-for-salaried-customers',
            '/personal-loan-for-professionals',
            '/personal-loan-for-businessclass-having-home-loan-with-us',
            '/salary-gain-scheme',
            '/loan-against-property',
            '/maha-lap-mortgage-loan',
            
            # Education Loans (3 URLs)
            '/educational-loans',
            '/model-education-loan-scheme',
            '/maha-bank-skill-loan-scheme',
            
            # Gold Loans (3 URLs)
            '/gold-loan',
            '/agri-gold-loan',
            '/msme-gold-loan',
            
            # Other Personal Loans (3 URLs)
            '/lad',  # Loan Against Deposit
            '/maha-adhaar-loan',
            '/mahabank-rooftop-solar-panel-loan',
            
            # Professional Loans (2 URLs)
            '/mahabank-loan-scheme-for-doctors',
            '/mahabank-professional-loan-scheme-mpls',
            
            # Interest Rates (2 URLs)
            '/advances',
            '/retail-interest-rates',
            
            # MSME Loans (9 URLs)
            '/mahabank-gst-credit-scheme',
            '/hotel-and-restaurant-loan',
            '/mahabank-scheme-for-contractors',
            '/pradhan-mantri-mudra-yojana',
            '/stand-up-india',
            '/maha-msme-project-loan-scheme',
            '/ms-loan-tap-credit-products',
            '/msme-schematic-loans',
            '/collateral-free-term-loan-facility',
            
            # Agriculture Loans (8 URLs)
            '/kisan-credit-card',
            '/kisan-all-purpose-term-loan',
            '/solar-based-pumpset-loans',
            '/loan-for-plantation-horticulture',
            '/farmers-loan-for-purchase-of-land',
            '/estate-purchase-loans',
            '/loan-against-warehouse-receipts-to-farmers',
            
            # COVID-19 Related Loans (2 URLs)
            '/loan-for-covid-affected-sectors',
            '/loan-for-covid-affected-tourism-service',
        ]
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching: {url} (Attempt {attempt + 1}/{self.max_retries})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                time.sleep(self.delay)  # Rate limiting
                return response
            except requests.RequestException as e:
                logger.warning(f"Request failed: {e}")
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    return None
    
    def scrape_page(self, url: str) -> Dict:
        full_url = urljoin(self.base_url, url)
        response = self._make_request(full_url)
        
        if not response:
            return {
                'url': full_url,
                'scraped_at': datetime.now().isoformat(),
                'success': False,
                'error': 'Failed to fetch page'
            }
        
        try:
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract loan type from URL
            loan_type = self._extract_loan_type(url)
            
            # Extract page title
            title = soup.find('h1')
            loan_name = title.get_text(strip=True) if title else 'Unknown Loan'
            
            # Extract all text content from main content area
            main_content = soup.find('div', class_='dvMainBodyCLS') or soup.find('main') or soup.body
            
            if main_content:
                # Remove script and style elements
                for script in main_content(['script', 'style', 'nav', 'footer', 'header']):
                    script.decompose()
                
                # Get text content
                text_content = main_content.get_text(separator='\n', strip=True)
            else:
                text_content = soup.get_text(separator='\n', strip=True)
            
            # Extract specific information
            loan_data = {
                'url': full_url,
                'scraped_at': datetime.now().isoformat(),
                'success': True,
                'loan_type': loan_type,
                'loan_name': loan_name,
                'content': text_content,
                'raw_html': str(soup)
            }
            
            logger.info(f"Successfully scraped: {loan_name}")
            return loan_data
            
        except Exception as e:
            logger.error(f"Error parsing page {full_url}: {e}")
            return {
                'url': full_url,
                'scraped_at': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }
    
    def _extract_loan_type(self, url: str) -> str:
        url_lower = url.lower()
        
        # Interest Rates
        if 'retail-interest' in url_lower:
            return 'Retail Interest Rates'
        elif 'advance' in url_lower:
            return 'Interest Rates'
        
        # Home/Housing Loans
        elif 'home' in url_lower or 'housing' in url_lower or 'awas' in url_lower or 'topup' in url_lower or 'green-building' in url_lower:
            return 'Home Loan'
        
        # Vehicle Loans
        elif 'car' in url_lower or 'vehicle' in url_lower or 'wheeler' in url_lower or 'transport' in url_lower:
            return 'Vehicle Loan'
        
        # Professional Loans
        elif 'doctor' in url_lower or 'professional' in url_lower or 'mpls' in url_lower:
            return 'Professional Loan'
        
        # Personal Loans
        elif 'personal' in url_lower or 'salary' in url_lower or 'lap' in url_lower or 'mortgage' in url_lower:
            return 'Personal Loan'
        
        # Education Loans
        elif 'education' in url_lower or 'scholar' in url_lower or 'skill' in url_lower:
            return 'Education Loan'
        
        # Gold Loans
        elif 'gold' in url_lower:
            return 'Gold Loan'
        
        # Solar/Green Loans
        elif 'solar' in url_lower or 'rooftop' in url_lower:
            return 'Solar Loan'
        
        # Other Loans
        elif 'lad' in url_lower:
            return 'Loan Against Deposit'
        elif 'adhaar' in url_lower:
            return 'Adhaar Loan'
        elif 'covid' in url_lower:
            return 'COVID-19 Loan'
        
        # MSME Loans
        elif 'msme' in url_lower or 'gst' in url_lower or 'hotel' in url_lower or 'contractor' in url_lower or 'mudra' in url_lower or 'stand-up' in url_lower or 'collateral-free' in url_lower:
            return 'MSME Loan'
        
        # Agriculture Loans
        elif 'kisan' in url_lower or 'agri' in url_lower or 'farm' in url_lower or 'plantation' in url_lower or 'estate' in url_lower or 'warehouse' in url_lower or 'pumpset' in url_lower:
            return 'Agriculture Loan'
        
        else:
            return 'Other Loan'
    
    def scrape_loan_products(self) -> List[Dict]:
        logger.info(f"Starting to scrape {len(self.loan_urls)} loan pages...")
        all_data = []
        
        for url in self.loan_urls:
            loan_data = self.scrape_page(url)
            all_data.append(loan_data)
            
        successful = sum(1 for d in all_data if d.get('success', False))
        logger.info(f"Scraping complete: {successful}/{len(self.loan_urls)} pages successful")
        
        return all_data
    
    def save_raw_data(self, data: List[Dict], filepath: str):
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Raw data saved to: {filepath}")
        except Exception as e:
            logger.error(f"Error saving data to {filepath}: {e}")
            raise


def main():
    from dotenv import load_dotenv
    load_dotenv()
    
    base_url = os.getenv('BASE_URL', 'https://bankofmaharashtra.bank.in')
    delay = float(os.getenv('REQUEST_DELAY', 1.5))
    max_retries = int(os.getenv('MAX_RETRIES', 3))
    
    scraper = BankOfMaharashtraScraper(base_url, delay, max_retries)
    data = scraper.scrape_loan_products()
    scraper.save_raw_data(data, 'data/raw/scraped_data.json')
    
    print(f"\n✅ Scraping complete!")
    print(f"📊 Total pages scraped: {len(data)}")
    print(f"✓ Successful: {sum(1 for d in data if d.get('success', False))}")
    print(f"✗ Failed: {sum(1 for d in data if not d.get('success', False))}")


if __name__ == '__main__':
    main()
