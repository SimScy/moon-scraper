import os
import time
import random
import pandas as pd
import numpy as np
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import lxml


# =====================================================
# CONFIGURATION
# Defines scraping time range, location and output path
# =====================================================


START_DATE = "2026-03-01"
END_DATE = "2026-06-01"

# Geographic coordinates (Munich)
LATITUDE = 48.17
LONGITUDE = 11.50

OUTPUT_DIR = "data/raw"


# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =====================================================
# SELENIUM DRIVER SETUP
# Headless Chrome with minimal resource usage
# =====================================================

options = Options()
options.add_argument("--headless")

# Custom user agent to mimic a normal browser
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
)

# Do not wait for full page load (faster scraping)
options.page_load_strategy = "eager"

# Disable image loading to reduce bandwidth
prefs = {
    "profile.managed_default_content_settings.images": 2
}

options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)

# Some sites require a valid Referer header
# This is the page you manually 'create' data on the website
driver.execute_cdp_cmd(
    "Network.setExtraHTTPHeaders",
    {
        "headers": {
            "Referer": "https://aa.usno.navy.mil/data/AltAz"
        }
    }
)


# =====================================================
# BUILD DATE RANGE FOR REQUESTS
# One request per day
# =====================================================

dates = pd.date_range(
    START_DATE,
    END_DATE,
    freq="D"
).strftime("%Y-%m-%d")


# =====================================================
# URL CONSTRUCTION
# Static base + parameterized date/location
# =====================================================

base_url = "https://aa.usno.navy.mil/calculated/altaz?body=11&date="

# Additional URL parameters for the Alt/Az calculator
# tz and tz_sign specify the local time zone offset (UTC+1 for Munich)
rest_url = (
    f"&intv_mag=1"
    f"&lat={LATITUDE}"
    f"&lon={LONGITUDE}"
    f"&label="
    f"&tz=1.00"
    f"&tz_sign=1"
    f"&submit=Get+Data"
)


urls = [f"{base_url}{d}{rest_url}" for d in dates]


# =====================================================
# MAIN SCRAPING LOOP
# Loads each page, extracts table data, and saves it
# =====================================================

start = time.time()

for url in urls:

    try:

        driver.get(url)

        # Extract date parameter from URL for filename
        parsed = urlparse(url)
        date_str = parse_qs(parsed.query)["date"][0]

        filename = f"datatable_{date_str}.txt"
        output_path = os.path.join(OUTPUT_DIR, filename)

        # Wait until table content appears
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//tbody[1]/tr[2]")
                )
            )
        except:
            print("⚠️ Table not found")

        # Parse HTML using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "lxml")

        tbody = soup.select("tbody")[1]
        trs = tbody.find_all("tr")

        # -------------------------------------------------
        # Extract metadata (table header information)
        # -------------------------------------------------

        th_tag = trs[0].find("th")

        if th_tag:

            # Convert <br> tags to newline characters
            for br in th_tag.find_all("br"):
                br.replace_with("\n")

            meta_line = th_tag.get_text(
                strip=True,
                separator="\n"
            )

        else:

            meta_line = ""

        # -------------------------------------------------
        # Extract column names
        # -------------------------------------------------

        col_names = [
            td.get_text(strip=True)
            for td in trs[1].find_all("td")
        ]

        num_cols = len(col_names)

        # -------------------------------------------------
        # Extract table rows
        # -------------------------------------------------

        data_rows = []

        for tr in trs[2:]:

            cells = [
                td.get_text(strip=True)
                for td in tr.find_all("td")
            ]

            # Pad rows if column count is inconsistent
            padded = cells + [np.nan] * (num_cols - len(cells))

            data_rows.append(padded)

        df = pd.DataFrame(data_rows, columns=col_names)

        # -------------------------------------------------
        # Save result as tab-separated file
        # Metadata is stored in the first line (= 4 lines)
        # -------------------------------------------------

        with open(output_path, "w", encoding="utf-8") as f:

            f.write(meta_line + "\n")

            df.to_csv(
                f,
                sep="\t",
                index=False
            )

        print(f"✔ {filename} saved")

    finally:
        pass

        # optional delay to mimic human browsing behaviour
        #time.sleep(random.uniform(2, 4))


driver.quit()

duration = time.time() - start
print(f"Process took {duration:.2f} seconds")

