from flask import Flask,render_template,redirect,request,send_file,flash,url_for,session,jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from datetime import datetime
import mysql.connector
import base64
import smtplib
import random
import csv
from io import StringIO
from flask import Response
import re
import datetime
app = Flask(__name__,static_folder='static')
app.secret_key='grocery_store'
app.config['SESSION_PERMANENT'] = False

bcrypt = Bcrypt(app)

# MySQL configuration
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Pabithashree123'
app.config['MYSQL_DB'] = 'grocery_store'

mysql = MySQL(app)

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "Siva08032004"

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

tokens = ["1","2","3",'4','5','6','7','8','9','0','q','w','e','r','t','y','u','i','o','p','a','s','d','f','g','h','j','k','l','z','x','c','v','b','n','m','Q','W','E','R','T','Y','U','I','O','P','A','S','D','F','G','H','J','K','L','Z','X','C','V','B','B','N','M']


@app.route('/save_personal_info', methods=['POST'])
def save_personal_info():
    name = request.form.get('firstName')
    # last_name = request.form.get('lastName')
    user_mail = session.get('email')
    # name = f'{first_name} {last_name}'

    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE customers SET customer_name = %s WHERE email = %s", (name, user_mail))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False})

    # Render the template with the updated first and last name
    return redirect('/my account')
@app.route('/save_mobile', methods=['POST'])
def save_mobile():
    mobile_number = request.form['mobileNumber']
    user_mail = session.get('email')
    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE customers SET mobile_number = %s WHERE email = %s", (mobile_number, user_mail))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False})
    return redirect('/my account')


@app.route('/save_address', methods=["GET",'POST'])
def save_address():
    # Get data from form
    go_to_payment = request.args.get('var',type=str)  
    customer_id = session.get('customer_id')
    name = request.form.get('name')
    email = request.form['email']
    mobile = request.form['mobile']
    pincode = request.form['pincode']
    address = request.form['address']
    landmark = request.form.get('landmark', '')
    district = request.form['district']
    state = request.form['state']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO customer_addresses (customer_id,name, email, mobile, pincode, address, landmark,district,state) VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s)",(customer_id,name,email,mobile,pincode,address,landmark,district,state))
    mysql.connection.commit()
    cur.close()
    if go_to_payment:
        return redirect('/payment')
    return redirect(url_for('my_account'))



# Route to Edit Address
@app.route('/edit_address/<int:address_id>', methods=['GET', 'POST'])
def edit_address(address_id):
    try:
        # Fetch the address details from the database using the address_id
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM customer_addresses WHERE address_id = %s", (address_id,))
        address = cur.fetchone()
        cur.close()

        if not address:
            flash("Address not found.", "danger")
            return redirect(url_for('my_account'))

        # Handle the POST request to update the address
        if request.method == 'POST':
            updated_name = request.form.get('name')
            updated_email = request.form.get('email')
            updated_mobile = request.form.get('mobile')
            updated_pincode = request.form.get('pincode')
            updated_address = request.form.get('address')
            updated_landmark = request.form.get('landmark')
            updated_district = request.form.get('district')
            updated_state = request.form.get('state')

            # Update the address details in the database
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE customer_addresses
                SET name = %s, email = %s, mobile = %s, pincode = %s, address = %s, 
                    landmark = %s, district = %s, state = %s
                WHERE address_id = %s
            """, (updated_name, updated_email, updated_mobile, updated_pincode, updated_address, 
                  updated_landmark, updated_district, updated_state, address_id))
            mysql.connection.commit()
            cur.close()

            flash("Address updated successfully.", "success")
            return redirect(url_for('my_account'))

        return render_template('myaccount.html', address=address)

    except Exception as e:
        print(f"Error fetching or updating address: {e}")
        return redirect(url_for('my_account'))


@app.route('/saveedited_address/<int:address_id>',methods=['GET', 'POST'])
def save_edited_add(address_id):
    customer_id = session.get('customer_id')
    name = request.form['name']
    email = request.form['email']
    mobile = request.form['mobile']
    pincode = request.form['pincode']
    address = request.form['address']
    landmark = request.form.get('landmark', '')
    district = request.form['district']
    state = request.form['state']
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE customer_addresses 
        SET customer_id = %s, name = %s, email = %s, mobile = %s, pincode = %s, 
            address = %s, landmark = %s, district = %s, state = %s 
        WHERE address_id = %s
    """, (customer_id, name, email, mobile, pincode, address, landmark, district, state, address_id))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('my_account'))

