import os
import mysql.connector
import re


def connect_to_database():
    try:
        conn = mysql.connector.connect(
            # host='34.94.17.75',
            host=os.getenv('host'),
            port='3306',
            user='root',
            # password='4r{4F"PYD5TQ|rMN',
            password='change-me',
            database='fse_engstore'
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Error connection to MySQL: {e}")
        return None


# 1. List all products that are out of stock.
def products_out_of_stock(conn):
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM Products WHERE UnitsInStock < 1;"
        cursor.execute(query)
        for (ProductID, ProductName, SupplierID, Category, UnitPrice, UnitsInStock) in cursor:
            print(f"ProductID: {ProductID}, ProductName: {ProductName}, SupplierID: {SupplierID}, "
                  f"Category: {Category}, UnitPrice: {UnitPrice}, UnitsInStock: {UnitsInStock}")
    except mysql.connector.Error as e:
        print(f"Error fetching records: {e}")


# 2. Find the total number of orders placed by each customer.
def customers_total_number_orders(conn):
    try:
        cursor = conn.cursor()
        query = ("SELECT C.CustomerID, C.CustomerName, C.ContactName, C.Address, C.City, C.PostalCode, C.Country, "
                 "COUNT(*) AS TotalNumberOrders FROM Orders AS O "
                 "INNER JOIN Customers AS C ON O.CustomerID = C.CustomerID "
                 "GROUP BY O.CustomerID;")
        cursor.execute(query)
        for (CustomerID, CustomerName, ContactName, Address, City, PostalCode, Country, TotalNumberOrders) in cursor:
            print(f"CustomerID: {CustomerID}, CustomerName: {CustomerName}, ContactName: {ContactName}, "
                  f"Address: {Address}, City: {City}, PostalCode: {PostalCode}, Country: {Country}, "
                  f"TotalNumberOrders: {TotalNumberOrders}")
    except mysql.connector.Error as e:
        print(f"Error fetching records: {e}")


# 3. Display the details of the most expensive product ordered in each order.
def most_expensive_product_in_order(conn):
    try:
        cursor = conn.cursor()
        # query = ("SELECT OrderID, P.ProductID, P.ProductName, P.SupplierID, P.Category, P.UnitPrice, OD.Quantity "
        #          "FROM OrderDetails AS OD "
        #          "JOIN Products AS P ON P.ProductID = OD.ProductID "
        #          "WHERE (OrderID, OD.UnitPrice) IN ( "
        #              "SELECT OrderID, MAX(UnitPrice) "
        #              "FROM OrderDetails "
        #              "GROUP BY OrderID"
        #              ");")
        query = ("SELECT O.OrderID, P.ProductID, P.ProductName, P.SupplierID, P.Category, P.UnitPrice, OD.Quantity "
                 "FROM Orders AS O "
                 "JOIN OrderDetails AS OD ON O.OrderID = OD.OrderID "
                 "JOIN Products AS P ON OD.ProductID = P.ProductID "
                 "WHERE (O.OrderID, OD.UnitPrice) IN ( "
                 "SELECT OrderID, MAX(UnitPrice) "
                 "FROM OrderDetails "
                 "GROUP BY OrderID )"
                 )
        cursor.execute(query)
        for (OrderID, ProductID, ProductName, SupplierID, Category, UnitPrice, Quantity) in cursor:
            print(f"OrderID: {OrderID}, ProductID: {ProductID}, ProductName: {ProductName}, SupplierID: {SupplierID}, "
                  f"Category: {Category}, UnitPrice: {UnitPrice}")
    except mysql.connector.Error as e:
        print(f"Error fetching records: {e}")


# 4. Retrieve a list of products that have never been ordered.
def never_ordered_products(conn):
    try:
        cursor = conn.cursor()
        query = ("SELECT * "
                 "FROM Products "
                 "WHERE ProductID NOT IN (SELECT ProductID FROM OrderDetails) "
                 )
        cursor.execute(query)
        for (ProductID, ProductName, SupplierID, Category, UnitPrice, UnitsInStock) in cursor:
            print(f"ProductID: {ProductID}, ProductName: {ProductName}, SupplierID: {SupplierID}, "
                  f"Category: {Category}, UnitPrice: {UnitPrice}, UnitsInStock: {UnitsInStock}")
    except mysql.connector.Error as e:
        print(f"Error fetching records: {e}")


# 5. Show the total revenue (price * quantity) generated by each supplier.
def total_supplier_revenue(conn):
    try:
        cursor = conn.cursor()
        query = ("SELECT S.SupplierID, S.SupplierName, "
                 "SUM(OD.UnitPrice*OD.Quantity) AS TotalRevenue "
                 "FROM Suppliers AS S "
                 "JOIN Products AS P ON S.SupplierID = P.SupplierID "
                 "JOIN OrderDetails AS OD ON P.ProductID = OD.ProductID "
                 "GROUP BY S.SupplierID "
                 "ORDER BY TotalRevenue DESC "
                 )
        cursor.execute(query)
        for (SupplierID, SupplierName, TotalRevenue) in cursor:
            print(f"SupplierID: {SupplierID}, SupplierName: {SupplierName}, TotalRevenue: {TotalRevenue}")
    except mysql.connector.Error as e:
        print(f"Error fetching records: {e}")


# 6. Create a stored procedure to add a new order. This should include
# inserting records into both the Orders and OrderDetails tables.

def add_new_order(conn):
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'

    try:
        cursor = conn.cursor()

        inputCustomerID = input("Enter CustomerID: ")
        while not inputCustomerID.isdigit():
            inputCustomerID = input("Enter CustomerID: ")

        inputOrderDate = input("Enter OrderDate (YYYY-MM-DD): ")
        while not re.match(date_pattern, inputOrderDate):
            inputOrderDate = input("Enter OrderDate (YYYY-MM-DD): ")

        inputShipDate = input("Enter ShipDate (YYYY-MM-DD): ")
        while not re.match(date_pattern, inputShipDate):
            inputShipDate = input("Enter ShipDate (YYYY-MM-DD): ")

        inputShipAddress = input("Enter ShipAddress: ")[:255]
        inputShipCity = input("Enter ShipCity: ")[:100]
        inputShipPostalCode = input("Enter ShipPostalCode: ")[:20]
        inputShipCountry = input("Enter ShipCountry: ")[:100]

        inputProductID = input("Enter ProductID: ")
        while not inputProductID.isdigit():
            inputProductID = input("Enter ProductID: ")

        inputQuantity = input("Enter Quantity: ")
        while not inputQuantity.isdigit():
            inputQuantity = input("Enter Quantity: ")

        cursor.callproc('AddNewOrder', (inputCustomerID, inputOrderDate, inputShipDate, inputShipAddress,
                                        inputShipCity, inputShipPostalCode, inputShipCountry, inputProductID,
                                        inputQuantity)
                        )
        conn.commit()

    except mysql.connector.Error as e:
        print(f"Error fetching records: {e}")


def check_input():
    while True:
        try:
            user_input = int(input("Enter a Number: "))
            if user_input < 1 or user_input > 7:
                print("Invalid input")
                continue
            break
        except ValueError:
            print("Invalid input")
    return user_input


def main():
    conn = connect_to_database()
    if conn:
        while True:
            print("1. List all products that are out of stock.")
            print("2. Find the total number of orders placed by each customer.")
            print("3. Display the details of the most expensive product ordered in each order.")
            print("4. Retrieve a list of products that have never been ordered.")
            print("5. Show the total revenue (price * quantity) generated by each supplier.")
            print("6. Add a new order.")
            print("7. Exit.")
            user_input = check_input()
            if user_input == 1:
                products_out_of_stock(conn)
            elif user_input == 2:
                customers_total_number_orders(conn)
            elif user_input == 3:
                most_expensive_product_in_order(conn)
            elif user_input == 4:
                never_ordered_products(conn)
            elif user_input == 5:
                total_supplier_revenue(conn)
            elif user_input == 6:
                add_new_order(conn)
            elif user_input == 7:
                break
            else:
                continue
    conn.close()


if __name__ == "__main__":
    main()
