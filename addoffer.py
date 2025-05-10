from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# Database configuration
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Pabithashree123'
app.config['MYSQL_DB'] = 'grocery_store'

mysql = MySQL(app)

# Route to update offers column
@app.route('/update_offers', methods=['GET'])
def update_offers():
    cursor = mysql.connection.cursor()
    try:
        # Fetch all products with price and actual_price
        cursor.execute("SELECT product_id, price, actual_price FROM products")
        products = cursor.fetchall()

        # Loop through the products and calculate offers
        for product in products:
            product_id = product[0]
            price = product[1]
            actual_price = product[2]

            # Calculate the offer percentage as an integer
            if actual_price > 0:  # Avoid division by zero
                offer = int(((actual_price - price) / actual_price) * 100)
                # If the offer is negative, set it to 0
                if offer < 0:
                    offer = 0
            else:
                offer = 0  # Default to 0 if actual_price is 0

            # Update the offers column in the database
            cursor.execute("UPDATE products SET offers = %s WHERE product_id = %s", (offer, product_id))

        # Commit changes to the database
        mysql.connection.commit()

        return "Offers updated successfully for all products!"

    except Exception as e:
        return f"An error occurred: {e}"

    finally:
        cursor.close()


if __name__ == "__main__":
    app.run(debug=True)