# Route to Delete Address
@app.route('/delete_address/<int:address_id>', methods=['POST'])
def delete_address(address_id):
    try:
        print(address_id)
        # Find the address by ID and delete it from the database
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM customer_addresses WHERE address_id = %s", (address_id,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('my_account'))
        
    except Exception as e:
        print(f"Error deleting address: {e}")
        flash("An error occurred while deleting the address.", "danger")
    
    return redirect(url_for('my_account'))







def send_otp(receiver_mail):
    otp = ''.join(random.choices('0123456789', k=4))  # Generate a 4-digit OTP
    sender_mail = "makemoney9047@gmail.com"
    sender_mail_pass = "rzbixshpspcvqqar"
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security
    s.starttls()
    # Authentication
    s.login(sender_mail,sender_mail_pass )
    # message to be sent
    message = f"'Your  OTP is' {otp}"

    # sending the mail
    s.sendmail(sender_mail, receiver_mail, message)
    # terminating the session
    s.quit()    
    return otp

def category():
    cur = None
    try:
        cur = mysql.connection.cursor()
        # Retrieve necessary columns
        cur.execute("SELECT category_id, category_name, category_image FROM category")
        categories = cur.fetchall()

        category_list = []

        if categories:
            for category in categories:
                category_id = category[0]  # First column: category_id
                category_name = category[1]  # Second column: category_name
                category_image = category[2]  # Third column: category_image

                category_list.append({
                    'id': category_id,
                    'name': category_name,
                    'image': category_image
                })
        else:
            return "No categories found in the database."

    except Exception as e:
        return f"Error fetching data: {e}"
    finally:
        if cur is not None:
            cur.close()

    return category_list

def get_offer_products(var):
    # Define the offer ranges based on the offer type
    offer_ranges = {
        5: (1, 5),        # Today Offer (1-5%)
        4: (10, 20),       # Best Offer (10-20%)
        3: (40, 80),     # Biggest Sale (40-80%)
        2: (30, 35),    # Special Offer (30-35%)
        1: (20, 30)      # Weekly Offer (20-30%)
    }
    
    # Get the offer range based on the passed 'var'
    if var in offer_ranges:
        min_offer, max_offer = offer_ranges[var]
        
        cursor = mysql.connection.cursor()
        try:
            # Query to get products within the offer range
            cursor.execute("SELECT * FROM products WHERE offers BETWEEN %s AND %s", (min_offer, max_offer))
            products = cursor.fetchall()
            products_list = []  # Initialize an empty list

            if products:
                for product in products:
                    product_id = product[0]
                    product_name = product[1]
                    price = product[3]
                    brand_name = product[2]
                    weight = product[5]
                    picture = product[8]
                    actual_price = product[4]
                    ratings = product[6]

                    # Append product details to the list
                    products_list.append({
                        'id': product_id,
                        'name': product_name,
                        'image': picture,
                        'price': price,
                        'weight': weight,
                        'brand': brand_name,
                        'actual_price':actual_price,
                        'ratings':ratings
                    })
            return products_list
        except Exception as e:
            return f"An error occurred: {e}"
        finally:
            cursor.close()
    else:
        return []  # If offer type is not recognized



def offers():
    cur = mysql.connection.cursor()

    try:
        cur.execute("SELECT offer_id, off_name, offer_image FROM offers")
        offers = cur.fetchall()

        # Debugging: Print out what categories contains

        offers_list = []

        if offers:
            for offer in offers:
                # Print each category for debugging

                # Ensure category has at least 3 elements
                if len(offer) >= 3:
                    offer_id = offer[0]
                    offer_name = offer[1]
                    offer_image = offer[2]

                    offers_list.append({
                        'offer_id': offer_id,
                        'offer_name': offer_name,
                        'offer_image': offer_image
                    })
                else:
                    return "Unexpected category structure: {offer}"
        else:
            return "No categories found in the database."

    except Exception as e:
        return "Error fetching data: {e}"
    finally:
        return offers_list
        cur.close()


def top_5_brands():
    cursor = mysql.connection.cursor()
    try:
        # Fetch the first 5 brands
        cursor.execute("SELECT * FROM topbrand LIMIT 5")
        brands = cursor.fetchall()  # Fetch results as tuples
        topbrands = []
        for brand in brands:
        # Map to a dictionary structure for easier template rendering
        
            topbrands.append({
                'brand_id': brand[0],
                'brand_name': brand[1],
                'brand_image': brand[2],
                'category_id': brand[3],
            })
            
        

        if not topbrands:
            return "No item found"
        return topbrands
    except Exception as e:
        print(f"Error fetching brands: {e}")
        return []
    finally:
        cursor.close()


