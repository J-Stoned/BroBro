"""
BroBro - Niche Snapshot Generator
Generates snapshot documentation for 150+ industry niches
"""

import json
from pathlib import Path
from datetime import datetime
import hashlib

def generate_niche_snapshots():
    """Generate snapshot documentation for all known niches"""

    # Comprehensive list of niches from research
    niches = {
        "Home Services": [
            "Pressure Washing", "House Cleaning", "Carpet Cleaning", "Window Cleaning",
            "Construction", "Electrician", "Plumber", "HVAC", "Roofing", "Landscaping",
            "Pest Control", "Garage Door Repair", "Locksmiths", "Moving Companies",
            "Restoration", "Tree Service", "Junk Removal", "Pool Service",
            "Outdoor Lighting", "Kitchen Remodel", "Home Mover", "Handyman",
            "Painting", "Flooring", "Deck Building", "Fencing", "Gutter Cleaning"
        ],

        "Healthcare & Medical": [
            "Dental Practice", "Orthodontist", "Dentist", "Dental Implants",
            "Chiropractor", "Physical Therapy", "Med Spa", "Massage Therapy",
            "Acupuncture", "Veterinarian", "Pharmacy", "Dermatology",
            "Ophthalmology", "Lasik", "Sports Medicine", "Functional Medicine",
            "IV Therapy", "Float Spa", "Ketamine Clinics", "Drug Rehab",
            "Counselor & Therapist", "Mental Health", "Nursing Homes",
            "Home Care", "Plastic Surgery", "Cosmetic Surgery", "Weight Loss Clinic"
        ],

        "Fitness & Wellness": [
            "Gyms", "Fitness Studio", "Martial Arts", "Yoga Studio",
            "Personal Training", "Crossfit", "Pilates", "Dance Studio",
            "Boxing Gym", "MMA Gym", "Nutrition Coaching", "Life Coach"
        ],

        "Beauty & Personal Care": [
            "Hair Salon", "Barber Shop", "Nail Salon", "Spa",
            "Microblading", "Eyelash Extensions", "Tanning Salon",
            "Mobile Spray Tanning", "Tattoo Parlor", "Makeup Artist"
        ],

        "Real Estate": [
            "Real Estate Agent", "Real Estate Broker", "Real Estate Wholesale",
            "Property Management", "Real Estate Investor", "Home Staging",
            "Real Estate Photography", "Mortgage Broker", "Title Company"
        ],

        "Legal Services": [
            "Personal Injury Attorney", "Family Law", "Divorce Attorney",
            "Estate Planning", "Immigration Law", "Real Estate Law",
            "Bankruptcy Attorney", "Tax Attorney", "Business Law",
            "Intellectual Property", "Malpractice Attorney", "Civil Litigation",
            "Criminal Defense", "DUI Attorney"
        ],

        "Financial Services": [
            "Financial Advisor", "Insurance Agent", "Life Insurance",
            "Health Insurance", "Auto Insurance", "Home Insurance",
            "Dental & Vision Insurance", "Medicare", "Tax Preparation",
            "Accounting", "Bookkeeping", "Credit Repair", "Debt Consolidation"
        ],

        "Automotive": [
            "Auto Repair", "Car Dealership", "Car Wash", "Auto Detailing",
            "Mobile Mechanic", "Tire Shop", "Transmission Repair",
            "Body Shop", "Oil Change", "Towing Service", "RV Repair"
        ],

        "Food & Beverage": [
            "Restaurant", "Cafe", "Food Truck", "Catering",
            "Bakery", "Bar", "Coffee Shop", "Pizza Shop",
            "Meal Prep Service", "Personal Chef"
        ],

        "Professional Services": [
            "Marketing Agency", "Digital Marketing", "SEO Agency",
            "Web Design", "Graphic Design", "Photography",
            "Videography", "Event Planning", "Wedding Planner",
            "Consulting", "Business Coaching", "IT Services",
            "Computer Repair", "Printing Services"
        ],

        "E-commerce & Retail": [
            "E-commerce Store", "Retail Store", "Boutique",
            "Furniture Store", "Mattress Store", "Glasses/Eyewear",
            "Jewelry Store", "Pet Store", "Gift Shop"
        ],

        "Education & Childcare": [
            "Tutoring", "Day Care", "PreSchool", "Private School",
            "College", "Vocational School", "Music Lessons",
            "Language School", "Test Prep", "Child Development",
            "Online Courses"
        ],

        "Industrial & B2B": [
            "Manufacturing", "Logistics & Supply Chain", "Trucking",
            "Courier Service", "Delivery Service", "Pharmaceutical",
            "Medical Supplies", "Solar", "Commercial Cleaning",
            "Exercise Equipment", "Security Services"
        ],

        "Hospitality & Travel": [
            "Hotel", "Bed & Breakfast", "Vacation Rental",
            "Travel Agency", "Tour Operator", "Event Venue"
        ],

        "Specialty Services": [
            "Funeral Home", "Pet Grooming", "Dog Training",
            "Kennel", "Notary Services", "Translation Services",
            "Private Investigation"
        ]
    }

    snapshots = []

    for category, industries in niches.items():
        for industry in industries:
            snapshot_id = hashlib.md5(f"{industry}_{category}".encode()).hexdigest()[:12]

            snapshot = {
                "snapshot_name": f"{industry} Complete Automation System",
                "snapshot_id": snapshot_id,
                "industry": f"{industry} / {category}",
                "use_case": f"Complete business automation for {industry.lower()} businesses including lead generation, appointment booking, and customer retention",
                "target_audience": f"{industry} business owners, {category.lower()} professionals",
                "pricing_model": "Varies by provider",
                "version": "1.0.0",
                "last_updated": datetime.now().strftime('%Y-%m-%d'),
                "author": "Multiple Providers",
                "description": {
                    "overview": f"Industry-specific automation system designed for {industry.lower()} businesses. Includes lead capture funnels, automated follow-up sequences, appointment booking, customer communication workflows, and review generation. Built on proven best practices for the {industry.lower()} industry.",
                    "key_benefits": [
                        "Automated lead capture and nurturing",
                        f"Industry-specific funnels for {industry.lower()} services",
                        "Appointment scheduling and reminders",
                        "Multi-channel follow-up (Email, SMS, Voicemail)",
                        "Review generation automation",
                        "Customer retention workflows",
                        "Pipeline for tracking leads to customers"
                    ],
                    "ideal_for": [
                        f"{industry} businesses wanting to automate operations",
                        f"New {industry.lower()} businesses needing a complete system",
                        f"Established {category.lower()} companies looking to scale",
                        "Agencies serving this niche"
                    ]
                },
                "components": {
                    "funnels": [
                        {
                            "name": f"{industry} Lead Capture Funnel",
                            "purpose": "Convert website visitors into leads"
                        },
                        {
                            "name": f"{industry} Quote Request Funnel",
                            "purpose": "Collect quote requests and service details"
                        }
                    ],
                    "workflows": [
                        {
                            "name": "New Lead Welcome Sequence",
                            "trigger": "New lead submission",
                            "purpose": "Engage leads immediately with multi-channel outreach"
                        },
                        {
                            "name": "Appointment Reminder Automation",
                            "trigger": "Appointment booked",
                            "purpose": "Reduce no-shows with automated reminders"
                        },
                        {
                            "name": "Review Request Automation",
                            "trigger": "Service completed",
                            "purpose": "Generate positive reviews automatically"
                        }
                    ],
                    "calendars": [
                        {
                            "name": f"{industry} Booking Calendar",
                            "type": "Service Booking",
                            "purpose": "Schedule appointments and consultations"
                        }
                    ],
                    "pipelines": [
                        {
                            "name": f"{industry} Sales Pipeline",
                            "stages": ["New Lead", "Contacted", "Quote Sent", "Booked", "Completed"],
                            "purpose": "Track leads through entire customer journey"
                        }
                    ]
                },
                "tags": [
                    industry.lower().replace(" ", "-"),
                    category.lower().replace(" & ", "-").replace(" ", "-"),
                    "lead-generation",
                    "appointments",
                    "automation"
                ],
                "source_type": "niche_generated",
                "available_providers": ["GHL Automations", "Streamline Results", "Top GHL Snapshots"]
            }

            snapshots.append(snapshot)

    return snapshots


