from flask import Flask
from flask_mysqldb import MySQL
import pandas as pd
import random
import re
from datetime import datetime, timedelta

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Pabithashree123'
app.config['MYSQL_DB'] = 'grocery_store'

# Initialize MySQL
mysql = MySQL(app)

# Load the CSV file
file_path = 'bigbasket_data_combined.csv'
data = pd.read_csv(file_path)

# Clean the data
category_mapping = {
    'Buy Fruits and Vegetables Online': 1,
    'Buy Bakery Cakes and Dairy Online': 2,
    'Buy Eggs, Meat and Fish Online: Meat Store Near Me': 3,
    'Buy Groceries Online': 4,
    'Buy Branded Food Online': 5,
    'Beauty Hygiene Products': 6,
    'Buy Household Items Online': 7,
    'Buy baby care products online': 8,
    'Buy Beverages Online': 9,
}

# Strip whitespace from column names
data.columns = data.columns.str.strip()

# Rename columns to match MySQL table structure
data.rename(columns={
    'Product Name': 'product_name',
    'Brand_Name': 'brand_name',
    'Price': 'price',
    'Actual Price': 'actual_price',
    'Weight/Quantity': 'weight_quantity',
    'Description': 'description',
    'Image_url': 'image_url'
}, inplace=True)

# Map categories to numbers
data['category'] = data['Category'].map(category_mapping)

# Remove rows with null or 'N/A' values in important columns (after 'category' is created)
data = data.dropna(subset=['product_name', 'brand_name', 'price', 'actual_price', 'weight_quantity', 'description', 'category'])
data = data[data['brand_name'] != 'N/A']

# Add the 'ratings' column if it doesn't exist
if 'ratings' not in data.columns:
    data['ratings'] = [round(random.uniform(1, 5), 1) for _ in range(len(data))]

# Replace missing ratings (NaN) with random ratings
data['ratings'] = data['ratings'].fillna(round(random.uniform(1, 5), 1))

# Replace missing brand names with the most frequent brand per category
def replace_brand(row, category_brands):
    if row['brand_name'] == 'N/A':
        return category_brands.get(row['category'], 'Unknown Brand')
    return row['brand_name']

# Generate random price
def random_price():
    return round(random.uniform(10, 500), 2)

# Generate random weight/quantity
def random_weight():
    return f"{random.randint(1, 5)}kg"

# Replace missing brand names
category_brands = data.groupby('category')['brand_name'].apply(
    lambda x: x.mode()[0] if not x.mode().empty else 'Unknown Brand'
).to_dict()
data['brand_name'] = data.apply(replace_brand, axis=1, category_brands=category_brands)

# Clean the price column
def clean_price(value):
    if isinstance(value, str):
        value = re.sub(r'[^\d\.]', '', value)  # Remove non-numeric characters
    try:
        return float(value)  # Convert to a float
    except ValueError:
        return random_price()  # Default value if conversion fails

# Apply cleaning functions
data['price'] = data['price'].apply(clean_price)
data['actual_price'] = data['actual_price'].apply(clean_price)

# Handle missing weight_quantity values (replace with random weight if necessary)
data['weight_quantity'] = data['weight_quantity'].apply(lambda x: random_weight() if x == 'N/A' else x)

# Handle missing expiry date (set a default expiry date)
data['expirydate'] = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

# Insert data into MySQL
@app.route('/insert_data')
def insert_data():
    # Create a cursor to interact with the database
    cur = mysql.connection.cursor()

    # SQL for insertion
    sql_insert = """
    INSERT INTO products (
        product_name, brand_name, price, actual_price, 
        weight_quantity, ratings, description, image_url, 
        stock_keep_unit, expirydate, availability, country, category_id
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        # Insert data
        for _, row in data.iterrows():
            # Ensure ratings is a valid number (if it's missing or NaN)
            ratings = row['ratings'] if pd.notna(row['ratings']) else round(random.uniform(1, 5), 1)

            # Ensure the value is not NaN
            ratings = float(ratings)

            values = (
                row['product_name'], row['brand_name'], row['price'], row['actual_price'],
                row['weight_quantity'], ratings, row['description'], row['image_url'],
                50, row['expirydate'], 'yes', 'india', row['category']
            )
            print(values)  # Debugging: Print values being inserted
            cur.execute(sql_insert, values)

        mysql.connection.commit()  # Commit transaction
        return "Data inserted successfully!"

    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"

    finally:
        # Close the cursor
        cur.close()


category_data = [
    ('Fruits and Vegetables', 'Fresh and organic fruits and vegetables, sourced locally and delivered to your door.', "D:\Mini Project\Images\categories\friuts and vegitables.jpeg"),
    ('Bakery, Cakes, and Dairy', 'Delicious bakery items, fresh cakes, and dairy products for all your needs.', "D:\Mini Project\Images\categories\Dairy and bakery.jpeg"),
    ('Meat Store', 'Fresh meat and fish from trusted sources, delivered straight to your home.', "D:\Mini Project\Images\categories\OIP.jfif"),
    ('Groceries', 'Your one-stop shop for all grocery items including cereals, grains, and snacks.', "D:\Mini Project\Images\categories\groceries.jpg"),
    ('Branded Food', 'Top branded food items with guaranteed quality and taste.', "D:\Mini Project\Images\categories\OIP (1).jfif"),
    ('Beauty and Hygiene', 'Personal care products, cosmetics, and hygiene essentials for your daily needs.', "D:\Mini Project\Images\categories\OIP (3).jfif"),
    ('Household Items', 'Essential household items to make your life easier, from cleaning supplies to kitchen essentials.', "D:\Mini Project\Images\categories\OIP (4).jfif"),
    ('Baby Care', 'All baby care products including diapers, wipes, baby food, and more.', "D:\Mini Project\Images\categories\OIP (5).jfif"),
    ('Beverages', 'A wide variety of beverages including soft drinks, juices, tea, and coffee.', "D:\Mini Project\Images\categories\cool drinks.jpeg")
]
@app.route('/insert_categories')
def insert_categories():
    # Create a cursor to interact with the database
    cur = mysql.connection.cursor()

    # Define the SQL insert query
    sql_insert = """
    INSERT INTO category (category_name, category_description, category_image)
    VALUES (%s, %s, %s)
    """

    try:
        # Insert multiple rows using executemany
        cur.executemany(sql_insert, category_data)
        mysql.connection.commit()  # Commit transaction
        return "Categories inserted successfully!"

    except Exception as e:
        # Handle errors during insertion
        return f"Error: {e}"

    finally:
        # Close the cursor after execution
        cur.close()







# Test database connection
@app.route('/test_connection')
def test_connection():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        return "Database connection successful!"
        cur.close()
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)