def get_brand_pro(var):
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT * FROM products WHERE brand_name = %s", (var,))
        brand_pro = cur.fetchall()
        brand_pro_list = []
        if brand_pro:
            for product in brand_pro:
                    product_id = product[0]
                    product_name = product[1]
                    price = product[3]
                    brand_name = product[2]
                    weight = product[5]
                    picture = product[8]

                    # Append product details to the list
                    brand_pro_list.append({
                        'id': product_id,
                        'name': product_name,
                        'image': picture,
                        'price': price,
                        'weight': weight,
                        'brand': brand_name
                    })
        
        return brand_pro_list  # Return the list of products

    except Exception as e:
        # Log the error message for debugging
        print(f"Error fetching data: {e}")
        return []  # Return an empty list in case of an error

    finally:
        cur.close()          



def get_single_product(single_products):
    cur = mysql.connection.cursor()
    pro = []
    try:
        # Explicitly list required columns in the query
        cur.execute("""
            SELECT product_id, product_name, brand_name, price, actual_price, 
                   weight_quantity, ratings, description, image_url, 
                   stock_keep_unit, availability, country, category_id, expirydate
            FROM products
            WHERE product_id = %s
        """, (single_products,))  # Use parameterized query to prevent SQL injection

        # Fetch the single product details
        product = cur.fetchone()  # Fetch a single record

        if product:
            # Fetch column names for mapping
            columns = [desc[0] for desc in cur.description]
            product_details = dict(zip(columns, product))

            # Return product details as a dictionary
            pro.append( {
                'id': product_details.get('product_id'),
                'name': product_details.get('product_name'),
                'brand': product_details.get('brand_name'),
                'price': product_details.get('price'),
                'actual_price': product_details.get('actual_price'),
                'weight_quantity': product_details.get('weight_quantity'),
                'ratings': product_details.get('ratings'),
                'description': product_details.get('description'),
                'image': product_details.get('image_url'),
                'stock_keep_unit': product_details.get('stock_keep_unit'),
                'availability': product_details.get('availability'),
                'country': product_details.get('country'),
                'category_id': product_details.get('category_id'),
                'expiry_date': product_details.get('expirydate'),
            })
            return pro
        else:
            # Return None if no product is found
            return None

    except Exception as e:
        print(f"Error fetching product details: {e}")
        return None  # Return None in case of an error

    finally:
        cur.close()  # Always close the cursor


def show_products_cate_wise(var):
    cur = mysql.connection.cursor()

    try:
        # Execute query with proper parameter tuple (notice the comma in (var,))
        cur.execute("SELECT * FROM products WHERE category_id = %s", (var,))
        products = cur.fetchall()

        products_list = []  # Initialize an empty list

        if products:
            for product in products:
                product_id = product[0]
                product_name = product[1]
                price = product[3]
                brand_name = product[2]
                weight = product[5]
                picture = product[8]
                actual_price = product[4]
                ratings = product[6]

                # Append product details to the list
                products_list.append({
                    'id': product_id,
                    'name': product_name,
                    'image': picture,
                    'price': price,
                    'weight': weight,
                    'brand': brand_name,
                    'actual_price':actual_price,
                    'ratings':ratings
                })

        return products_list  # Return the list of products

    except Exception as e:
        # Log the error message for debugging
        print(f"Error fetching data: {e}")
        return []  # Return an empty list in case of an error

    finally:
        cur.close()  # Always close the cursor
        
def date_convertor(var):
    if var:
            try:
                # Parse the expiry date to ensure it's valid
                date = datetime.strptime(var, "%Y-%m-%d").date()
                return date
            except ValueError:
                # If the date is invalid, handle it here (e.g., set to None or return an error)
                date = None
    else:
        # Set expirydate to None if it's empty
        date = None

def image_checker(var):
    if var:
        image_data = var.read()
        return image_data     
    else:
        # handle the case where no file was sent
        return None

    
def add(customer_address):
        address_list = []
        for address in customer_address:
            address_dict = {}
            session['address_id'] = address[0]
            address_dict['address_id'] = address[0]
            address_dict['customer_id'] = address[1]
            address_dict['name'] = address[2]
            address_dict['email'] = address[3]
            address_dict['mobile'] = address[4]
            address_dict['pincode'] = address[5]
            address_dict['address'] = address[6]
            address_dict['landmark'] = address[7]
            address_dict['district'] = address[8]
            address_dict['state'] = address[9]
            address_list.append(address_dict)
        return address_list





