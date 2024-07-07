import os
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import requests
from requests.auth import HTTPBasicAuth
from authorize import role_required
from models import *
from datetime import datetime as dt
from werkzeug.utils import secure_filename  # friendly filenames only
from werkzeug.security import check_password_hash, generate_password_hash
import yagmail
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import func


basedir = os.path.abspath(os.path.dirname(__file__))

# Database connection and flask application initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'beyond_course_scope'
app.config['TEMPLATES_AUTO_RELOAD'] = True
db.init_app(app)

app.config['MAX_QUANTITY_PER_ITEM'] = 99

# PayPal API and yagmail parameters
app.config['PAYPAL_API'] = 'https://api-m.sandbox.paypal.com/v2'
app.config['PAYPAL_CLIENT_ID'] = 'Ad61-PqFotabih1hJJW9T0SYmZnL_MkKU567XT_KEzTAooNOcUaNAWvg6czfThig3_bOODZI-7j3SyUb'
app.config['PAYPAL_SECRET'] = 'EHKStMJyYYA-T9-HNgrLMLs5wlyoT66761JCEhEChWfxRAbEPVW2WOUeY_etFWJei-1O89UcGaSi8Szn'


app.config['GMAIL_USER'] = 'umdclubbaseballteam@gmail.com'
app.config['GMAIL_APP_PASSWORD'] = 'qssu dqdj ejcj pnwi'


login_manager = LoginManager()
login_manager.login_view = 'login'  # default login route
login_manager.init_app(app)

# auto logout any users upon launch
# logout_user()


# login for manger to return user id
@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    return User.query.get(int(user_id.split('- ')[-1]))
    # the [-1] is b/c user_id was returning as '(admin - ADMIN - 2'
    # should also work even if user_id is '2'


#error handling for the 404 page
@app.errorhandler(404)
# inbuilt function which takes error as parameter
def not_found(e):
    # defining function
    return render_template("404.html")


#login route so the user is authenticated
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Determine where to redirect user if they are already logged in
        if current_user and current_user.is_authenticated:
            if current_user.role in ['ADMIN', 'MANAGER']:
                return redirect(url_for('report_rev'))
            else:
                return redirect(url_for('merch'))
        else:
            redirect_route = request.args.get('next')
            return render_template('sign-in.html', redirect_route=redirect_route)

    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        # Validate user credentials and redirect them to initial destination
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'You are now logged in as {username}!', 'success')
            # redirect admin to manage_products, redirect manager to inventory_status
            if user.role == 'ADMIN':
                return redirect(url_for('manage_products'))
            elif user.role == 'MANAGER':
                return redirect(url_for('inventory_status'))
            elif user.role == 'CUSTOMER':
                return redirect(url_for('merch'))
        else:
            flash(f'Your login information was not correct. Please try again.', 'error')
            return redirect(url_for('login'))

    return redirect(url_for('login'))


# logout for the admin and the manager
@app.route('/logout')
@login_required
@role_required(['ADMIN', 'MANAGER', 'CUSTOMER'])
def logout():
    logout_user()
    flash(f'You have been logged out.', 'success')
    return redirect(url_for('home'))


app.config['MAX_QUANTITY_PER_ITEM'] = 99

## PayPal API and yagmail parameters
app.config['PAYPAL_API'] = 'https://api-m.sandbox.paypal.com/v2'
app.config['PAYPAL_CLIENT_ID'] = 'Ad61-PqFotabih1hJJW9T0SYmZnL_MkKU567XT_KEzTAooNOcUaNAWvg6czfThig3_bOODZI-7j3SyUb'
app.config['PAYPAL_SECRET'] = 'EHKStMJyYYA-T9-HNgrLMLs5wlyoT66761JCEhEChWfxRAbEPVW2WOUeY_etFWJei-1O89UcGaSi8Szn'


app.config['GMAIL_USER'] = 'umdclubbaseballteam@gmail.com'
app.config['GMAIL_APP_PASSWORD'] = 'qssu dqdj ejcj pnwi'

login_manager = LoginManager()
login_manager.login_view = 'login' # default login route
login_manager.init_app(app)

#query to load manager into the database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.errorhandler(404)
# inbuilt function which takes error as parameter
def not_found(e):
    # defining function
    return render_template("404.html")


#rendering the route for the home page
@app.route('/')
def home():
    return render_template('homepage.html')


#pulling in base html to render as a template
@app.route('/test-base')  # base template as a route
def test():
    return render_template('base.html')


#creating a test report for the base html page
@app.route('/test-report')
def test_report():
    return render_template('base-report.html')


#creating merch route ot showcase all of the products
@app.route('/merch')
def merch():
    # grab all the merch items and inventories from the db
    merchitems = MerchItem.query.order_by(MerchItem.item_name).all()
    inventories = Inventory.query.all()
    # pass on all merchandise and all inventories (for images, colors, and sizes)
    return render_template('merch.html', merchitems=merchitems, inventories=inventories)


