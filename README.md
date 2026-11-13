# E-Commerce Order Portal

Assignment 3: End-to-End Portal Design

A console-based portal written in plain Python. Shop staff use it to manage products and customer orders.
All data is saved in simple text files, so nothing is lost when the program is closed.

## Group members

| Name | Roll No |
|---|---|
| Haseeb Ullah | 25L-4044 |
| Faiq Hassan | 24L-5166 |

## Features

- Login with username and password (3 attempts allowed)
- View all products in a table
- Add a new product (duplicate product IDs are rejected)
- Place an order: checks the product and the stock, reduces the stock, applies a discount
- View all orders
- Search orders by order ID or part of the customer name
- Update an order status (Pending, Shipped, Delivered)
- Cancel an order (the quantity goes back into stock)
- Sales report: number of orders, revenue, average order, biggest order, orders per status,
  best-selling product and low-stock products (also saved to `report.txt`)
- Sales statistics using pandas (bonus)
- Every action is written to `activity_log.txt`

Discount rule: 10% off when an order is Rs 50,000 or more, 5% off from Rs 20,000.

## Files

| File | What it holds |
|---|---|
| `portal.py` | The full program as one Python script |
| `portal.ipynb` | The same code split into notebook cells, with explanations and sample test runs |
| `products.csv` | Products: `product_id,name,category,price,stock` |
| `orders.csv` | Orders: `order_id,customer_name,product_id,product_name,quantity,total,status` |
| `users.txt` | Logins: one `username,password` per line |
| `activity_log.txt` | One line added for each action (created when the portal runs) |
| `report.txt` | The last sales report (created when a report is generated) |

## How to run

You need Python 3. pandas is only needed for the Sales statistics option.

From a terminal, inside this folder:

```
python portal.py
```

Or open `portal.ipynb` in Jupyter Notebook and run the cells from top to bottom. The last cell starts the portal.

## Sample login

| Username | Password |
|---|---|
| admin | admin123 |
| staff | staff123 |

If `users.txt` is missing, the program creates it with the `admin` login.

## Error handling

- Missing data file: the portal starts with an empty list instead of crashing (`FileNotFoundError`).
- File cannot be saved, for example when it is open in Excel: an error message is shown (`PermissionError`).
- Typing a word where a number is expected: the program asks again (`ValueError`).
- Zero or negative price, stock or quantity is rejected.
- Commas are not allowed in names, because they would break the CSV file.
- A damaged line in a data file is skipped and the rest is loaded.
- Ordering more than the stock raises our own `OutOfStockError`.

## Use of AI tools

Our instructor allowed AI help for this assignment. We used an AI assistant to help draft the code and documents,
then went through, tested and changed the code ourselves.