@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        # Get the search query from the form
        search_query = request.form.get('search_query')

        # Check if the search query is None or empty
        if not search_query:
            return redirect('/home')

        # Sanitize input: lowercasing the search term and stripping unwanted spaces
        search_query = search_query.strip().lower()

        cursor = mysql.connection.cursor()

        try:
            # Search for products by name, description, or brand name
            cursor.execute("""
                SELECT * FROM products 
                WHERE LOWER(product_name) LIKE %s 
                OR LOWER(description) LIKE %s 
                OR LOWER(brand_name) LIKE %s
            """, ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))

            # Fetch the results from the query
            brand_pro = cursor.fetchall()

            # Convert the results into a list of dictionaries
            brand_pro_list = []
            if brand_pro:
                for product in brand_pro:
                    product_id = product[0]
                    product_name = product[1]
                    price = product[3]
                    brand_name = product[2]
                    weight = product[5]
                    picture = product[8]

                    # Append product details to the list as a dictionary
                    brand_pro_list.append({
                        'id': product_id,
                        'name': product_name,
                        'image': picture,
                        'price': price,
                        'weight': weight,
                        'brand': brand_name
                    })

            if not brand_pro_list:
                return redirect('/home')

            # Return the list of products to the template
            return render_template('products.html', products=brand_pro_list)

        except Exception as e:
            return f"An error occurred: {e}"

        finally:
            cursor.close()

    return render_template('home.html')  # Default page if no search

@app.route('/add_to_cart/<int:product_id>', methods=['GET'])
def add_to_cart(product_id):
    customer_id = session.get('customer_id')
    price = request.args.get('price', type=float) 
    image = request.args.get('image', type=str)
    name = request.args.get('name',type=str)  

    # Redirect to login if customer_id is not set
    if not customer_id:
        return redirect('/login')  # Replace with your login route

    cursor = mysql.connection.cursor()
    try:
        # Check if the product already exists in the cart
        cursor.execute("SELECT COUNT(*) FROM cart WHERE customer_id = %s AND product_id = %s", (customer_id, product_id))
        exists = cursor.fetchone()[0]  # Fetch count result

        if exists:
            # If the product is already in the cart, do nothing
            return redirect('/cart')

        # Insert the product into the cart if it doesn't exist
        cursor.execute("INSERT INTO cart (customer_id, product_id, quantity,price,product_name,image_url) VALUES (%s, %s, %s, %s, %s, %s)", (customer_id, product_id, 1,price,name,image))
        mysql.connection.commit()

        return redirect('/cart')

    except Exception as e:
        return f"Error: {e}"

    finally:
        cursor.close()



@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        action = request.form.get('action')
        product_id = int(action.split('-')[1])

        cursor = mysql.connection.cursor()

        # Handle increase, decrease, and delete actions
        if action.startswith("increase"):
            cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE product_id = %s AND customer_id = %s", (product_id, session['customer_id']))
        elif action.startswith("decrease"):
            cursor.execute("UPDATE cart SET quantity = GREATEST(quantity - 1, 1) WHERE product_id = %s AND customer_id = %s", (product_id, session['customer_id']))
        elif action.startswith("delete"):
            cursor.execute("DELETE FROM cart WHERE product_id = %s AND customer_id = %s", (product_id, session['customer_id']))

        mysql.connection.commit()
        cursor.close()
        flash("Cart updated successfully!", "success")
        return redirect(url_for('cart'))

    # Fetch cart items from the database
    cursor = mysql.connection.cursor()
    if 'customer_id' in session:
        cursor.execute("SELECT product_id, product_name, quantity, price, image_url FROM cart WHERE customer_id = %s", (session['customer_id'],))
        cart_items = cursor.fetchall()
        cursor.close()
    else:
        return redirect('login')    

    # Convert tuples to dictionaries
    cart_items_dict = []
    for item in cart_items:
        cart_items_dict.append({
            'product_id': item[0],
            'product_name': item[1],
            'quantity': item[2],
            'price': item[3],
            'image_url': item[4]
        })

    # Calculate subtotal and total items
    subtotal = sum(item['quantity'] * item['price'] for item in cart_items_dict)
    delivery_charge = 0
    if cart_items:
        delivery_charge = 40  # Flat delivery charge   
    total = subtotal + delivery_charge
    session['total'] = total
    total_items = sum(item['quantity'] for item in cart_items_dict)

    return render_template('cart.html', cart_items=cart_items_dict, subtotal=subtotal, total_items=total_items, delivery_charge=delivery_charge, total=total)

@app.route('/checkout')
def checkout():
    return "Checkout Page"