#merch item
@app.route('/merch-view/<int:item_id>')
def merch_item(item_id):  # url_id refers to the suffix (equivalent to db column item_url_id)
    # retrieve the merchandise item based on the item_url_id
    merchitem = MerchItem.query.filter_by(item_id=item_id).first()
    print(f'Type of merch item {merchitem}')

    if merchitem:
        # get all inventory items associated with the given merch item
        inventories = Inventory.query.filter_by(item_id=item_id).all()
        print(f'Type of inventories {inventories}')
        # pass on merchandise and associated inventories
        return render_template('merch-item.html', merchitem=merchitem, inventories=inventories)
    else:
        flash('Item not found, redirected to all items')
        return redirect(url_for('merch'))


# capture payment gets order details from paypal api
@app.route("/payments/<orderId>/capture", methods=["POST"])
def capture_payment(orderId):  # Checks and confirms payment
    captured_payment = approve_payment(orderId)

    if captured_payment['status'] == 'COMPLETED':
        first_name = captured_payment['payment_source']['paypal']['name']['given_name']
        last_name = captured_payment['payment_source']['paypal']['name']['surname']
        email = captured_payment['payment_source']['paypal']['email_address']
        session['paypal_email'] = email
        address = captured_payment['purchase_units'][0]['shipping']['address']['address_line_1']
        city = captured_payment['purchase_units'][0]['shipping']['address']['admin_area_2']
        state = captured_payment['purchase_units'][0]['shipping']['address']['admin_area_1']
        zip = captured_payment['purchase_units'][0]['shipping']['address']['postal_code']
        if current_user and current_user.is_authenticated:
            if current_user.role == 'CUSTOMER' and current_user.user_id:
                customerid = current_user.user_id
        else:
            customerid = None
        # populate order and orderitem(s)
        an_ord = Order(order_date=dt.today(), user_id=customerid, first_name=first_name,
                       last_name=last_name, email=email,
                       address=address, city=city,
                       state=state, zipcode=zip,
                       order_total=round(session['cart_total'], 2))
        print(f'{an_ord} added to db')
        current_order_id = an_ord.order_id
        current_email = an_ord.email
        db.session.add(an_ord)
        db.session.flush()
        db.session.commit()

        for each_oi in session['cart']:
            an_oi = OrderItem(order_id=current_order_id, product_code=each_oi['product_code'],
                              product_qty=each_oi['product_quantity'])
            an_oi.item_price = each_oi['product_price']
            an_oi.line_price = each_oi['product_price']*each_oi['product_quantity']
            db.session.add(an_oi)
            db.session.commit()

        send_basic_email(current_order_id, current_email, an_ord)

        if 'cart' in session:
            clear_cart()

    return jsonify(captured_payment)

# helper method for capture_payment to send an email
# takes in recipient email and order as input
def send_basic_email(current_order_id, current_email, an_ord):
    user = app.config['GMAIL_USER']
    app_password = app.config['GMAIL_APP_PASSWORD']
    to = current_email
    order_items = (db.session.query(
        MerchItem.item_name.label('item_name'), Inventory.product_size.label('product_size'),
        Inventory.product_color.label('product_color'), OrderItem.product_qty.label('product_qty'),
        OrderItem.item_price.label('item_price'), OrderItem.line_price.label('line_price'))
                   .select_from(OrderItem)
                   .join(Inventory, OrderItem.product_code == Inventory.product_code)
                   .join(MerchItem, Inventory.item_id == MerchItem.item_id)
                   .filter(OrderItem.order_id == current_order_id)
                   .all())
    # test email to test
    # to = 'your_real_email@gmail'
    subject = "Order confirmation from Club Baseball"

    # Send email confirmation automatically upon successful payment capture
    html_content = render_template('order-confirmation-email.html', latest_order=an_ord, order_items=order_items)
    try:
        with yagmail.SMTP(user, app_password) as yag:
            print(f'paypal sent')
            yag.send(to, subject, html_content)
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")


# paypal api approve_payment
def approve_payment(orderId):
    api_link = f"{app.config['PAYPAL_API']}/checkout/orders/{orderId}/capture"
    client_id = app.config['PAYPAL_CLIENT_ID']
    secret = app.config['PAYPAL_SECRET']
    basic_auth = HTTPBasicAuth(client_id, secret)
    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(url=api_link, headers=headers, auth=basic_auth)
    response.raise_for_status()
    json_data = response.json()
    return json_data


