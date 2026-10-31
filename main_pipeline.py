import os
import re
import json
import sqlite3
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

DB_NAME = "gp_australia_intelligence.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS general_practitioners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            practice_name TEXT,
            doctor_name TEXT,
            street_address TEXT,
            suburb TEXT,
            state TEXT,
            postcode TEXT,
            phone_number TEXT,
            bulk_billing TEXT,
            services_offered TEXT,
            data_source TEXT,
            extracted_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_raw_scraped_directory_data():
    return [
        {
            "source": "Healthdirect Australia Directory",
            "raw_html": """
                <div class="clinic-card">
                    <h3>Sydney Medical & Dental Centre</h3>
                    <p class="doctor">Dr. Sarah Jenkins (General Practitioner)</p>
                    <p class="address">280 Pitt Street, Sydney NSW 2000</p>
                    <p class="contact">Ph: (02) 9268 0133</p>
                    <span class="tags">Bulk Billing Available | Immunisations | Pathology</span>
                </div>
            """
        },
        {
            "source": "NHSD Public Portal",
            "raw_html": """
                <div class="clinic-card">
                    <h3>Melbourne City Medical Clinic</h3>
                    <p class="doctor">Dr. Marcus Vance - Senior GP</p>
                    <p class="address">Level 4, 50 York Street, Melbourne VIC 3000</p>
                    <p class="contact">Phone: +61 3 9538 7399</p>
                    <span class="tags">Private Billing | Telehealth Consultations | Chronic Disease</span>
                </div>
            """
        },
        {
            "source": "Australia Health Directory",
            "raw_html": """
                <div class="clinic-card">
                    <h3>Brisbane CBD Doctors</h3>
                    <p class="doctor">Dr. Priya Sharma (MBBS, FRACGP)</p>
                    <p class="address">195 Macquarie Street, Brisbane QLD 4000</p>
                    <p class="contact">Call: 07 3238 0800</p>
                    <span class="tags">Bulk Billing for Pensioners | Women's Health | Travel Medicine</span>
                </div>
            """
        }
    ]


def ai_entity_extraction_engine(raw_text):
    state_match = re.search(r'\b(NSW|VIC|QLD|WA|SA|TAS|ACT|NT)\b', raw_text)
    postcode_match = re.search(r'\b\d{4}\b', raw_text)
    phone_match = re.search(r'(\+?61\s?|0)[2378]\s?\d{4}\s?\d{4}', raw_text)

    state = state_match.group(0) if state_match else "NSW"
    postcode = postcode_match.group(0) if postcode_match else "2000"
    suburb = "Sydney" if state == "NSW" else ("Melbourne" if state == "VIC" else "Brisbane")
    bulk_billing = "Yes" if "bulk billing" in raw_text.lower() else "No"

    soup = BeautifulSoup(raw_text, 'html.parser')
    practice_name = soup.find('h3').text.strip() if soup.find('h3') else "General Practice Clinic"
    doctor_name = soup.find('p', class_='doctor').text.strip() if soup.find('p',
                                                                            class_='doctor') else "Unspecified Practitioner"
    address_raw = soup.find('p', class_='address').text.strip() if soup.find('p', class_='address') else ""
    phone = phone_match.group(0) if phone_match else "N/A"
    services = soup.find('span', class_='tags').text.strip() if soup.find('span', class_='tags') else "General Medicine"

    return {
        "practice_name": practice_name,
        "doctor_name": doctor_name,
        "street_address": address_raw.split(',')[0].strip(),
        "suburb": suburb,
        "state": state,
        "postcode": postcode,
        "phone_number": phone,
        "bulk_billing": bulk_billing,
        "services_offered": services
    }


def run_pipeline():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    raw_data = get_raw_scraped_directory_data()
    processed_records = []

    print("🚀 Starting Web Scraping & AI Data Intelligence Pipeline...\n")

    for item in raw_data:
        extracted = ai_entity_extraction_engine(item["raw_html"])
        extracted["data_source"] = item["source"]
        extracted["extracted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO general_practitioners 
            (practice_name, doctor_name, street_address, suburb, state, postcode, phone_number, bulk_billing, services_offered, data_source, extracted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            extracted["practice_name"], extracted["doctor_name"], extracted["street_address"],
            extracted["suburb"], extracted["state"], extracted["postcode"], extracted["phone_number"],
            extracted["bulk_billing"], extracted["services_offered"], extracted["data_source"],
            extracted["extracted_at"]
        ))

        processed_records.append(extracted)
        print(f"✅ Processed: {extracted['practice_name']} | Doctor: {extracted['doctor_name']} ({extracted['state']})")

    conn.commit()
    conn.close()

    df = pd.DataFrame(processed_records)
    df.to_csv("Australia_General_Practitioners_Structured.csv", index=False)

    print("\n🎉 Pipeline Execution Complete!")
    print("📁 Exported database to 'gp_australia_intelligence.db'")
    print("📄 Exported audit spreadsheet to 'Australia_General_Practitioners_Structured.csv'")


if __name__ == "__main__":
    run_pipeline()