@app.route('/otp', methods=["GET", "POST"])
def verify_otp():
    username = session.get('username')
    user_email = session.get('email')
    hashed_password = session.get('hashed_password')
    token = session.get('otp')
    
    if request.method == "POST":
        user_otp = request.form['otp']
        if token == user_otp:
            # OTP is correct, store user in the database
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO customers (customer_name, email, password) VALUES (%s, %s, %s)', (username, user_email, hashed_password))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('login'))
        else:
            flash("Invalid OTP. Please try again.", "danger")
            
    return render_template('otp_page.html')


@app.route('/signup',methods=["GET","POST"])
def signup():
    if request.method == "POST" and "username" in request.form and "email" in request.form and "password" in request.form :
        name = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        cur = mysql.connection.cursor()

        if not re.match(EMAIL_REGEX, email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('signup'))
        if not re.match(PASSWORD_REGEX, password):
            flash('Password must be at least 8 characters long and include both letters and numbers.', 'danger')
            return redirect(url_for('signup'))
        
        # Check if email already exists
        cur.execute('SELECT email,password FROM customers WHERE email=%s or password = %s', [email,password])
        db_customer_data = cur.fetchall()
        print(db_customer_data)

        if db_customer_data:
            return "Email or Password already exists"
        else:
            session['username'] = name
            session['email'] = email
            session['hashed_password'] = hashed_password
            user_email = session.get('email')
            session['otp'] = send_otp(receiver_mail=user_email)
            return redirect(url_for('verify_otp'))    
        cur.close()    
    return render_template('signup.html')

@app.route('/login',methods=["POST","GET"])
def login():
    if request.method == "POST" and "email" in request.form and "password" in request.form:
        email = request.form["email"]
        session['email'] = email
        password = request.form["password"]
        if (email == ADMIN_EMAIL) and (password == ADMIN_PASSWORD):
            return redirect(url_for('admin_dashboard'))

        cur = mysql.connection.cursor()
        cur.execute('SELECT password , customer_id FROM customers WHERE email = %s', [email])
        fetching_email_password = cur.fetchone()
        
        if fetching_email_password:
            session['customer_id'] = fetching_email_password[1]
            hashed_password = fetching_email_password[0]
            if bcrypt.check_password_hash(hashed_password, password):
                return redirect('/home')  # Redirect to the home page on successful login
            else:
                return "Incorrect password"
        else:
            return "Email does not exist"
        cur.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')  # Redirect to the login page

@app.route('/home')
def home():
    category_list = category()
    offers_list = offers()
    brands = top_5_brands()
    return render_template('home.html', categories=category_list, offers = offers_list ,brands=brands)

@app.route('/home/offer/<int:var>')
def offer(var):
    products_var = get_offer_products(var)
    return render_template('products.html',products=products_var)