# connects capture payment to order confirmation
@app.route('/process-order/')
def process_order():
    latest_order = Order.query.order_by(Order.order_date.desc()).first()
    order_items = (db.session.query(
        MerchItem.item_name.label('item_name'), Inventory.product_size.label('product_size'),
        Inventory.product_color.label('product_color'), OrderItem.product_qty.label('product_qty'),
        OrderItem.item_price.label('item_price'), OrderItem.line_price.label('line_price'))
                   .select_from(OrderItem)
                   .join(Inventory, OrderItem.product_code == Inventory.product_code)
                   .join(MerchItem, Inventory.item_id == MerchItem.item_id)
                   .filter(OrderItem.order_id == latest_order.order_id)
                   .all())
    print(order_items)
    print('will render order-confirmation')
    return render_template('order-confirmation.html', latest_order=latest_order, order_items=order_items)


# the html template that is the payload for email
@app.route('/order-confirmation-email.html')
def order_confirmation_email():
    latest_order = Order.query.order_by(Order.order_date.desc()).first()
    order_items = (db.session.query(
        MerchItem.item_name.label('item_name'), Inventory.product_size.label('product_size'),
        Inventory.product_color.label('product_color'), OrderItem.product_qty.label('product_qty'),
        OrderItem.item_price.label('item_price'), OrderItem.line_price.label('line_price'))
                   .select_from(OrderItem)
                   .join(Inventory, OrderItem.product_code == Inventory.product_code)
                   .join(MerchItem, Inventory.item_id == MerchItem.item_id)
                   .filter(OrderItem.order_id == latest_order.order_id)
                   .all())
    print(order_items)
    paypal_email = session.get('paypal_email', '')
    print('will render order-confirmation-email')
    return render_template('order-confirmation-email.html',
                           latest_order=latest_order, order_items=order_items, default_email=paypal_email)


# dynamic cart w/ session management
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'cart' in session:
        if request.method == 'POST':
            # email = request.form.get('email')
            db.session.commit()
            flash(f'Email was successfully updated!', 'success')
        return render_template('cart.html', products=session['cart'], cart_count=len(session['cart']),
                               cart_total=round(session['cart_total'], 2), cart_sum=session['cart_sum'],
                               cart_shipping=session['cart_shipping'])
    else:
        return render_template('cart.html', cart_count=0)


# basic cart add w/ session management and db connection
@app.route('/cart/add/<int:item_id>', methods=['GET', 'POST'])
def cart_add(item_id):
    print("added to cart")
    merch_item = MerchItem.query.filter_by(item_id=item_id).first()
    # item_id = request.args.get('item_id')  # Get item_id from args
    size_selection = request.args.get('size_selection')
    print(size_selection)
    product_quantity = int(request.args.get('product_quantity'))
    color_selection = request.args.get('color_selection')

    if merch_item:
        inventory_item = Inventory.query.filter_by(item_id=item_id, product_size=size_selection, product_color=color_selection).first()
        print("Item found! ID:", item_id)
        if 'cart' not in session:
            session['cart'] = []
        found_item = next((item for item in session['cart'] if ((item['item_id'] == item_id) & (item['product_size'] == size_selection))), None)
        # found_item = None
        if found_item:
            found_item['product_quantity'] += product_quantity
            print(product_quantity)
            if found_item['product_quantity'] > app.config['MAX_QUANTITY_PER_ITEM']:
                found_item['product_quantity'] = app.config['MAX_QUANTITY_PER_ITEM']
                flash(f"You cannot exceed more than {app.config['MAX_QUANTITY_PER_ITEM']} of the same item.")
        else:
            if product_quantity > app.config['MAX_QUANTITY_PER_ITEM']:
                session['cart'].append(
                    {'item_id': merch_item.item_id, 'product_name': merch_item.item_name,
                     'product_quantity': 99, 'product_image': inventory_item.image_dir,
                     'product_price': merch_item.item_price, 'product_size': size_selection,
                     'product_code': inventory_item.product_code})
            else:
            # Access attributes from the retrieved item object
                session['cart'].append(
                {'item_id': merch_item.item_id, 'product_name': merch_item.item_name,
                 'product_quantity': product_quantity, 'product_image': inventory_item.image_dir,
                 'product_price': merch_item.item_price, 'product_size': size_selection,
                 'product_code': inventory_item.product_code}
                )
        session['cart_sum'] = sum(item['product_price'] * item['product_quantity'] for item in session['cart'])
        session['cart_shipping'] = 0.06 * session['cart_sum']
        session['cart_total'] = session['cart_sum'] + session['cart_shipping']
        print(session['cart'])
        flash(f"{merch_item.item_name} has been successfully added to your cart.", 'success')
        return redirect(url_for('cart'))  # Assuming 'cart_view' is the route for the cart page
    else:
        flash(f'Item could not be found. Please contact support if this problem persists.', 'error')
        return redirect(url_for('merch'))  # Assuming 'merch' is the route for all merchandise items


