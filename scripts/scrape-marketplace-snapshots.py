"""
BroBro - Marketplace Snapshot Scraper
Scrapes snapshot information from various GHL marketplaces and converts to our format
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import time
import hashlib

class MarketplaceSnapshotScraper:
    """Scrapes snapshot information from GHL marketplaces"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.output_dir = Path('data/snapshots/marketplace')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def scrape_product_page(self, url: str) -> Optional[Dict]:
        """Scrape a single marketplace product page"""
        try:
            print(f"  >> Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract basic info
            title_elem = soup.select_one('h1, .product-title, .entry-title, h1.title')
            if not title_elem:
                print(f"  [WARN] Could not find title for {url}")
                return None

            title = title_elem.get_text(strip=True)

            # Extract description
            description = ""
            desc_selectors = [
                '.product-description',
                '.entry-content',
                '.description',
                'article',
                '.content'
            ]
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    # Get text, clean up
                    description = desc_elem.get_text(separator='\n', strip=True)
                    break

            # Extract price
            price = None
            price_selectors = [
                '.price',
                '.product-price',
                '[class*="price"]',
                '.cost'
            ]
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = price_text
                    break

            # Extract features/bullets
            features = []
            list_items = soup.select('ul li, .features li, .benefits li')
            for li in list_items[:20]:  # Limit to 20 features
                feature_text = li.get_text(strip=True)
                if len(feature_text) > 10 and len(feature_text) < 200:
                    features.append(feature_text)

            # Try to identify components
            text_lower = description.lower() if description else ""

            components = {
                'has_funnels': 'funnel' in text_lower or 'landing page' in text_lower,
                'has_workflows': 'workflow' in text_lower or 'automation' in text_lower,
                'has_calendars': 'calendar' in text_lower or 'appointment' in text_lower or 'booking' in text_lower,
                'has_forms': 'form' in text_lower or 'survey' in text_lower,
                'has_emails': 'email' in text_lower or 'email template' in text_lower,
                'has_sms': 'sms' in text_lower or 'text message' in text_lower,
                'has_pipelines': 'pipeline' in text_lower or 'stage' in text_lower
            }

            snapshot_data = {
                'name': title,
                'url': url,
                'description': description[:1000] if description else "",  # Limit length
                'price': price,
                'features': features,
                'components_detected': components,
                'scraped_date': datetime.now().isoformat(),
                'source': 'marketplace'
            }

            print(f"  [OK] Scraped: {title}")
            return snapshot_data

        except Exception as e:
            print(f"  [ERROR] Failed to scrape {url}: {e}")
            return None

    def curated_snapshots_list(self) -> List[Dict]:
        """
        Manually curated list of known snapshots from research
        This provides baseline data even if scraping fails
        """
        snapshots = [
            {
                "snapshot_name": "Extendly Ultimate Small Business Snapshot",
                "snapshot_id": "extendly-small-biz",
                "industry": "General / Small Business",
                "use_case": "Complete automation for any small business, compatible with multiple niches",
                "target_audience": "Small business owners across multiple industries",
                "pricing_model": "Paid",
                "version": "1.0.0",
                "last_updated": "2025-01-01",
                "author": "Extendly",
                "description": {
                    "overview": "The Ultimate Small Business Snapshot includes complete automation for ANY small business and is compatible with multiple niches. Designed to be the fastest path to launching a functional business automation system.",
                    "key_benefits": [
                        "Compatible with multiple business niches",
                        "Complete automation workflows included",
                        "Ready-to-use landing pages and funnels",
                        "Pre-built email and SMS sequences"
                    ],
                    "ideal_for": [
                        "New businesses needing quick setup",
                        "Agencies onboarding multiple clients",
                        "Small businesses wanting to automate operations"
                    ]
                },
                "tags": ["small-business", "multi-niche", "automation", "extendly"]
            },
            {
                "snapshot_name": "Extendly Ultimate AI Agency Snapshot",
                "snapshot_id": "extendly-ai-agency",
                "industry": "Agency / AI Services",
                "use_case": "Launch a fully functional AI SaaS offer with complete sales page, demos and pitch materials",
                "target_audience": "Agencies selling AI services, SaaS resellers",
                "pricing_model": "Paid",
                "version": "1.0.0",
                "last_updated": "2025-01-01",
                "author": "Extendly",
                "description": {
                    "overview": "The fastest path to launching a fully functional AI SaaS offer with HighLevel, complete with full sales page, built-in demos and pitch materials. Includes everything needed to sell AI services.",
                    "key_benefits": [
                        "Complete AI service sales materials",
                        "Built-in demo environments",
                        "Pitch decks and presentations included",
                        "Ready-to-sell AI automation funnels"
                    ],
                    "ideal_for": [
                        "Agencies adding AI services",
                        "SaaS providers entering AI market",
                        "Consultants selling AI automation"
                    ]
                },
                "tags": ["ai", "agency", "saas", "automation", "extendly"]
            },
            {
                "snapshot_name": "Top GHL Snapshots - Dental Practice",
                "snapshot_id": "topghl-dental",
                "industry": "Dental / Healthcare",
                "use_case": "Complete dental practice management and patient acquisition system",
                "target_audience": "Dental practices, orthodontists, dental marketing agencies",
                "pricing_model": "One-time ($900)",
                "version": "1.0.0",
                "last_updated": "2025-01-01",
                "author": "Top GHL Snapshots",
                "description": {
                    "overview": "Transform your dental practice with this all-in-one solution. Includes patient acquisition funnels, appointment booking, reminders, 52 weekly nurture campaigns, and complete practice management workflows. HIPAA compliant with dental software integration.",
                    "key_benefits": [
                        "Two complete funnel versions with 10 pages each",
                        "12+ holiday reminder campaigns",
                        "52 weekly nurture emails and text messages",
                        "Appointment booking and no-show reduction workflows",
                        "Review generation and management",
                        "Database reactivation campaigns",
                        "HIPAA compliant",
                        "Lifetime free updates"
                    ],
                    "ideal_for": [
                        "Dental practices wanting to automate patient communication",
                        "New dental offices needing complete marketing system",
                        "Practices looking to reduce no-shows and increase reviews"
                    ]
                },
                "components": {
                    "funnels": [
                        {"name": "Patient Acquisition Funnel (Version 1)", "pages": ["Landing", "About", "Services", "Booking", "Thank You"], "purpose": "Convert website visitors into booked appointments"},
                        {"name": "Patient Acquisition Funnel (Version 2)", "pages": ["Alternative landing design", "Service showcase", "Testimonials", "Booking", "Confirmation"], "purpose": "A/B testing variant for conversion optimization"},
                        {"name": "Review Collection Funnel", "pages": ["Review request", "Platform selection", "Thank you"], "purpose": "Generate 5-star reviews from happy patients"}
                    ],
                    "workflows": [
                        {"name": "Appointment Reminder Sequence", "trigger": "Appointment booked", "purpose": "Reduce no-shows with multi-channel reminders"},
                        {"name": "New Patient Welcome", "trigger": "New patient added to CRM", "purpose": "Onboard new patients and build relationship"},
                        {"name": "Holiday Campaigns (12+)", "trigger": "Seasonal/holiday dates", "purpose": "Stay top-of-mind with seasonal touchpoints"},
                        {"name": "Weekly Nurture Campaign", "trigger": "Weekly schedule (52 campaigns)", "purpose": "Ongoing patient engagement and education"},
                        {"name": "Database Reactivation", "trigger": "Inactive patients", "purpose": "Win back patients who haven't visited recently"}
                    ],
                    "forms": [
                        {"name": "New Patient Registration", "fields": ["Name", "Contact", "Insurance", "Chief Complaint"], "purpose": "Collect patient information"},
                        {"name": "Appointment Request", "fields": ["Preferred date/time", "Reason for visit"], "purpose": "Enable online booking"}
                    ]
                },
                "tags": ["dental", "healthcare", "appointments", "patient-acquisition", "hipaa"]
            },
            {
                "snapshot_name": "GHL Automations - Pressure Washing Snapshot",
                "snapshot_id": "ghlautomations-pressure-washing",
                "industry": "Pressure Washing / Home Services",
                "use_case": "Complete pressure washing business automation from lead to payment",
                "target_audience": "Pressure washing companies, home service contractors",
                "pricing_model": "One-time ($297)",
                "version": "1.0.0",
                "last_updated": "2025-01-01",
                "author": "GHL Automations",
                "description": {
                    "overview": "Streamline your pressure washing operations with this fully-loaded snapshot. Includes lead capture, quote automation, appointment booking, customer communication, and review generation. Save time and achieve growth with proven automation workflows.",
                    "key_benefits": [
                        "Automated lead capture and follow-up",
                        "Instant quote request system",
                        "Appointment scheduling and reminders",
                        "Customer communication workflows",
                        "Review generation automation",
                        "Ready-to-use landing pages",
                        "Mobile-responsive funnels"
                    ],
                    "ideal_for": [
                        "Pressure washing businesses wanting to automate operations",
                        "New contractors needing a complete system",
                        "Established companies looking to scale"
                    ]
                },
                "tags": ["pressure-washing", "home-services", "lead-generation", "appointments", "local-business"]
            },
            {
                "snapshot_name": "Extendly Real Estate Wholesale Snapshot",
                "snapshot_id": "extendly-real-estate-wholesale",
                "industry": "Real Estate / Wholesale",
                "use_case": "Complete real estate wholesaling operation automation",
                "target_audience": "Real estate wholesalers, investors, flippers",
                "pricing_model": "Paid",
                "version": "1.0.0",
                "last_updated": "2025-01-01",
                "author": "Extendly",
                "description": {
                    "overview": "Automate your real estate wholesale business with lead generation, deal management pipelines, investor matching, and transaction workflows. Built specifically for wholesalers to manage deals from acquisition to assignment.",
                    "key_benefits": [
                        "Seller lead generation funnels",
                        "Buyer investor matching system",
                        "Deal management pipelines",
                        "Automated follow-up sequences",
                        "Transaction coordination workflows",
                        "Market analysis tools integration"
                    ],
                    "ideal_for": [
                        "Real estate wholesalers",
                        "Property investors",
                        "Fix-and-flip operations"
                    ]
                },
                "tags": ["real-estate", "wholesale", "investing", "deal-management", "extendly"]
            },
            {
                "snapshot_name": "GHL Star Boys - Dental Implants Snapshot",
                "snapshot_id": "ghlstarboys-dental-implants",
                "industry": "Dental / Implants",
                "use_case": "Specialized dental implant patient acquisition and nurturing",
                "target_audience": "Implant dentists, oral surgeons, dental implant centers",
                "pricing_model": "Paid",
                "version": "1.0.0",
                "last_updated": "2025-01-01",
                "author": "GHL Star Boys",
                "description": {
                    "overview": "Turnkey solution for dental implant practices. Fully integrates with dental practice management software, HIPAA compliant, with specific funnels and workflows for implant consultations, treatment plans, and post-operative care.",
                    "key_benefits": [
                        "Implant consultation booking funnels",
                        "Treatment plan presentation automation",
                        "Pre-operative and post-operative care sequences",
                        "Financing options integration",
                        "HIPAA compliant communications",
                        "Integration with dental software"
                    ],
                    "ideal_for": [
                        "Dental implant specialists",
                        "Oral surgery practices",
                        "Multi-specialty dental groups"
                    ]
                },
                "tags": ["dental", "implants", "healthcare", "hipaa", "high-ticket"]
            }
        ]

        return snapshots

    def convert_to_full_format(self, snapshot_summary: Dict) -> Dict:
        """Convert a summary snapshot to our full documentation format"""

        # Generate ID if not present
        if 'snapshot_id' not in snapshot_summary:
            name = snapshot_summary.get('snapshot_name', snapshot_summary.get('name', 'unnamed'))
            snapshot_summary['snapshot_id'] = hashlib.md5(name.encode()).hexdigest()[:12]

        # Ensure required fields exist with defaults
        full_doc = {
            "snapshot_name": snapshot_summary.get('snapshot_name', snapshot_summary.get('name', 'Unnamed Snapshot')),
            "snapshot_id": snapshot_summary['snapshot_id'],
            "industry": snapshot_summary.get('industry', 'General'),
            "use_case": snapshot_summary.get('use_case', ''),
            "target_audience": snapshot_summary.get('target_audience', 'Business owners'),
            "pricing_model": snapshot_summary.get('pricing_model', 'Unknown'),
            "version": snapshot_summary.get('version', '1.0.0'),
            "last_updated": snapshot_summary.get('last_updated', datetime.now().strftime('%Y-%m-%d')),
            "author": snapshot_summary.get('author', 'Marketplace'),
            "description": snapshot_summary.get('description', {}),
            "components": snapshot_summary.get('components', {}),
            "tags": snapshot_summary.get('tags', []),
            "source_url": snapshot_summary.get('url', ''),
            "scraped_from_marketplace": True
        }

        return full_doc

    def save_snapshots(self, snapshots: List[Dict]):
        """Save snapshots to JSON files"""
        print(f"\n>> Saving {len(snapshots)} snapshots...")

        for snapshot in snapshots:
            # Convert to full format
            full_doc = self.convert_to_full_format(snapshot)

            # Generate filename
            snapshot_id = full_doc['snapshot_id']
            filename = f"{snapshot_id}.json"
            filepath = self.output_dir / filename

            # Save
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(full_doc, f, indent=2, ensure_ascii=False)

            print(f"  [OK] Saved: {filepath.name}")

        print(f"\n[SUCCESS] Saved {len(snapshots)} marketplace snapshots")


def main():
    print("\n" + "="*70)
    print("BroBro - Marketplace Snapshot Scraper")
    print("="*70)

    scraper = MarketplaceSnapshotScraper()

    # Use curated list (can be expanded with actual scraping later)
    print("\n>> Loading curated marketplace snapshots...")
    snapshots = scraper.curated_snapshots_list()

    print(f"   [OK] Loaded {len(snapshots)} snapshots")

    # Save to files
    scraper.save_snapshots(snapshots)

    print(f"\n{'='*70}")
    print(f"[COMPLETE] Marketplace snapshots ready for embedding")
    print(f"   Run: python scripts/embed-snapshots.py data/snapshots/marketplace/")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