@app.route('/blog')
def blog():
    return render_template('blog.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
    


@app.route('/my account',methods=["GET","POST"])
def my_account():
    email = session.get('email')
    customer_id = session.get('customer_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM customers where email=%s",(email,))
    one_user = cur.fetchone()
    if one_user:
        customer_id = one_user[0]
        session['customer_id'] = customer_id
        name = one_user[1]
        user_name = name.split()
        first_name = user_name[0]
        # last_name = user_name[1]
        mobile_number = one_user[4]
    else:
        return redirect('/login')    
        
    cur.execute("SELECT * FROM customer_addresses where customer_id=%s",(customer_id,))
    customer_address = cur.fetchall()
    address_list = add(customer_address)
    cur.close()
    return render_template('my account.html',address_list=address_list,email=email,first_name=first_name,mobile_number=mobile_number)



@app.route('/add_address/<int:var>', methods=['GET', 'POST'])
def add_address(var):
    try:
        if var:
            customer_id = session.get('customer_id')
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM customer_addresses WHERE customer_id=%s", (customer_id,))
            customer_address = cur.fetchall()
            address_list = add(customer_address)  # Assuming you have a function to format or filter this list
            cur.close()
            
            # Render the form with address list
            return render_template('add address.html', address_list=address_list)
        else:
            return redirect('/cart')
    except Exception as e:
        return str(e)


@app.route('/products/<int:var>',methods=["GET","POST"])
def product(var):
    products_var = show_products_cate_wise(var)
    return render_template('products.html',products=products_var)


@app.route('/single product/<int:single_products>')
def single_product(single_products):
    product_var = get_single_product(single_products)
    category_id = product_var[0]['category_id']
    related_products = show_products_cate_wise(category_id)
    return render_template('single product.html',product=product_var,related_products=related_products)






@app.route('/topbrand/<string:var>',methods=["GET","POST"])
def top_brand(var):
    products_var = get_brand_pro(var)
    return render_template('products.html',products=products_var)
@app.route('/payment', methods=["POST", "GET"])
def payment():
    # Generate a new captcha for the user
    captcha = ''.join(random.choices(tokens, k=6))

    # Store captcha in session
    session['captcha'] = captcha

    if request.method == 'POST':
        selected_address = request.form.get('address')  # Get the address from the form

        # If the address is not provided, redirect to the add_address page
        if not selected_address:
            return redirect('/add_address')  # Redirect to the address page if no address is selected

        # Render the payment page with the selected address and captcha
        return render_template('payment.html', captcha=captcha, address=selected_address)

    # If it's a GET request, just render the payment page without any address or captcha
    return render_template('payment.html', captcha=captcha)


@app.route('/order_confirmation', methods=['POST', 'GET'])
def order_confirmation():
    try:
        # Retrieve the CAPTCHA from the session (stored during payment)
        captcha_from_session = session.get('captcha')
        print(captcha_from_session)
        if request.method == 'POST':
            # Retrieve the user-entered CAPTCHA from the form
            user_captcha = request.form.get('captchas')

            # Validate the CAPTCHA
            if user_captcha == captcha_from_session:
                # Proceed with order processing

                order_id = ''.join(random.choices('0123456789', k=10))
                address = request.form.get('address')  # Retrieve address from form data
                total = session.get('total')
                order_date = datetime.datetime.now().date()
                delivery_date = order_date + datetime.timedelta(days=1)
                customer_id = session.get('customer_id')

                # Fetch customer name from the database
                cursor = mysql.connection.cursor()
                cursor.execute("SELECT customer_name FROM customers WHERE customer_id = %s", (customer_id,))
                result = cursor.fetchone()
                customer_name = result[0] if result else "Guest"  # Handle missing customer name

                # Insert order into the database
                cursor.execute(
                    "INSERT INTO orders (order_id, customer_name, order_date, total, status, delivery_date, customer_id, address) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (order_id, customer_name, order_date, total, 'Pending', delivery_date, customer_id, address)
                )
                mysql.connection.commit()
                cursor.close()

                # Render confirmation page with order details
                return render_template(
                    'order confirmation.html',
                    order_id=order_id,
                    order_date=order_date,
                    delivery_date=delivery_date,
                    total=total,
                    address=address
                )
            else:
                # Invalid CAPTCHA; redirect back to the payment page with captcha token and selected address
                print("CAPTCHA validation failed.")
                return redirect(url_for('payment', captcha=captcha_from_session, address=address))

        else:
            print(captcha_from_session)
            # Redirect to payment page if method is not POST
            return redirect(url_for('payment'))
    
    except Exception as e:
        print(f"Error in order confirmation: {e}")
        return render_template('error.html', message="An unexpected error occurred. Please try again later.")



   
# @app.route('/admin')
# def admin():
#     return render_template('admin.html')

# @app.route('/admin customer details')
# def admin_customer_details():
#     return render_template('admin customer details.html')

# @app.route('/admin order details')
# def admin_order_details():
#     return render_template('admin order details.html')

# @app.route('/admin add product', methods=["GET", "POST"])
# def admin_add_product():
#     category = 0
#     if request.method == "POST":
#         # Function to read binary data is no longer necessary here.
#         p_id = request.form['productId']
        
#         # Ensure product_id is not empty
#         if not p_id:
#             return "Product ID is required!", 400  # Returning an error if productId is missing
        
#         # Convert productId to integer if it's provided as a string
#         try:
#             p_id = int(p_id)
#         except ValueError:
#             return "Invalid Product ID. It should be an integer.", 400  # Erro
#         name = request.form['productName']
#         description = request.form['description']
#         brand = request.form['brandName']
#         price = request.form['price']
#         expirydate = request.form["expiryDate"]
#         quantity = request.form.get("weightquantity")
#         stock = request.form['sku']
#         ratings = request.form["rating"]
#         nutritional_info = request.form["nutritionalInfo"]
#         country = request.form["country"]
#         categoryid = request.form['categoryId']
#         category_name = request.form['categoryName']
#         category_description = request.form['categoryDescription']

#         if stock:
#              availability = "available"

#         product_image = request.files["image"]
#         image_data = image_checker(product_image)
#         category_image = request.files["categoryImage"]
#         image_data1 = image_checker(category_image)


#         expirydate = date_convertor(expirydate)

#         # Insert the data into the database
#         cur = mysql.connection.cursor()
#         cur.execute('SELECT category_id FROM categories WHERE category_id = %s', [categoryid])
#         db_category_data =  cur.fetchone()

#         if not  db_category_data:
#             cur.execute('INSERT INTO categories (category_id,category_name,description,category_image) VALUES(%s,%s,%s,%s)',(categoryid,category_name,category_description,image_data1))
        
#         if p_id and categoryid: 
#             cur.execute('INSERT INTO products (product_id, product_name, price, brand_name, stock_keep_unit, expiry_date, weight_quantity, availability, ratings, nutritional_info, country, picture, category_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
#                     (p_id, name, price, brand, stock, expirydate, quantity, availability, ratings, nutritional_info, country, image_data, categoryid))
#         mysql.connection.commit()
#         cur.close()

#     return render_template('admin add product.html')


# @app.route('/admin add offers',methods=["GET","POST"])
# def add_offer():
#     if request.method == "POST":
#         offer_id = request.form['offer_id']
#         offer_name = request.form['offer_title']  
#         offer_description = request.form['offer_description']
#         start_date = date_convertor(request.form['start_date'])
#         end_date = date_convertor( request.form['end_date'])
#         discount_percentage = request.form['discount_percentage']
#         off_img = request.files['offer_image']
#         offer_image = image_checker(off_img)

#         cur = mysql.connection.cursor()
#         cur.execute('INSERT INTO offers (offer_id,off_name,off_desc,start_date,end_date,discount,image) VALUES(%s,%s,%s,%s,%s,%s,%s)',(offer_id,offer_name,offer_description,start_date,end_date,discount_percentage,offer_image))
#         mysql.connection.commit()
#         cur.close()

        
    
        

#     return render_template('admin add offers.html')




@app.route('/admin_dashboard')
def admin_dashboard():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM products")
    products = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    cursor.execute("SELECT COUNT(product_id) AS total_products FROM products")
    result = cursor.fetchone() 
    total_products = result[0]

    cursor.execute("SELECT * FROM orders")
    orders = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    cursor.execute('SELECT COUNT(order_id) AS total_orders, SUM(total) AS total_sales FROM orders') 
    result = cursor.fetchone() 
    total_orders = result[0] 
    total_sales = result[1] 
    dashboard_item = { 'total_orders': total_orders, 'total_sales': total_sales   }

    cursor.execute("SELECT * FROM customers")
    customers = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

    cursor.close()
    return render_template('admin_dashboard.html', products=products, orders=orders, customers=customers,dashboard_item=dashboard_item,total_products=total_products)


@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    brand = request.form['brand']
    price = request.form['price']
    actual_price = request.form['actual_price']
    weight_quantity = request.form['weight_quantity']
    ratings = request.form['ratings']
    description = request.form['description']
    image_url = request.form['image_url']
    stock = request.form['stock']
    availability = request.form['availability']
    country = request.form['country']
    category_id = request.form['category_id']
    expirydate = request.form['expirydate']
    offers = request.form['offers']
    
    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO products (product_name, brand_name, price, actual_price, weight_quantity, ratings, description, image_url, stock_keep_unit, availability, country, category_id, expirydate, offers) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (name, brand, price, actual_price, weight_quantity, ratings, description, image_url, stock, availability, country, category_id, expirydate, offers)
    )
    mysql.connection.commit()
    cursor.close()
    flash("Product added successfully!")
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (id,))
    row = cursor.fetchone()
    product = dict(zip([column[0] for column in cursor.description], row))
    
    if request.method == 'POST':
        name = request.form['name']
        brand = request.form['brand']
        price = request.form['price']
        actual_price = request.form['actual_price']
        weight_quantity = request.form['weight_quantity']
        ratings = request.form['ratings']
        description = request.form['description']
        image_url = request.form['image_url']
        stock = request.form['stock']
        availability = request.form['availability']
        country = request.form['country']
        category_id = request.form['category_id']
        expirydate = request.form['expirydate']
        offers = request.form['offers']
        
        cursor.execute(
            "UPDATE products SET product_name = %s, brand_name = %s, price = %s, actual_price = %s, weight_quantity = %s, ratings = %s, description = %s, image_url = %s, stock_keep_unit = %s, availability = %s, country = %s, category_id = %s, expirydate = %s, offers = %s "
            "WHERE product_id = %s",
            (name, brand, price, actual_price, weight_quantity, ratings, description, image_url, stock, availability, country, category_id, expirydate, offers, id)
        )
        mysql.connection.commit()
        cursor.close()
        flash("Product updated successfully!")
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:id>', methods=['POST','GET'])
def delete_product(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM products WHERE product_id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('admin_dashboard'))
@app.route('/generate_report', methods=['POST'])
def generate_report():
    report_type = request.form['report_type']
    
    cursor = mysql.connection.cursor()
    
    # Sales Report
    if report_type == 'sales':
        cursor.execute("SELECT order_id, customer_name, order_date, total FROM orders")
        sales_report = cursor.fetchall()
        return render_template('sales_report.html', sales_report=sales_report)

    # Customer Report
    elif report_type == 'customer':
        cursor.execute("SELECT customer_id, customer_name, email FROM customers")
        customer_report = cursor.fetchall()
        return render_template('customer_report.html', customer_report=customer_report)

    flash("Report generated successfully!")
    return redirect(url_for('admin_dashboard'))