# cart update w/ session management
@app.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    new_quantity = int(request.args.get('quantity'))

    if 'cart' in session:
        for item in session['cart']:
            if item['item_id'] == product_id:
                item['product_quantity'] = new_quantity
                break

        # Recalculate cart sum, shipping, and total
        session['cart_sum'] = sum(item['product_price'] * item['product_quantity'] for item in session['cart'])
        session['cart_shipping'] = 0.06 * session['cart_sum']
        session['cart_total'] = session['cart_sum'] + session['cart_shipping']

        flash('Cart updated successfully!', 'success')
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Cart not found in session'}), 404


# clear cart session
@app.route('/cart/clear')
def clear_cart():
    if 'cart' in session:
        del(session['cart'])
        flash(f"Cart Cleared", 'success')
    else:
        flash(f"Cart already empty", 'error')
    return redirect(url_for('home'))


# remove single item with session management
@app.route('/cart/remove/<int:index>', methods=['GET'])
def cart_remove(index):
    if 'cart' in session:
        if index < len(session['cart']):
            product_name = session['cart'][index]['product_name']
            session['cart'].pop(index)
            flash(f"{product_name} has been successfully removed from your cart.", 'success')

        else:
            flash(f'Product is not in the cart and could not be removed.', 'error')

    session['cart_sum'] = sum(item['product_price'] * item['product_quantity'] for item in session['cart'])
    session['cart_shipping'] = 0.06 * session['cart_sum']
    session['cart_total'] = session['cart_sum'] + session['cart_shipping']

    return redirect(url_for('cart'))


# attempt at webscraping the order confirmation html to put in an email
@app.route("/send_confirmation", methods=["POST"])
# separate method to not load a new template upon sending email confirmation
def send_confirmation():
    email = request.form.get("email")

    # Paypal login credentials
    user = "sb-dhrn330632828@personal.example.com"
    app_password = "aB990|q/"
    subject = "Order confirmation from Club Baseball"

    # Capture HTML content from specific div
    html_content = request.form["htmlContent"]
    soup = BeautifulSoup(html_content, "lxml")
    container_div = soup.find("div", id="email_send_id")

    if container_div:
        extracted_html = str(container_div)
        try:
            with yagmail.SMTP(user, app_password) as yag:
                yag.send(email, subject, extracted_html)
            return "Confirmation email sent!"
        except Exception as e:
            return f"An error occurred while sending the email: {e}"
    else:
        return "An error occurred: Container div not found."


# Sales table route that queries required fields to make the table
@app.route('/sales-table')
@login_required
@role_required(['ADMIN', 'MANAGER'])
def sales_table():
    import datetime as local_dt
    # Execute SQLAlchemy query to fetch sales data
    sales_data = db.session.query(
        Order.order_id.label('order_id'),
        OrderItem.product_code.label('product_code'),
        Order.first_name.label('first_name'),
        Order.last_name.label('last_name'),
        Order.email.label('email'),
        Order.order_date.label('order_date'),
        OrderItem.product_qty.label('product_qty'),
        (OrderItem.item_price * OrderItem.product_qty).label('total_revenue')
    ).join(OrderItem).join(Inventory).all()

    # Rev by month query
    qry_rev_by_month = db.session.query(
        func.strftime('%Y-%m', Order.order_date).label('order_month'),
        func.sum(OrderItem.item_price * OrderItem.product_qty).label('total_rev')
    ) \
        .join(OrderItem, Order.order_id == OrderItem.order_id) \
        .group_by('order_month') \
        .order_by('order_month') \
        .all()

    # Orders in past 30 days query

    qry_orders_past_30 = db.session.query(
        func.count(Order.order_id).label("order_count")
    ) \
    .filter(Order.order_id >= dt.now() - local_dt.timedelta(days=30)) \
    .all()

    # Put orders in past 30 days query into a dataframe

    df_orders_past_30 = pd.DataFrame(qry_orders_past_30, columns=['order_count'])

    # Make a pie chart for orders in past 30 days

    orders_past_30_figure = px.pie(df_orders_past_30, names='order_count', values='order_count', title='Number of Orders in Past 30 Days',
            color_discrete_sequence=['#3366CC'])
    orders_past_30_figure.update_traces(textposition='inside', textinfo='label', hovertemplate=None, hoverinfo='none', textfont_size=30, showlegend=False)
    orders_past_30_figure.update_layout(
        title={'x': 0.5}
    )
    orders_past_30_figureJSON = orders_past_30_figure.to_json()

    # Put revenue by month query into df
    df_rev_by_month = pd.DataFrame(qry_rev_by_month, columns=['order_month', 'total_rev'])

    rev_by_month_figure = px.line(df_rev_by_month, x='order_month', y='total_rev', title = 'Revenue by Month', markers=True,
                                  color_discrete_sequence=px.colors.qualitative.Antique,
                                  labels={'order_month': '', 'total_rev': 'Total Revenue'})
    rev_by_month_figure.update_layout(
        title={'x': 0.5}
    )

    rev_by_month_figureJSON = rev_by_month_figure.to_json()


    # Pass data to template
    return render_template('sales-table.html', sales_data=sales_data, rev_by_month_graph = rev_by_month_figureJSON, orders_past_30_graph = orders_past_30_figureJSON)



