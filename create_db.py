from app import app, db
from models import *
from datetime import datetime as dt
from werkzeug.security import generate_password_hash


with app.app_context():
    db.drop_all()
    db.create_all()
    # Initial loading of the users
    users = [
        {'username': 'manager', 'password': generate_password_hash('managerpw', method='pbkdf2:sha256'),
         'role': 'MANAGER'},
        {'username': 'admin', 'password': generate_password_hash('adminpw', method='pbkdf2:sha256'), 'role': 'ADMIN'},
        {'username': 'customer', 'password': generate_password_hash('customerpw', method='pbkdf2:sha256'), 'role': 'CUSTOMER'}

    ]
    # initial loading of merchandise items
    merchitemlist = [
        {'item_id': 1, 'item_name': 'Lightweight Performance Polo', 'item_price': 45.99, 'item_class': 'Unisex',
         'long_desc': "Show your love for the Maryland Terrapins on the diamond with this "
                      "lightweight performance polo! It has a classic polo"
                      "look and feel, but with a little extra comfort thanks to its cotton and polyester blend. "
                      "It's a must-have for any Maryland Terrapins Baseball fan.",
         'manu_details': 'Brand: Under Armor, Imported, lightweight polo suitable for hot temperatures, '
                         'Polo with buttons, logo, collared, Ribbed cuffs, '
                         'Short Sleeve, Material: 50% Cotton/50% Polyester, Machine wash, Tumble dry low, '
                         'Officially licensed'},
        {'item_id': 2, 'item_name': 'Quarter Zip Pullover', 'item_price': 50.99, 'item_class': 'Unisex',
         'long_desc': "Display your pride comfortably with this Maryland Terrapins Baseball Performance Quarter "
                      "Zip from Under Armour. The long sleeve features lightweight fabric to keep you "
                      "comfortable, whether you're cheering from the stands or lounging around the house. "
                      "The design includes Club Baseball graphics so that your team pride "
                      "will be the stylish focal point of your outfit.",
         'manu_details': "Brand: Under Armour, Imported, Screen printed graphics, Material: "
                         "60% Polyester/40% Cotton, Long sleeve, HeatGear® technology regulates "
                         "your body temperature and wicks away moisture, Officially licensed"},
        {'item_id': 3, 'item_name': 'Team Chino Hat', 'item_price': 20.99, 'item_class': 'Unisex',
         'long_desc': "Support your favorite Maryland Terrapins Baseball player with this Under Armor "
                      "Branded Baseball Gameday Tradition Cap!"
                      "It's made from 100% Chino and features front and back graphics.",
         'manu_details': "Brand: Under Amrmor, Imported, Material: 100% Chino, "
                         },
        {'item_id': 4, 'item_name': 'Hustle Team Backpack', 'item_price': 35.99, 'item_class': 'Unisex',
         'long_desc': "Support the Maryland Terrapins Baseball club with this Under Armor "
                      "Branded Club Baseball Backpack!",
         'manu_details': "Brand: Under Amrmor, Imported, Material: 50% Polyester/50% Nylon "}
    ]

    # Initial loading of inventory items
    inventorylist = [
        {'item_id': 1, 'product_code': 'polo-s-white',
         'product_stock': 15, 'product_size': 'S', 'product_color': 'White',
         'image_dir': 'whitepolo.png', 'purchase_price': 30},
        {'item_id': 1, 'product_code': 'polo-m-white',
         'product_stock': 15, 'product_size': 'M', 'product_color': 'White',
         'image_dir': 'whitepolo.png', 'purchase_price': 30},
        {'item_id': 1, 'product_code': 'polo-l-white',
         'product_stock': 15, 'product_size': 'L', 'product_color': 'White',
         'image_dir': 'whitepolo.png', 'purchase_price': 30},
        {'item_id': 1, 'product_code': 'polo-xl-white',
         'product_stock': 15, 'product_size': 'XL', 'product_color': 'White',
         'image_dir': 'whitepolo.png', 'purchase_price': 30},
        {'item_id': 1, 'product_code': 'polo-s-red',
         'product_stock': 15, 'product_size': 'S', 'product_color': 'Red',
         'image_dir': 'redpolo.png', 'purchase_price': 30},
        {'item_id': 1, 'product_code': 'polo-m-red',
         'product_stock': 15, 'product_size': 'M', 'product_color': 'Red',
         'image_dir': 'redpolo.png', 'purchase_price': 30},
        {'item_id': 1, 'product_code': 'polo-l-red',
         'product_stock': 15, 'product_size': 'L', 'product_color': 'Red',
         'image_dir': 'redpolo.png', 'purchase_price': 30},
        {'item_id': 1, 'product_code': 'polo-xl-red',
         'product_stock': 15, 'product_size': 'XL', 'product_color': 'Red',
         'image_dir': 'redpolo.png', 'purchase_price': 30},
        {'item_id': 2, 'product_code': 'qzip-xs-white',
         'product_stock': 10, 'product_size': 'XS', 'product_color': 'White',
         'image_dir': 'whitequarterzip.png', 'purchase_price': 30},
        {'item_id': 2, 'product_code': 'qzip-s-white',
         'product_stock': 10, 'product_size': 'S', 'product_color': 'White',
         'image_dir': 'whitequarterzip.png', 'purchase_price': 30},
        {'item_id': 2, 'product_code': 'qzip-m-white',
         'product_stock': 10, 'product_size': 'M', 'product_color': 'White',
         'image_dir': 'whitequarterzip.png', 'purchase_price': 30},
        {'item_id': 2, 'product_code': 'qzip-l-white',
         'product_stock': 10, 'product_size': 'L', 'product_color': 'White',
         'image_dir': 'whitequarterzip.png', 'purchase_price': 30},
        {'item_id': 2, 'product_code': 'qzip-xl-white',
         'product_stock': 10, 'product_size': 'XL', 'product_color': 'White',
         'image_dir': 'whitequarterzip.png', 'purchase_price': 30},
        {'item_id': 3, 'product_code': 'hat-s-gray',
         'product_stock': 5, 'product_size': 'S', 'product_color': 'Gray',
         'image_dir': 'grayteamchinohat.png', 'purchase_price': 20},
        {'item_id': 3, 'product_code': 'hat-l-gray',
         'product_stock': 5, 'product_size': 'L', 'product_color': 'Gray',
         'image_dir': 'grayteamchinohatback.png', 'purchase_price': 20},
        {'item_id': 4, 'product_code': 'backpack-m-gray',
         'product_stock': 5, 'product_size': 'M', 'product_color': 'Gray',
         'image_dir': 'graybackpack.png', 'purchase_price': 20},
    ]

    # fake orders
    orderlist = [
        {'order_date': dt(2024, 4, 1, 1, 0, 0),
         'first_name': 'John', 'last_name': 'Smith', 'email': '<EMAIL>',
         'address': '7002 Mowatt Ln', 'city': 'San Francisco', 'state': 'CA', 'zipcode': '94103',
         'order_total': 50.00},
        {'order_date': dt.now(),
         'first_name': 'Lucas', 'last_name': 'Gonzalez-Rey', 'email': 'lucasglezrey120@gmail.com',
         'address': '1101 Tenleytown St', 'city': 'Washington', 'state': 'DC', 'zipcode': '20016',
         'order_total': 50.00},
        {'order_date': dt.now(),
         'first_name': 'John', 'last_name': 'Smith', 'email': '<EMAIL>',
         'address': '7002 Mowatt Ln', 'city': 'San Francisco', 'state': 'CA', 'zipcode': '20000',
         'order_total': 50.00},
        {'order_date': dt(2024, 4, 30, 23, 0, 0),
         'first_name': 'Lucas', 'last_name': 'Gonzalez-Rey', 'email': 'lucasglezrey120@gmail.com',
         'address': '1101 Tenleytown St', 'city': 'Washington', 'state': 'DC', 'zipcode': '20016',
         'order_total': 50.00},
        {'order_date': dt(2024, 4, 1, 1, 0, 0),
         'first_name': 'John', 'last_name': 'Smith', 'email': '<EMAIL>',
         'address': '7002 Mowatt Ln', 'city': 'San Francisco', 'state': 'CA', 'zipcode': '94103',
         'order_total': 50.00},
        {'order_date': dt.now(),
         'first_name': 'Lucas', 'last_name': 'Gonzalez-Rey', 'email': 'lucasglezrey120@gmail.com',
         'address': '1101 Tenleytown St', 'city': 'Washington', 'state': 'DC', 'zipcode': '20016',
         'order_total': 50.00},
        {'order_date': dt.now(),
         'first_name': 'John', 'last_name': 'Smith', 'email': '<EMAIL>',
         'address': '7002 Mowatt Ln', 'city': 'San Francisco', 'state': 'CA', 'zipcode': '20000',
         'order_total': 50.00},
        {'order_date': dt(2024, 4, 30, 23, 0, 0),
         'first_name': 'Lucas', 'last_name': 'Gonzalez-Rey', 'email': 'lucasglezrey120@gmail.com',
         'address': '1101 Tenleytown St', 'city': 'Washington', 'state': 'DC', 'zipcode': '20016',
         'order_total': 50.00},
        {'order_date': dt(2024, 4, 1, 1, 0, 0),
         'first_name': 'John', 'last_name': 'Smith', 'email': '<EMAIL>',
         'address': '7002 Mowatt Ln', 'city': 'San Francisco', 'state': 'CA', 'zipcode': '94103',
         'order_total': 50.00},
        {'order_date': dt.now(),
         'first_name': 'Lucas', 'last_name': 'Gonzalez-Rey', 'email': 'lucasglezrey120@gmail.com',
         'address': '1101 Tenleytown St', 'city': 'Washington', 'state': 'DC', 'zipcode': '20016',
         'order_total': 50.00}
    ]

    # fake orderitems
    # Extended fake orderitems list
    orderitemlist = [
        {'order_id': 'ORD-1', 'product_code': 'polo-s-white', 'product_qty': 2},
        {'order_id': 'ORD-1', 'product_code': 'polo-m-white', 'product_qty': 1},
        {'order_id': 'ORD-2', 'product_code': 'polo-s-white', 'product_qty': 1},
        {'order_id': 'ORD-2', 'product_code': 'polo-l-red', 'product_qty': 3},
        {'order_id': 'ORD-3', 'product_code': 'polo-s-red', 'product_qty': 2},
        {'order_id': 'ORD-3', 'product_code': 'polo-xl-white', 'product_qty': 1},
        {'order_id': 'ORD-4', 'product_code': 'polo-xl-red', 'product_qty': 1},
        {'order_id': 'ORD-5', 'product_code': 'qzip-xs-white', 'product_qty': 4},
        {'order_id': 'ORD-6', 'product_code': 'qzip-xs-white', 'product_qty': 2},
        {'order_id': 'ORD-7', 'product_code': 'qzip-xs-white', 'product_qty': 1},
        {'order_id': 'ORD-8', 'product_code': 'qzip-xl-white', 'product_qty': 2},
        {'order_id': 'ORD-9', 'product_code': 'qzip-m-white', 'product_qty': 1},
        {'order_id': 'ORD-10', 'product_code': 'qzip-l-white', 'product_qty': 3},
        {'order_id': 'ORD-10', 'product_code': 'polo-xl-red', 'product_qty': 2},
        {'order_id': 'ORD-10', 'product_code': 'backpack-m-gray', 'product_qty': 1},
        {'order_id': 'ORD-10', 'product_code': 'hat-s-gray', 'product_qty': 1},
        {'order_id': 'ORD-10', 'product_code': 'hat-l-gray', 'product_qty': 1},
        {'order_id': 'ORD-10', 'product_code': 'polo-m-red', 'product_qty': 2},
        {'order_id': 'ORD-9', 'product_code': 'backpack-m-gray', 'product_qty': 2},
        {'order_id': 'ORD-5', 'product_code': 'backpack-m-gray', 'product_qty': 1},
        {'order_id': 'ORD-6', 'product_code': 'backpack-m-gray', 'product_qty': 2},
        {'order_id': 'ORD-7', 'product_code': 'polo-m-white', 'product_qty': 3},
        {'order_id': 'ORD-8', 'product_code': 'polo-l-white', 'product_qty': 2},
        {'order_id': 'ORD-9', 'product_code': 'polo-m-red', 'product_qty': 3},
        {'order_id': 'ORD-10', 'product_code': 'qzip-s-white', 'product_qty': 2}
    ]

    purchaselist = [
        {'product_code': 'qzip-s-white', 'purchase_price': 25, 'purchase_qty': 1,
         'purchase_date': dt(2024, 4, 1)},
        {'product_code': 'polo-s-red', 'purchase_price': 30, 'purchase_qty': 3,
         'purchase_date': dt.today().date()},
        {'product_code': 'polo-m-white', 'purchase_price': 45, 'purchase_qty': 2,
         'purchase_date': dt.today().date()},
        {'product_code': 'backpack-m-gray', 'purchase_price': 42, 'purchase_qty': 2, 'purchase_date': dt.today().date()},
        {'product_code': 'hat-m-gray', 'purchase_price': 50, 'purchase_qty': 3, 'purchase_date': dt(2024, 3, 28)},
        {'product_code': 'hat-s-gray', 'purchase_price': 55, 'purchase_qty': 1, 'purchase_date': dt(2024, 3, 31)},
        {'product_code': 'qzip-l-white', 'purchase_price': 28, 'purchase_qty': 4, 'purchase_date': dt(2024, 4, 1)},
        {'product_code': 'polo-l-red', 'purchase_price': 27, 'purchase_qty': 3,
         'purchase_date': dt(2024, 3, 30)},
        {'product_code': 'qzip-xl-white', 'purchase_price': 26, 'purchase_qty': 5,
         'purchase_date': dt.today().date()},
        {'product_code': 'qzip-xs-white', 'purchase_price': 29, 'purchase_qty': 2, 'purchase_date': dt(2024, 4, 2)},
        {'product_code': 'polo-m-white', 'purchase_price': 20, 'purchase_qty': 3, 'purchase_date': dt.today().date()},
        {'product_code': 'polo-l-white', 'purchase_price': 20, 'purchase_qty': 2, 'purchase_date': dt(2024, 3, 30)}
    ]
    #fake pricechange
    pricechangelist= [
        {'change_id': 1, 'item_id': 1, 'item_price':45.99, 'price_change': -3, 'new_price': 42.99, 'change_date': dt.today().date()}
    ]

    for each_mi in merchitemlist:
        an_mi = MerchItem(item_name=each_mi['item_name'], item_price=each_mi['item_price'],
                          item_class=each_mi['item_class'], long_desc=each_mi['long_desc'], manu_details=each_mi['manu_details'])
        print(f'{an_mi.item_name} inserted to db at ${an_mi.item_price}')
        db.session.add(an_mi)
        db.session.commit()

    # Adding products to Inventory Table
    for each_prod in inventorylist:
        a_prod = Inventory(item_id=each_prod['item_id'], product_code=each_prod['product_code'], product_stock=each_prod['product_stock'],
                           product_size=each_prod['product_size'], product_color=each_prod['product_color'], purchase_price=each_prod['purchase_price'], image_dir=each_prod['image_dir'])
        print(f'{a_prod.product_code} added to db')
        db.session.add(a_prod)
        db.session.commit()

    for each_user in users:
        print(f'{each_user["username"]} inserted into user')
        a_user = User(username=each_user["username"], password=each_user["password"], role=each_user["role"])
        db.session.add(a_user)
        db.session.commit()

    # Adding orders to Orders table
    for each_order in orderlist:
        an_ord = Order(order_date=each_order['order_date'], first_name=each_order['first_name'],
                       last_name=each_order['last_name'], email=each_order['email'], address=each_order['address'],
                       city=each_order['city'], state=each_order['state'], zipcode=each_order['zipcode'],
                       order_total=each_order['order_total'])  # default in progress status assigned
        print(f'{an_ord} added to db')
        db.session.add(an_ord)
        db.session.commit()

    # Adding orderitems to OrderItem table
    for each_oi in orderitemlist:
        an_oi = OrderItem(order_id=each_oi['order_id'], product_code=each_oi['product_code'], product_qty=each_oi['product_qty'],)
        db.session.add(an_oi)
        db.session.flush()

        # deferred item_price setting for safety
        if an_oi.inv_ref is not None:
            an_oi.item_price = an_oi.inv_ref.merchitem_ref.item_price
            an_oi.line_price = round(each_oi['product_qty'] * an_oi.item_price, 2)
        else:
            print(f"Inventory not found for product code {each_oi['product_code']}")
            an_oi.item_price = None


        print(f'{an_oi} at line price of ${an_oi.line_price} added to db')
        db.session.commit()

    for each_ip in purchaselist:
        an_ip = InvPurchase(product_code=each_ip['product_code'], purchase_price=each_ip['purchase_price'],
                            purchase_qty=each_ip['purchase_qty'], purchase_date=each_ip['purchase_date'])
        db.session.add(an_ip)
        print(f'{an_ip} added to db')
        db.session.commit()

    for each_pc in pricechangelist:
        an_pc= merchitem_pricechange( item_id=each_pc['item_id'],item_price=each_pc['item_price'],
                                     price_change=each_pc['price_change'], new_price=each_pc['new_price'], change_date=each_pc['change_date'])
        db.session.add(an_pc)
        print(f'{an_pc} added to db')
        db.session.commit()


'''code for the console to test CRUD
PRAGMA foreign_keys = ON;
PRAGMA foreign_key_list('Inventory');

SELECT inv.product_code, inv.product_stock, mi.item_price, oi.product_qty FROM OrderItem oi
INNER JOIN main.Inventory inv on oi.product_code = inv.product_code
INNER JOIN main.MerchItem mi on inv.item_id = mi.item_id;

SELECT * FROM MerchItem;
SELECT * FROM Inventory;

DELETE FROM MerchItem WHERE item_id = 2;
SELECT * FROM MerchItem;
SELECT * FROM Inventory;

PRAGMA table_info('OrderItem');
SELECT * FROM OrderItem;

SELECT * FROM "Order";
'''