@app.route('/all_products')
def all_products():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return render_template('all_products.html', products=products)

@app.route('/all_orders')
def all_orders():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    return render_template('all_orders.html', orders=orders)

@app.route('/all_customers')
def all_customers():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    return render_template('all_customers.html', customers=customers)



@app.route('/add_product_page',methods=["GET","POST"])
def add_product_page():
    return render_template('add_products_page.html')

@app.route('/add_products', methods=['GET', 'POST'])
def add_products():
    if request.method == 'POST':
        try:
            # Retrieve form data
            product_name = request.form['product_name']
            brand_name = request.form['brand_name']
            price = request.form['price']
            actual_price = request.form['actual_price']
            weight_quantity = request.form['weight_quantity']
            ratings = request.form['ratings']
            description = request.form['description']
            image_url = request.form['image_url']
            stock_keep_unit = request.form['stock_keep_unit']
            availability = request.form['availability']
            country = request.form['country']
            category_id = request.form['category_id']
            expirydate = request.form['expirydate']
            offers = request.form['offers']

            # Insert into the database
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO products 
                (product_name, brand_name, price, actual_price, weight_quantity, ratings, description, image_url, stock_keep_unit, availability, country, category_id, expirydate, offers)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (product_name, brand_name, price, actual_price, weight_quantity, ratings, description, image_url, stock_keep_unit, availability, country, category_id, expirydate, offers))
            mysql.connection.commit()
            flash("Product added successfully!", "success")
            return redirect(url_for('add_product'))

        except Exception as e:
            flash(f"Error: {e}", "danger")
    
    return redirct({{'admin_dashboard'}})