@app.route('/inventory-status')
@login_required
@role_required(['ADMIN', 'MANAGER'])
def inventory_status():
    inventories = Inventory.query.all()
    # Query the database to get inventory information
    qry_inventory = db.session.query(
        Inventory.product_code, Inventory.item_id, Inventory.product_stock, Inventory.purchase_price
    ).all()

    # descriptive inventory w/ the item name
    desc_inv = db.session.query(
        Inventory.product_id, Inventory.product_code, MerchItem.item_name,  Inventory.product_size, Inventory.product_color,
        Inventory.purchase_price, Inventory.product_stock).join(MerchItem, Inventory.item_id == MerchItem.item_id)
    # Execute the query and fetch all results
    custom_inventories = desc_inv.all()

    # Convert results into a pandas dataframe
    columns = [
        'product_id', 'product_code', 'item_name', 'product_size', 'product_color', 'purchase_price', 'product_stock']
    inv_df = pd.DataFrame(custom_inventories, columns=columns)
    # elementary labels -> product code, group labels -> item name
    labs = inv_df["product_code"].tolist() + inv_df["item_name"].unique().tolist()
    # intermediate parents -> item name, root parents -> empty string
    pars = inv_df["item_name"].tolist() + ["" for i in range(len(inv_df["item_name"].unique()))]
    # find stock by item_name
    cat_sums = inv_df.groupby("item_name")["product_stock"].sum().reset_index()
    vals = inv_df["product_stock"].tolist() + cat_sums["product_stock"].tolist()
    # add zero as sums for roots
    vals += [0 for _ in range(len(inv_df["item_name"].unique()) - len(cat_sums))]

    fig = go.Figure(go.Treemap(labels=labs, parents=pars, values=vals))
    fig.update_layout(
        title={'text': 'Current Inventory Levels', 'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'}
    )

    fig_json = fig.to_html(full_html=False)

    # Convert the query result into a DataFrame for data processing
    df_inventory = pd.DataFrame(qry_inventory)

    # Create a pie chart showing inventory amounts
    inventory_figure = px.pie(df_inventory, names='product_code', values='product_stock', title='Inventory Status')
    inventory_figure.update_layout(
        title={'text': 'Proportional Inventory Status', 'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'}
    )

    # Convert the Plotly figure to JSON for rendering in HTML
    inventory_figure_json = inventory_figure.to_json()
    # Render the HTML template with the inventory pie chart
    return render_template('inventory-status.html', inventory_tree=fig_json, inventory_pie_graph=inventory_figure_json,
                           inventories=custom_inventories, role=current_user.role)


# inventory status pie chart helper method
def inventory_status_pie():
   inventories = Inventory.query.all()
   # Query the database to get inventory information
   qry_inventory = db.session.query(
       Inventory.product_code,
       Inventory.product_stock,
       Inventory.purchase_price
   ).all()

   # Convert the query result into a DataFrame for data processing
   df_inventory = pd.DataFrame(qry_inventory)

   # Create a pie chart showing inventory amounts
   inventory_figure = px.pie(df_inventory, names='product_code', values='product_stock', title='Inventory Status')

   # Convert the Plotly figure to JSON for rendering in HTML
   inventory_figure_json = inventory_figure.to_json()

   # Render the HTML template with the inventory pie chart
   return render_template('inventory-status.html', inventory_pie_graph=inventory_figure_json,
                          inventories=inventories)


