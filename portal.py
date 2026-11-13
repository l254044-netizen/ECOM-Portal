# E-Commerce Order Portal
# Assignment 3 - End-to-End Portal Design
# Group members: Haseeb Ullah (25L-4044) and Faiq Hassan (24L-5166)
#
# A console portal for shop staff to manage products and customer orders.
# All data is kept in text files, so nothing is lost when the program closes.


# ==================== 1. Constants ====================

# File names used by the portal
PRODUCTS_FILE = "products.csv"
ORDERS_FILE = "orders.csv"
USERS_FILE = "users.txt"
LOG_FILE = "activity_log.txt"
REPORT_FILE = "report.txt"

# A product with this much stock or less is called "low stock"
LOW_STOCK_LIMIT = 5

# How many times the user can try to log in
MAX_LOGIN_ATTEMPTS = 3

# The only status values an order can have
STATUSES = ["Pending", "Shipped", "Delivered", "Cancelled"]

# First line (header) of each CSV file
PRODUCTS_HEADER = "product_id,name,category,price,stock"
ORDERS_HEADER = "order_id,customer_name,product_id,product_name,quantity,total,status"


# ==================== 2. Custom exception ====================

# Our own error, raised when a customer orders more than we have in stock.
# It is written the same way as FileTooLargeError in the class notebook.
class OutOfStockError(Exception):
    def __init__(self, message="Not enough stock for this order"):
        self.message = message
        super().__init__(self.message)


# ==================== 3. Input checking ====================

def check_text(text, label):
    """Checks that text is not empty and has no comma (a comma would break the CSV file).
    Takes the text and a label for the message. Returns True if the text is fine, otherwise False."""
    if text == "":
        print(f"Error: {label} cannot be empty.")
        return False
    if "," in text:
        print(f"Error: {label} cannot contain a comma.")
        return False
    return True


def convert_price(text):
    """Turns typed text into a price. Takes the text.
    Returns the price as a float, or None if the text is not a valid price."""
    try:
        price = float(text)
    except ValueError:
        print(f"Error: '{text}' is not a number. Please type a price like 1500 or 999.50")
        return None
    # the price must be above zero and not unrealistically large
    if price > 0 and price <= 10000000:
        return price
    print("Error: price must be more than 0 and not more than 10000000.")
    return None


def convert_whole_number(text, label):
    """Turns typed text into a whole number above zero (used for stock, quantity and order ID).
    Takes the text and a label for the message. Returns the number as an int, or None if it is not valid."""
    try:
        number = int(text)
    except ValueError:
        print(f"Error: {label} must be a whole number, not '{text}'.")
        return None
    if number <= 0:
        print(f"Error: {label} must be more than zero.")
        return None
    return number


def ask_text(prompt, label):
    """Keeps asking until the user types valid text.
    Takes the question to show and a label. Returns the text."""
    while True:
        text = input(prompt).strip()
        if check_text(text, label):
            return text


def ask_price(prompt):
    """Keeps asking until the user types a valid price.
    Takes the question to show. Returns the price as a float."""
    while True:
        price = convert_price(input(prompt).strip())
        if price is not None:
            return price


def ask_whole_number(prompt, label):
    """Keeps asking until the user types a whole number above zero.
    Takes the question to show and a label. Returns the number as an int."""
    while True:
        number = convert_whole_number(input(prompt).strip(), label)
        if number is not None:
            return number


# ==================== 4. File functions ====================