def main():
    print("\n" + "="*70)
    print("BroBro - Niche Snapshot Generator")
    print("="*70)

    print("\n>> Generating niche-specific snapshots...")
    snapshots = generate_niche_snapshots()

    print(f"   [OK] Generated {len(snapshots)} snapshots")

    # Create output directory
    output_dir = Path('data/snapshots/niche-library')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save all snapshots
    print(f"\n>> Saving snapshots to {output_dir}...")

    for snapshot in snapshots:
        filename = f"{snapshot['snapshot_id']}.json"
        filepath = output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)

    print(f"   [OK] Saved {len(snapshots)} snapshot files")

    # Create summary
    print(f"\n>> Creating category summary...")

    categories = {}
    for snapshot in snapshots:
        industry = snapshot['industry']
        category = industry.split(' / ')[1] if ' / ' in industry else 'Other'
        if category not in categories:
            categories[category] = []
        categories[category].append(snapshot['snapshot_name'])

    print(f"\n{'='*70}")
    print("SNAPSHOT LIBRARY BY CATEGORY")
    print(f"{'='*70}")

    for category, snaps in sorted(categories.items()):
        print(f"\n{category}: {len(snaps)} snapshots")

    print(f"\n{'='*70}")
    print(f"TOTAL: {len(snapshots)} snapshots generated")
    print(f"{'='*70}")
    print(f"\nNext step: python scripts/embed-snapshots.py data/snapshots/niche-library/")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