# line graph for monthly profits, revenues, and expenses
@app.route('/profit-summary')
@login_required
@role_required(['ADMIN', 'MANAGER'])
def profit_summary():

    # Query to show monthly profit for the graph
    qry_monthly_revenue = db.session.query(
        func.strftime('%Y-%m', Order.order_date).label('month'),
        func.sum(OrderItem.line_price).label('revenue'),
    ).outerjoin(Order, OrderItem.order_id == Order.order_id)\
    .group_by('month')\
    .order_by('month')\
    .all()

    qry_monthly_expenses = db.session.query(
        func.strftime('%Y-%m', InvPurchase.purchase_date).label('month'),
        func.sum(InvPurchase.purchase_price).label('expenses'),
    ).group_by('month')\
    .order_by('month')\
    .all()

    print(qry_monthly_revenue)
    print(qry_monthly_expenses)
    # Combine both queries to feed into the profit-summary table

    df_monthly_rev = pd.DataFrame(qry_monthly_revenue, columns=['month', 'revenue'])
    df_monthly_exp = pd.DataFrame(qry_monthly_expenses, columns=['month', 'expenses'])
    merged_df = pd.merge(df_monthly_rev, df_monthly_exp, on='month', how = 'outer')
    merged_df.fillna(0, inplace=True)
    merged_df['profit'] = merged_df['revenue'] - merged_df['expenses']

    # put the dataframe into a list of dictionaries to loop through for the profit-summary table
    merged_data = merged_df.to_dict('records')

    print(merged_df)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merged_df['month'], y=merged_df['revenue'], mode='lines', name='Revenue'))
    fig.add_trace(go.Scatter(x=merged_df['month'], y=merged_df['expenses'], mode='lines', name='Expenses'))
    fig.add_trace(go.Scatter(x=merged_df['month'], y=merged_df['revenue'] - merged_df['expenses'], mode='lines', name='Profit'))

    fig.update_layout(
        title='Profit, Revenue, and Expenses Over Time',
        xaxis_title='Month',
        yaxis_title='Amount',
        legend_title='Category',
        title_x=0.5
    )

    profit_exp_rev_by_month_figureJSON = fig.to_json()

    return render_template('profit-summary.html', merged_data = merged_data, profit_exp_rev_by_month_graph = profit_exp_rev_by_month_figureJSON)


# query merch items for product manage page
@app.route('/product/manage')
@login_required
@role_required(['ADMIN', 'MANAGER'])
def manage_products():
    merch_items = MerchItem.query.all()
    print(merch_items)
    return render_template('manage-products.html', MerchItems=merch_items)


# add a merchitem
# let managers do this b/c they need to create merchitem when they purchase new inventory
@app.route('/product/create', methods=['GET', 'POST'])
@login_required
@role_required(['ADMIN', 'MANAGER'])
def product_creation():
    if request.method == 'GET':
        merch_item = MerchItem.query.order_by(MerchItem.item_id).all()
        inventories = Inventory.query.all()
        return render_template('product-entry.html', action='create')
    elif request.method == 'POST':
        item_name = request.form['item_name']
        item_price = request.form['item_price']
        item_class = request.form['item_class']
        long_desc = request.form['long_desc']
        manu_details = request.form['manu_details']

        merchitem = MerchItem(item_name=item_name, item_price=item_price, item_class=item_class,
                              long_desc=long_desc, manu_details=manu_details)
        db.session.add(merchitem)
        db.session.commit()
        print(f'{item_name} inserted to db at ${item_price}')
        flash(f'{item_name} was successfully added!', 'success')
        return redirect(url_for('manage_products'))

    # Address issue where unsupported HTTP request method is attempted
    flash(f'Invalid request. Please contact support if this problem persists.', 'error')
    return redirect(url_for('manage_products'))


# modify a merchitem (incl price -> pricechange db)
@app.route('/product/update/<int:item_id>', methods=['GET', 'POST'])
@login_required
@role_required('ADMIN')
def product_edit(item_id):
    merch_item = MerchItem.query.filter_by(item_id=item_id).first()
    if request.method == 'GET':
        if merch_item:
            return render_template('product-entry.html', merch_item=merch_item, action='update')
        else:
            print(f'merchitem with id {item_id} does not exist')
            flash(f'Merchitem {item_id} does not exist, redirecting to Merchandise Create', 'error')
            return render_template('product-entry.html')

    elif request.method == 'POST':
        print('posting')
        merchitem = MerchItem.query.filter_by(item_id=item_id).first()
        # placeholder for merchitem info
        item_name = request.form['item_name']
        item_price = float(request.form['item_price'])
        old_price = float(merchitem.item_price)
        item_class = request.form['item_class']
        long_desc = request.form['long_desc']
        manu_details = request.form['manu_details']
        if merchitem:
            print(f'merchitem {merchitem.item_id} found')
            form_new_price = item_price
            print(f'form_new_price: {form_new_price} old_price: {old_price}')
            difference=form_new_price - old_price
            if form_new_price != old_price:
                price_change = merchitem_pricechange(
                    item_id=merchitem.item_id,
                    item_price=old_price,
                    new_price=form_new_price,
                    price_change=difference,
                    change_date=dt.now()
                )
                print(f'price change {price_change} entered')
                db.session.add(price_change)

            merchitem.item_name = item_name
            merchitem.item_price = item_price
            merchitem.item_class = item_class
            merchitem.long_desc = long_desc
            merchitem.manu_details = manu_details

    db.session.commit()
    print(f'merchitem {merch_item.item_name} updated')
    flash(f'{merch_item.item_name} was successfully updated!', 'success')
    return redirect(url_for('manage_products'))

    # Address issue where unsupported HTTP request method is attempted
    print('error')

    flash(f'Invalid request. Please contact support if this problem persists.', 'error')
    return redirect(url_for('manage_products'))


