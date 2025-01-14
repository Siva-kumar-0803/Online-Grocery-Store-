from bs4 import BeautifulSoup
from selenium import webdriver
import time
import csv
import pandas as pd

# Category links to scrape
category_list = [
    "https://www.bigbasket.com/cl/fruits-vegetables/",
    "https://www.bigbasket.com/cl/bakery-cakes-dairy/",
    "https://www.bigbasket.com/cl/eggs-meat-fish/",
    "https://www.bigbasket.com/cl/foodgrains-oil-masala/",
    "https://www.bigbasket.com/cl/snacks-branded-foods/",
    "https://www.bigbasket.com/cl/beauty-hygiene/",
    "https://www.bigbasket.com/cl/cleaning-household/",
    "https://www.bigbasket.com/cl/baby-care/",
    "https://www.bigbasket.com/cl/beverages/"
]

# Input and output files
input_file = 'bigbasket_data_combined.csv'
output_file = 'bigbasket_data_with_images.csv'

# Initialize WebDriver
driver = webdriver.Chrome()

def scrape_and_merge():
    # Load the existing CSV data
    existing_data = pd.read_csv(input_file)
    existing_data["Image URL"] = "N/A"  # Add a new column for Image URL

    # Dictionary to map product names to image URLs
    product_image_map = {}

    # Loop through category links
    for category_url in category_list:
        try:
            # Load the category page
            driver.get(category_url)
            time.sleep(2)  # Wait for the page to load
            
            # Parse the page source
            category_soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find all product containers
            product_containers = category_soup.find_all("div", class_="col-sm-12 col-xs-7 prod-view ng-scope")

            for container in product_containers:
                # Extract product name
                product_name_tag = container.find("a", class_="ng-binding")
                product_name = product_name_tag.get_text(strip=True) if product_name_tag else "N/A"

                # Extract image URL
                image_tag = container.find("img", class_="img-responsive ng-scope")
                image_url = image_tag.get("src", "N/A") if image_tag else "N/A"

                # Add to the dictionary
                product_image_map[product_name] = image_url

        except Exception as e:
            print(f"Error scraping category {category_url}: {e}")
            continue

    # Match the scraped image URLs to the existing data
    for index, row in existing_data.iterrows():
        product_name = row["Product Name"]
        if product_name in product_image_map:
            existing_data.at[index, "Image URL"] = product_image_map[product_name]

    # Save the updated data to the new output file
    existing_data.to_csv(output_file, index=False)
    print(f"Data with image URLs saved to {output_file}")

# Run the scraper and merge function
scrape_and_merge()

# Close the driver
driver.quit()
