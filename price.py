from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv

# Initialize the WebDriver
driver = webdriver.Chrome()

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

# Output CSV file
output_file = 'bigbasket_data_combined123.csv'

def scrape_categories():
    # Open the CSV file for writing
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(["Category", "Brand_Name", "Product Name", "Price", "Actual Price", 
                         "Weight/Quantity", "Offer", "Ratings", "Description", "Image_url"])

        # Track visited products to avoid duplicates
        visited_products = set()

        # Loop through each category link
        for category_url in category_list:
            try:
                driver.get(category_url)
                time.sleep(1)  # Wait for the page to load fully

                # Parse the category page
                category_soup = BeautifulSoup(driver.page_source, 'html.parser')
                category_name = category_soup.find("h1").get_text(strip=True) if category_soup.find("h1") else "Unknown Category"

                # Scrape product links
                product_links = [
                    "https://www.bigbasket.com" + a["href"]
                    for a in category_soup.find_all("a", href=True)
                    if "/pd/" in a["href"]
                ]

                # Filter out already visited product links
                product_links = [link for link in product_links if link not in visited_products]

                # Visit each product link
                for product_link in product_links:
                    try:
                        visited_products.add(product_link)  # Mark the product as visited
                        driver.get(product_link)
                        time.sleep(1)

                        # Parse the product page
                        product_soup = BeautifulSoup(driver.page_source, 'html.parser')

                        # Extract product-level details
                        brand_name = product_soup.find(class_="Label-sc-15v1nk5-0 BrandName___StyledLabel2-sc-hssfrl-1 gJxZPQ keQNWn")
                        product_name = product_soup.find('h3', class_='block m-0 line-clamp-2 font-regular text-base leading-sm text-darkOnyx-800 pt-0.5 h-full')
                        price = product_soup.find(class_="Label-sc-15v1nk5-0 Pricing___StyledLabel-sc-pldi2d-1 gJxZPQ AypOi")
                        actual_price = product_soup.find(class_='Label-sc-15v1nk5-0 Pricing___StyledLabel2-sc-pldi2d-2 gJxZPQ hsCgvu')
                        weight_quantity = product_soup.find(class_='Label-sc-15v1nk5-0 PackChanger___StyledLabel-sc-newjpv-1 gJxZPQ cWbtUx')
                        offer = product_soup.find(class_='Label-sc-15v1nk5-0 Tags___StyledLabel2-sc-aeruf4-1 gJxZPQ gKHXZJ')
                        ratings_div = product_soup.find('div', class_="ReviewsAndRatings___StyledDiv-sc-2rprpc-0 xQwmo")
                        if ratings_div:
                            rating_value = ratings_div.find('span', class_="Label-sc-16v1nk5-0 gJxZPQ")
                            ratings_text = rating_value.get_text(strip=True) if rating_value else "N/A"
                        else:
                            ratings_text = "N/A"
                        # Extract description
                        description_tag = product_soup.find(class_="bullets pd-4 leading-xss text-md")
                        description_text = description_tag.get_text(strip=True) if description_tag else ""
                        product_images = driver.find_elements(By.CSS_SELECTOR, 'section.Image___StyledSection-sc-1nc1erg-0 img')

                        # Get the 'src' attribute of the second image in the list
                        image_src1 = product_images[-1].get_attribute('src')

                        # Remove any URLs from the description
                        description_text = ' '.join(
                            word for word in description_text.split() if not word.startswith("http")
                        )

                        # Write data to CSV
                        writer.writerow([
                            category_name,
                            brand_name.get_text(strip=True) if brand_name else "N/A",
                            product_name.get_text(strip=True) if product_name else "N/A",
                            price.get_text(strip=True) if price else "N/A",
                            actual_price.get_text(strip=True) if actual_price else "N/A",
                            weight_quantity.get_text(strip=True) if weight_quantity else "N/A",
                            offer.get_text(strip=True) if offer else "N/A",
                            ratings_text,
                            description_text,
                            image_src1
                        ])
                        print(f"Scraped: {product_link}")

                    except Exception as e:
                        print(f"Error scraping product {product_link}: {e}")
                        continue

            except Exception as e:
                print(f"Error loading category {category_url}: {e}")
                continue

        print(f"Data saved to {output_file}")

# Run the scraper
scrape_categories()

# Close the driver after scraping
driver.quit()



# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import time

# # Path to your ChromeDriver
# url = 'https://www.bigbasket.com/pd/10000326/fresho-coriander-leaves-1-kg/'

# # Initialize WebDriver
# driver = webdriver.Chrome()

# # Open the website
# driver.get(url)

# # Wait for the page to load (adjust the time as needed for dynamic content)
# time.sleep(5)

# # Find the images within the product section using CSS selectors
# product_images = driver.find_elements(By.CSS_SELECTOR, 'section.Image___StyledSection-sc-1nc1erg-0 img')

# # Loop through the images and extract the 'src' attribute
# for img in product_images:
#     img_src = img.get_attribute('src')
#     print(img_src)

# # Close the browser
# driver.quit()