# delete a merchitem
@app.route('/product/delete/<int:item_id>')
@login_required
@role_required(['ADMIN'])
def product_delete(item_id):
    # merchandise item query for the delete
    mi = MerchItem.query.get_or_404(item_id)
    print(f'Product {mi.item_name} found')
    if merch_item:
        flash(f'{mi.item_name} was successfully deleted!', 'success')
        db.session.delete(mi)
        db.session.commit()

    else:
        print(f'Deletion failed. Merchitem {mi.item_name} could not be found.')
        flash(f'Delete failed! Product could not be found.', 'error')

    return redirect(url_for('manage_products'))


# helper method to get the inventory item
@app.route('/get-inv-info', methods=['GET'])
@login_required
def get_inv_info():
    # cross reference input with all results
    checklist = db.session.query(
        Inventory.product_id, Inventory.product_code, MerchItem.item_name, Inventory.product_size,
        Inventory.product_color,
        Inventory.purchase_price, Inventory.product_stock).join(MerchItem, Inventory.item_id == MerchItem.item_id)
    # product_code user input
    product_code = request.args.get('product_code')
    # Execute the query and fetch the matching result
    match = checklist.filter(Inventory.product_code == product_code).first()
    # invitem = Inventory.query.filter_by(product_code=product_code).first()
    # parent_merchitem = MerchItem.query.filter_by(item_id=invitem.item_id).first()

    # if purchasing existing inventory (found in database), prefill the other fields
    if match:
        print(f'Inventory {product_code} found')
        return jsonify({
            'item_name': match.item_name,
            'product_size': match.product_size,
            'product_color': match.product_color,
            'unit_price': match.purchase_price,
            'product_stock': match.product_stock
        })
    # if purchasing new inventory (not found in database), leave fields blank
    else:
        print(f'Inventory {product_code} not found')
        return jsonify({})


# app.config['PROD_IMG'] = 'static/images/products'  # save images to local image folder
app.config['PROD_IMG'] = '/home/team02spring2024bmgt407/team02spring2024bmgt407/static/images/products' # save images to python anywhere folder


# make a new route that covers both adding new inventories and updating existing inventories
# business context: inventory purchase form (of new and existing inventories)
@app.route('/inventory-purchase', methods=['GET', 'POST'])
@login_required
def inventory_purchase():
    if request.method == 'GET':
        item_names = MerchItem.query.distinct(MerchItem.item_name).all()
        print(item_names)
        return render_template('order-entry.html', item_names=item_names)
    elif request.method == 'POST':
        # grab form items
        data = request.form
        productcode = data.get("product_code")
        # get item id through the item name pased
        item_name = data.get("item_search")
        MI = MerchItem.query.filter_by(item_name=item_name).first()
        item_id = MI.item_id

        form_size = data.get("product_size")
        form_color = data.get("product_color")
        form_qty = int(data.get("purchase_qty"))
        form_price = float(data.get("unit_price"))

        invitem = Inventory.query.filter_by(product_code=productcode).first()
        # found product_code and update existing inventory
        if invitem:
            invitem.purchase_price = form_price
            invitem.product_stock += form_qty
            print(f'{form_qty}x product {productcode} purchased')
        # didn't find product_code and create a new inventory
        else:
            new_invitem = Inventory(
                product_code=productcode,
                item_id=item_id,
                product_size=form_size,
                product_color=form_color,
                purchase_price=form_price,
                product_stock=form_qty,
                # temporarily make image directory None
                image_dir=None
            )
            db.session.add(new_invitem)
            print(f'{form_qty}x new product {productcode} purchased')

            # handle image
            file_objs = request.files.getlist('image_dir')
            for file_obj in file_objs:
                if file_obj and file_obj.filename != '':
                    try:
                        # name to get stored in db
                        filename = secure_filename(file_obj.filename)
                        filepath = os.path.join(app.config['PROD_IMG'], filename)
                        if not os.path.exists(filepath):
                            file_obj.save(filepath)
                            new_invitem.image_dir = filename  # Update image path in object
                        else:
                            print(f'Skipping upload: {filename} already exists.')
                            new_invitem.image_dir = filename  # still set filename to itself
                    except Exception as e:
                        flash(f'Error saving image: {e}', 'error')
                        new_invitem.image_dir = 'Subject.png' #default image
                else: new_invitem.image_dir = 'Subject.png' #default image

        # loading inventory purchase into a dataframe
        new_ip = InvPurchase(
            product_code=productcode, purchase_date=dt.today(),
            purchase_price=form_price*form_qty, purchase_qty=form_qty,
        )
        db.session.add(new_ip)
        print(f'Purchase {new_ip.purchase_id} successfully entered')
        # commit all db changes
        db.session.commit()
        print('Going back to inventory')
        # go back to inventory table
        return redirect(url_for('inventory_status'))