@app.route('/admin_logout',methods=["POST","GET"])
def admin_logout():
    return redirect(url_for('login'))

@app.route('/download_sales_report', methods=['POST',"GET"])
def download_sales_report():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT order_id, customer_name, order_date, total FROM orders")
    sales_report = cursor.fetchall()

    # Create the CSV file in memory
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Order ID', 'Customer Name', 'Order Date', 'Total'])  # Write header
    writer.writerows(sales_report)  # Write data rows

    output.seek(0)

    # Prepare CSV response
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=sales_report.csv'
    return response

@app.route('/download_customer_report', methods=['POST',"GET"])
def download_customer_report():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT customer_id, customer_name, email, total_spent FROM customers")
    customer_report = cursor.fetchall()

    # Create the CSV file in memory
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Customer ID', 'Customer Name', 'Email', 'Total Spent'])  # Write header
    writer.writerows(customer_report)  # Write data rows

    output.seek(0)

    # Prepare CSV response
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=customer_report.csv'
    return response

@app.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    try:
        cursor = mysql.connection.cursor()
        # Delete the customer from the database using their customer_id
        cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
        mysql.connection.commit()
        flash("Customer deleted successfully!", "success")
        return redirect(url_for('admin_dashboard'))  # Redirect to dashboard or customer management page

    except Exception as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for('admin_dashboard'))  # In case of error, redirect to dashboard


@app.route('/order_details/<int:order_id>')
def order_details(order_id):
    cursor = mysql.connection.cursor()

    # Fetch order and customer details from the orders table
    cursor.execute("""
        SELECT o.order_id, o.customer_id, o.order_date, o.status, c.customer_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_id = %s
    """, (order_id,))

    order_data = cursor.fetchone()

    if not order_data:
        flash("Order not found!", "danger")
        return redirect(url_for('admin_dashboard'))

    # Fetch the products in the order and calculate the total
    cursor.execute("""
        SELECT p.product_name, op.quantity, p.price, (op.quantity * p.price) AS total
        FROM order_products op
        JOIN products p ON op.product_id = p.product_id
        WHERE op.order_id = %s
    """, (order_id,))
    products = cursor.fetchall()

    # Calculate total sum of the order (sum of individual product totals)
    total_amount = sum([product[3] for product in products])

    # Prepare the data to be passed to the template
    return render_template('view_order.html', 
                           order_id=order_data[0], 
                           customer_id=order_data[1], 
                           customer_name=order_data[4],
                           order_date=order_data[2],
                           order_status=order_data[3],
                           products=products,
                           total_amount=total_amount)




if (__name__) == "__main__":
    app.run(debug=True)