def load_products(filename):
    """Reads all products from the products CSV file. Takes the file name.
    Returns a list of product dictionaries (an empty list if the file is missing)."""
    products = []
    try:
        with open(filename, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Note: {filename} was not found. Starting with an empty product list.")
        return products

    # lines[1:] skips the first line because it is the header
    for line in lines[1:]:
        line = line.strip()
        if line == "":
            continue
        parts = line.split(",")
        if len(parts) != 5:
            print(f"Skipping damaged line in {filename}: {line}")
            continue
        try:
            product = {
                "product_id": parts[0],
                "name": parts[1],
                "category": parts[2],
                "price": float(parts[3]),
                "stock": int(parts[4])
            }
        except ValueError:
            print(f"Skipping damaged line in {filename}: {line}")
            continue
        products.append(product)
    return products


def save_products(filename, products):
    """Writes all products to the products CSV file. Takes the file name and the product list.
    Returns True if the file was saved, otherwise False."""
    try:
        with open(filename, "w") as file:
            file.write(PRODUCTS_HEADER + "\n")
            for product in products:
                parts = [product["product_id"], product["name"], product["category"],
                         str(product["price"]), str(product["stock"])]
                file.write(",".join(parts) + "\n")
        return True
    except PermissionError:
        print(f"Error: no permission to write {filename}. Close it if it is open in Excel and try again.")
        return False


def load_orders(filename):
    """Reads all orders from the orders CSV file. Takes the file name.
    Returns a list of order dictionaries (an empty list if the file is missing)."""
    orders = []
    try:
        with open(filename, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Note: {filename} was not found. Starting with an empty order list.")
        return orders

    for line in lines[1:]:
        line = line.strip()
        if line == "":
            continue
        parts = line.split(",")
        if len(parts) != 7:
            print(f"Skipping damaged line in {filename}: {line}")
            continue
        try:
            order = {
                "order_id": int(parts[0]),
                "customer_name": parts[1],
                "product_id": parts[2],
                "product_name": parts[3],
                "quantity": int(parts[4]),
                "total": float(parts[5]),
                "status": parts[6]
            }
        except ValueError:
            print(f"Skipping damaged line in {filename}: {line}")
            continue
        if order["status"] not in STATUSES:
            print(f"Skipping line with unknown status in {filename}: {line}")
            continue
        orders.append(order)
    return orders


def save_orders(filename, orders):
    """Writes all orders to the orders CSV file. Takes the file name and the order list.
    Returns True if the file was saved, otherwise False."""
    try:
        with open(filename, "w") as file:
            file.write(ORDERS_HEADER + "\n")
            for order in orders:
                parts = [str(order["order_id"]), order["customer_name"], order["product_id"],
                         order["product_name"], str(order["quantity"]), str(order["total"]),
                         order["status"]]
                file.write(",".join(parts) + "\n")
        return True
    except PermissionError:
        print(f"Error: no permission to write {filename}. Close it if it is open in Excel and try again.")
        return False


def log_activity(filename, message):
    """Adds one line to the end of the activity log (append mode).
    Takes the log file name and the message. Returns True if it was written, otherwise False."""
    try:
        with open(filename, "a") as file:
            file.write(message + "\n")
        return True
    except PermissionError:
        print("Warning: could not write to the activity log.")
        return False


# ==================== 5. Login ====================

def load_users(filename):
    """Reads usernames and passwords from the users file (one 'username,password' per line).
    Takes the file name. Returns a dictionary like {"admin": "admin123"}."""
    users = {}
    try:
        with open(filename, "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    users[parts[0]] = parts[1]
    except FileNotFoundError:
        # no users file yet, so make one with a default login
        print(f"{filename} was not found, so a default login was created.")
        print("Username: admin   Password: admin123")
        users["admin"] = "admin123"
        try:
            with open(filename, "w") as file:
                file.write("admin,admin123\n")
        except PermissionError:
            print(f"Warning: could not create {filename}.")
    finally:
        print("User file check completed.")

    # if the file had no valid lines, still allow the default login
    if len(users) == 0:
        print("No valid users found. You can log in with admin / admin123")
        users["admin"] = "admin123"
    return users


def check_login(users, username, password):
    """Checks one username and password. Takes the users dictionary, username and password.
    Returns True if they match, otherwise False."""
    if username in users:
        if users[username] == password:
            return True
    return False


def user_login(users):
    """Asks for a username and password and allows 3 tries. Takes the users dictionary.
    Returns the username if the login is correct, or None after 3 wrong tries."""
    attempts = 0
    while attempts < MAX_LOGIN_ATTEMPTS:
        print("\n--- Login ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        if check_login(users, username, password):
            print(f"Login successful. Welcome, {username}!")
            return username
        attempts = attempts + 1
        print(f"Wrong username or password. Attempts left: {MAX_LOGIN_ATTEMPTS - attempts}")
    return None


# ==================== 6. Products ====================

def find_product(products, product_id):
    """Looks for a product by its ID. Takes the product list and the product ID.
    Returns the product dictionary, or None if it is not found."""
    for product in products:
        if product["product_id"] == product_id:
            return product
    return None


def add_product(products, product_id, name, category, price, stock):
    """Adds a new product to the product list. Takes the product list and the new product's details.
    Returns True if it was added, or False if the ID already exists or a value is wrong."""
    if not check_text(product_id, "Product ID"):
        return False
    if not check_text(name, "Product name"):
        return False
    if not check_text(category, "Category"):
        return False
    if price <= 0:
        print("Error: price must be more than zero.")
        return False
    if stock <= 0:
        print("Error: stock must be more than zero.")
        return False
    if find_product(products, product_id) is not None:
        print(f"Error: a product with ID {product_id} already exists.")
        return False

    product = {
        "product_id": product_id,
        "name": name,
        "category": category,
        "price": price,
        "stock": stock
    }
    products.append(product)
    return True


def display_products(products):
    """Prints all products as a table. Takes the product list.
    Returns the number of products shown."""
    if len(products) == 0:
        print("There are no products to show.")
        return 0
    print("-" * 68)
    print(f"{'ID':<8}{'Name':<24}{'Category':<15}{'Price (Rs)':>13}{'Stock':>8}")
    print("-" * 68)
    for product in products:
        # [:23] cuts very long names so the table stays straight
        name = product["name"][:23]
        category = product["category"][:14]
        print(f"{product['product_id']:<8}{name:<24}{category:<15}{product['price']:>13.2f}{product['stock']:>8}")
    print("-" * 68)
    return len(products)


# ==================== 7. Orders ====================

def next_order_id(orders):
    """Works out the ID for a new order. Takes the order list.
    Returns the highest order ID so far plus one (1001 if there are no orders)."""
    highest = 1000
    for order in orders:
        if order["order_id"] > highest:
            highest = order["order_id"]
    return highest + 1


def calculate_total(price, quantity):
    """Works out the order total with a discount: 10% off from Rs 50000, 5% off from Rs 20000.
    Takes the price of one item and the quantity. Returns the total after discount."""
    subtotal = price * quantity
    if subtotal >= 50000:
        discount = subtotal * 0.10
    elif subtotal >= 20000:
        discount = subtotal * 0.05
    else:
        discount = 0
    total = subtotal - discount
    return round(total, 2)


def check_stock(product, quantity):
    """Checks that there is enough stock for an order. Takes the product and the quantity.
    Returns True if there is enough stock, otherwise raises OutOfStockError."""
    if quantity > product["stock"]:
        raise OutOfStockError(f"Only {product['stock']} of {product['name']} left, but {quantity} were ordered.")
    return True


def add_record(orders, products, customer_name, product_id, quantity):
    """Places a new order: checks the product and its stock, reduces the stock and adds the order.
    Takes the order list, product list, customer name, product ID and quantity.
    Returns the new order dictionary, or None if the order could not be placed."""
    if not check_text(customer_name, "Customer name"):
        return None
    if quantity <= 0:
        print("Error: quantity must be more than zero.")
        return None

    product = find_product(products, product_id)
    if product is None:
        print(f"Error: there is no product with ID {product_id}.")
        return None

    try:
        check_stock(product, quantity)
    except OutOfStockError as e:
        print(f"Error: {e}")
        return None

    # take the ordered items out of stock
    product["stock"] = product["stock"] - quantity

    order = {
        "order_id": next_order_id(orders),
        "customer_name": customer_name,
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "total": calculate_total(product["price"], quantity),
        "status": "Pending"
    }
    orders.append(order)
    return order


def display_orders(orders):
    """Prints orders as a table. Takes a list of orders.
    Returns the number of orders shown."""
    if len(orders) == 0:
        print("There are no orders to show.")
        return 0
    print("-" * 79)
    print(f"{'ID':<7}{'Customer':<20}{'Product':<23}{'Qty':>5}{'Total (Rs)':>13}  {'Status':<11}")
    print("-" * 79)
    for order in orders:
        customer = order["customer_name"][:19]
        product_name = order["product_name"][:22]
        print(f"{order['order_id']:<7}{customer:<20}{product_name:<23}{order['quantity']:>5}{order['total']:>13.2f}  {order['status']:<11}")
    print("-" * 79)
    return len(orders)


# ==================== 8. Search ====================

def search_record(orders, keyword):
    """Searches orders by order ID or by part of the customer name (not case sensitive).
    Takes the order list and the search word. Returns a list of matching orders."""
    matches = []
    keyword = keyword.strip().lower()
    # an empty search word would match everything, so return no matches
    if keyword == "":
        return matches
    for order in orders:
        if str(order["order_id"]) == keyword:
            matches.append(order)
        elif keyword in order["customer_name"].lower():
            matches.append(order)
    return matches


def find_order(orders, order_id):
    """Looks for one order by its ID. Takes the order list and the order ID (a number).
    Returns the order dictionary, or None if it is not found."""
    for order in orders:
        if order["order_id"] == order_id:
            return order
    return None


# ==================== 9. Update status and cancel ====================

def update_order_status(orders, order_id, new_status):
    """Changes the status of an order to Pending, Shipped or Delivered.
    Takes the order list, the order ID and the new status. Returns True if it was changed, otherwise False."""
    if new_status not in STATUSES:
        print(f"Error: '{new_status}' is not a valid status. Use Pending, Shipped or Delivered.")
        return False
    if new_status == "Cancelled":
        print("Please use the Cancel Order option, so the stock is put back.")
        return False

    order = find_order(orders, order_id)
    if order is None:
        print(f"Error: there is no order with ID {order_id}.")
        return False
    if order["status"] == "Cancelled":
        print("Error: this order is cancelled, so its status cannot be changed.")
        return False

    order["status"] = new_status
    return True


def cancel_order(orders, products, order_id):
    """Cancels an order and puts its quantity back into stock.
    Takes the order list, product list and order ID. Returns True if it was cancelled, otherwise False."""
    order = find_order(orders, order_id)
    if order is None:
        print(f"Error: there is no order with ID {order_id}.")
        return False
    if order["status"] == "Cancelled":
        print("Error: this order is already cancelled.")
        return False
    if order["status"] == "Delivered":
        print("Error: a delivered order cannot be cancelled.")
        return False

    order["status"] = "Cancelled"

    # put the items back into stock
    product = find_product(products, order["product_id"])
    if product is not None:
        product["stock"] = product["stock"] + order["quantity"]
    else:
        print("Note: this product is no longer in the list, so no stock was put back.")
    return True


# ==================== 10. Sales report ====================

def generate_report(orders, products, filename):
    """Works out the sales figures, prints them and saves them to the report file.
    Takes the order list, product list and report file name. Returns a dictionary with the summary."""
    total_revenue = 0
    counted_orders = 0
    biggest_order = None

    # start every status count at zero
    status_counts = {}
    for status in STATUSES:
        status_counts[status] = 0

    # product name -> how many were sold
    product_sales = {}

    for order in orders:
        status_counts[order["status"]] = status_counts[order["status"]] + 1

        # cancelled orders are not counted as sales
        if order["status"] == "Cancelled":
            continue
        total_revenue = total_revenue + order["total"]
        counted_orders = counted_orders + 1

        if biggest_order is None or order["total"] > biggest_order["total"]:
            biggest_order = order

        name = order["product_name"]
        if name in product_sales:
            product_sales[name] = product_sales[name] + order["quantity"]
        else:
            product_sales[name] = order["quantity"]

    if counted_orders > 0:
        average_order = total_revenue / counted_orders
    else:
        average_order = 0

    # find the product with the highest quantity sold
    best_product = "None"
    best_quantity = 0
    for name in product_sales:
        if product_sales[name] > best_quantity:
            best_product = name
            best_quantity = product_sales[name]

    low_stock = []
    for product in products:
        if product["stock"] <= LOW_STOCK_LIMIT:
            low_stock.append(f"{product['product_id']} {product['name']} ({product['stock']} left)")

    # build the report line by line, so we can print it and save it
    lines = []
    lines.append("=" * 50)
    lines.append("                 SALES REPORT")
    lines.append("=" * 50)
    lines.append(f"Total number of orders  : {len(orders)}")
    lines.append(f"Orders counted in sales : {counted_orders} (cancelled not counted)")
    lines.append(f"Total revenue           : Rs {total_revenue:.2f}")
    lines.append(f"Average order value     : Rs {average_order:.2f}")
    if biggest_order is not None:
        lines.append(f"Biggest order           : #{biggest_order['order_id']} by {biggest_order['customer_name']} (Rs {biggest_order['total']:.2f})")
    else:
        lines.append("Biggest order           : none yet")
    lines.append(f"Best-selling product    : {best_product} ({best_quantity} sold)")
    lines.append("-" * 50)
    lines.append("Orders in each status:")
    for status in STATUSES:
        lines.append(f"  {status:<10} : {status_counts[status]}")
    lines.append("-" * 50)
    lines.append(f"Low stock products ({LOW_STOCK_LIMIT} or fewer left):")
    if len(low_stock) == 0:
        lines.append("  None")
    for item in low_stock:
        lines.append("  " + item)
    lines.append("=" * 50)

    for line in lines:
        print(line)

    try:
        with open(filename, "w") as file:
            for line in lines:
                file.write(line + "\n")
        print(f"Report saved to {filename}")
    except PermissionError:
        print(f"Error: no permission to write {filename}, so the report was not saved.")
    finally:
        print("Report generation finished.")

    summary = {
        "total_orders": len(orders),
        "total_revenue": round(total_revenue, 2),
        "average_order": round(average_order, 2),
        "biggest_order": biggest_order,
        "status_counts": status_counts,
        "best_product": best_product,
        "low_stock": low_stock
    }
    return summary


# ==================== 11. Sales statistics with pandas (bonus) ====================

def sales_statistics(filename):
    """Uses pandas to show extra statistics from the orders CSV file. Takes the file name.
    Returns the pandas DataFrame of orders, or None if the data could not be read."""
    # pandas is imported here and not at the top, so the rest of the
    # portal still works on a computer that does not have pandas
    try:
        import pandas as pd
    except ImportError:
        print("pandas is not installed, so statistics are not available.")
        return None

    try:
        data = pd.read_csv(filename)
    except FileNotFoundError:
        print(f"Error: {filename} was not found, so there are no statistics to show.")
        return None
    except pd.errors.EmptyDataError:
        print(f"Error: {filename} is empty, so there are no statistics to show.")
        return None

    if len(data) == 0:
        print("There are no orders yet.")
        return data

    # keep only the orders that were not cancelled
    sales = data[data["status"] != "Cancelled"]

    print("Quantity sold per product:")
    print(sales.groupby("product_name")["quantity"].sum())
    print("\nRevenue per product (Rs):")
    print(sales.groupby("product_name")["total"].sum())
    print("\nTotal order value in each status (Rs):")
    print(data.groupby("status")["total"].sum())
    print("\nAverage order value (Rs):", round(sales["total"].mean(), 2))
    print("\nSummary of order totals (Rs):")
    print(sales["total"].describe())
    return data


# ==================== 12. Menu and main program ====================

def show_menu():
    """Prints the main menu. Takes nothing and returns nothing."""
    print("\n" + "=" * 40)
    print("   E-COMMERCE ORDER PORTAL - MAIN MENU")
    print("=" * 40)
    print("1.  View products")
    print("2.  Add product")
    print("3.  Place order")
    print("4.  View orders")
    print("5.  Search order")
    print("6.  Update order status")
    print("7.  Cancel order")
    print("8.  Sales report")
    print("9.  Sales statistics (pandas)")
    print("10. Exit")
    print("=" * 40)


def main():
    """Runs the portal: loads the data, asks for login, then shows the menu until the user exits.
    Takes nothing and returns nothing."""
    print("=" * 40)
    print("   WELCOME TO THE E-COMMERCE ORDER PORTAL")
    print("=" * 40)

    # read the saved data on startup
    products = load_products(PRODUCTS_FILE)
    orders = load_orders(ORDERS_FILE)
    users = load_users(USERS_FILE)
    print(f"Loaded {len(products)} products and {len(orders)} orders.")

    username = user_login(users)
    if username is None:
        print("Too many wrong attempts. The portal will now close.")
        log_activity(LOG_FILE, "Failed login: 3 wrong attempts")
        return
    log_activity(LOG_FILE, f"{username} logged in")

    while True:
        show_menu()
        choice_text = input("Enter your choice (1-10): ").strip()
        try:
            choice = int(choice_text)
        except ValueError:
            print("Please enter a number from 1 to 10.")
            continue

        if choice == 1:
            print("\n--- All Products ---")
            display_products(products)

        elif choice == 2:
            print("\n--- Add a New Product ---")
            product_id = ask_text("Product ID (for example P111): ", "Product ID").upper()
            name = ask_text("Product name: ", "Product name")
            category = ask_text("Category: ", "Category")
            price = ask_price("Price in Rs: ")
            stock = ask_whole_number("Stock quantity: ", "Stock")
            if add_product(products, product_id, name, category, price, stock):
                print(f"Product {product_id} added.")
                save_products(PRODUCTS_FILE, products)
                log_activity(LOG_FILE, f"{username} added product {product_id} ({name})")

        elif choice == 3:
            print("\n--- Place an Order ---")
            display_products(products)
            customer_name = ask_text("Customer name: ", "Customer name")
            product_id = ask_text("Product ID: ", "Product ID").upper()
            quantity = ask_whole_number("Quantity: ", "Quantity")
            order = add_record(orders, products, customer_name, product_id, quantity)
            if order is not None:
                print(f"Order {order['order_id']} placed. Total after discount: Rs {order['total']:.2f}")
                save_products(PRODUCTS_FILE, products)
                save_orders(ORDERS_FILE, orders)
                log_activity(LOG_FILE, f"{username} placed order {order['order_id']} for {customer_name}")

        elif choice == 4:
            print("\n--- All Orders ---")
            display_orders(orders)

        elif choice == 5:
            print("\n--- Search Orders ---")
            keyword = input("Enter an order ID or part of a customer name: ")
            matches = search_record(orders, keyword)
            if len(matches) == 0:
                print("No matching orders found.")
            else:
                print(f"Found {len(matches)} matching order(s):")
                display_orders(matches)
            log_activity(LOG_FILE, f"{username} searched for '{keyword.strip()}'")

        elif choice == 6:
            print("\n--- Update Order Status ---")
            order_id = ask_whole_number("Order ID: ", "Order ID")
            new_status = input("New status (Pending / Shipped / Delivered): ").strip().capitalize()
            if update_order_status(orders, order_id, new_status):
                print(f"Order {order_id} is now {new_status}.")
                save_orders(ORDERS_FILE, orders)
                log_activity(LOG_FILE, f"{username} changed order {order_id} to {new_status}")

        elif choice == 7:
            print("\n--- Cancel an Order ---")
            order_id = ask_whole_number("Order ID to cancel: ", "Order ID")
            if cancel_order(orders, products, order_id):
                print(f"Order {order_id} cancelled and stock put back.")
                save_products(PRODUCTS_FILE, products)
                save_orders(ORDERS_FILE, orders)
                log_activity(LOG_FILE, f"{username} cancelled order {order_id}")

        elif choice == 8:
            print()
            generate_report(orders, products, REPORT_FILE)
            log_activity(LOG_FILE, f"{username} generated the sales report")

        elif choice == 9:
            print("\n--- Sales Statistics ---")
            sales_statistics(ORDERS_FILE)
            log_activity(LOG_FILE, f"{username} viewed sales statistics")

        elif choice == 10:
            # save everything one last time before leaving
            products_saved = save_products(PRODUCTS_FILE, products)
            orders_saved = save_orders(ORDERS_FILE, orders)
            if products_saved and orders_saved:
                print("All data saved.")
            else:
                print("Some data could not be saved.")
            log_activity(LOG_FILE, f"{username} logged out")
            print("Thank you for using the portal. Goodbye!")
            break

        else:
            print("Please enter a number from 1 to 10.")


# ==================== 13. Start the portal ====================

main()