# delete is separate as it is just tied to a button
@app.route('/inventory-status/delete/<int:product_id>')
@login_required
@role_required('ADMIN')
def inventory_delete(product_id):
    inventory = Inventory.query.filter_by(product_id=product_id).first()
    print(product_id)
    if inventory:
        if inventory.image_dir:
            os.remove(os.path.join(app.config['PROD_IMG'], inventory.image_dir))  # delete the saved image
        db.session.delete(inventory)
        db.session.commit()
        flash(f'{product_id} was successfully deleted!', 'success')
    else:
        flash(f'Delete failed! Student could not be found.', 'error')

    return redirect(url_for('inventory_status'))


#creating a new route for inventory levels and connecting it to start date on the form
@app.route('/inventory-history', methods=["POST"])
def inventory_history():
    #query to get the invetory product code to connect to the other database
    if request.method == 'POST':
        start_date = request.form['start_date']
        start_date = dt.strptime(start_date, '%Y-%m-%d')
        results = (db.session.query(
            Inventory.product_code, Inventory.product_stock.label('today\'s inventory level'),
            func.sum(InvPurchase.purchase_qty).label('from supplier'),
            func.sum(OrderItem.product_qty).label('to customers'))
                   .select_from(Inventory)
                   .join(OrderItem, Inventory.product_code == OrderItem.product_code)
                   .join(Order, OrderItem.order_id == Order.order_id)
                   .outerjoin(InvPurchase, Inventory.product_code == InvPurchase.product_code)
                   .join(MerchItem, Inventory.item_id == MerchItem.item_id)
                   .filter(Order.order_date >= start_date, InvPurchase.purchase_date >= start_date)
                   .group_by(Inventory.product_code).all())

        # converting results intp pd dataframe
        df_inventory_level = pd.DataFrame(results, columns=["product_code", "inv level today", "inflow from supplier", "outflow to customer"])
        # creating calculated field for current inventory level
        df_inventory_level['historic inventory level'] = df_inventory_level['inv level today'] + df_inventory_level['outflow to customer'] - df_inventory_level['inflow from supplier']
        pd.set_option('display.max_rows', None)  # or use a specific large number if None is too much
        pd.set_option('display.max_columns', None)  # Show all columns
        pd.set_option('display.width', None)  # Automatically detect the display width
        pd.set_option('display.max_colwidth', None)
        print(df_inventory_level)
        # making visualization
        bar_trace = go.Bar(
            x=df_inventory_level['product_code'],
            y=df_inventory_level['historic inventory level'],
            marker_color=px.colors.qualitative.Antique,
            name='Historic Inventory Level'
        )
        layout = go.Layout(
            title=f'Inventory Level as of {start_date}',
            xaxis=dict(title='Product Code'),
            yaxis=dict(title='Historic Inventory Level'),
            bargap=0.3,  # Gap between bars
            bargroupgap=0.1  # Gap between groups of bars
        )
        fig = go.Figure(data=[bar_trace], layout=layout)
        # load figure payload
        fig_html = fig.to_html(full_html=False)

        return render_template( 'report-inv.html', results=results, inventory_level_figure=fig_html)


# created a price change route
@app.route('/price-change')
@login_required
@role_required('ADMIN')
def price_change_value():
    changes_table = (db.session.query(merchitem_pricechange.change_id, merchitem_pricechange.change_date,
                                      MerchItem.item_name, merchitem_pricechange.item_price,
                                      merchitem_pricechange.new_price, merchitem_pricechange.price_change)
                     .select_from(merchitem_pricechange)
                     .join(MerchItem, merchitem_pricechange.item_id == MerchItem.item_id).all())
    return render_template('price-change.html', table=changes_table)


# registration page for new customers
@app.route('/customer-registration', methods=['GET','POST'])
def customer_registration():
    if request.method == 'GET':
        return render_template('customer-registration.html')

    elif request.method == 'POST':
        # Gather information from the form
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        # Check if user put in matching passwords
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', category='error')
            return render_template('customer-registration.html')
        # If they did put matching passwords then hash the password and enter it to database
        else:
            hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password = hashed_pw, role='CUSTOMER')
            db.session.add(new_user)
            db.session.commit()
            flash('Your account has been registered! You can now log in.', category = 'success')
            return redirect (url_for('login'))

    return render_template('customer-registration.html')


# order history table for existing customers
@app.route('/order-history')
@login_required
@role_required('CUSTOMER')
def order_history():
    if current_user and current_user.is_authenticated:
        if current_user.user_id:
            customerid = current_user.user_id
            ordhist = db.session.query(
                Order.order_date.label('order_date'),
                Order.first_name.label('first_name'),
                Order.last_name.label('last_name'),
                Order.email.label('email'),
                Order.order_total.label('order_total')
            ).filter(Order.user_id == customerid).all()
            if ordhist:
                return render_template('order-history.html', orders=ordhist)
            else:
                flash('You have no previous orders')
                return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
