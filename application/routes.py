from datetime import datetime
from jinja2 import pass_eval_context
from loguru import logger
from pyqiwip2p import QiwiP2P
import requests
import config
import random


from application.UserLogin import UserLogin as uslg
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from application import *

@app.route("/")
def index():
    try:
        with app.app_context():
            db.create_all()

        user = models.getUser(current_user.get_id())["username"]
        return render_template("index.html", username=user, elements=models.GetItems(), user_id=current_user.get_id())
    except Exception as ex: return str(ex)

@login_manager.user_loader
def load_user(user_id):
    return uslg().from_db(user_id)

@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        if request.method == "POST":
            username = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            confirmPassword = request.form.get("confirmPassword")


            if password == confirmPassword:

                user = models.getUserByUsername(username)
                user2 = models.getUserByEmail(email)



                if user["username"] == False and user2["username"] == False:
                    user = models.Users(username=username, password=password, email=email, ip=request.remote_addr)
                    db.session.add(user)
                    db.session.commit()

                    user = models.getUserByUsername(username)

                    userLogin = uslg().create(user)
                    login_user(userLogin)
                    user = models.getUser(current_user.get_id())["username"]
                    return render_template("index.html", username=user)
                else:
                    flash("error")
                    user = models.getUser(current_user.get_id())["username"]
                    return render_template("register.html", username=user)

            else:
                flash("error")
                user = models.getUser(current_user.get_id())["username"]
                return render_template("register.html", username=user)


        user = models.getUser(current_user.get_id())["username"]
        return render_template("register.html", username=user)
    except: return "404"

@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":


            username = request.form.get("name")
            password = request.form.get("name1")


            user = models.getUserByUsername(username)

            usernamee = user["username"]

            if usernamee == False:
                flash("error")
                return  render_template("login.html")

            else:

                if user["password"] == password:

                    userLogin = uslg().create(user)
                    login_user(userLogin)

                    return redirect(url_for('index'))

                else:
                    flash("error")
                    return render_template("login.html")



        user = models.getUser(current_user.get_id())["username"]
        return render_template("login.html", username=user)
    except: return "404"

@app.route("/profile/<string:user_id>", methods=["GET", "POST"])
@login_required
def profile(user_id):
    if request.method == "POST":
        models.ChangeTelegramId(current_user.get_id(), request.form.get("telegram"))
    
    user = models.getUser(user_id=int(user_id))
    elements = models.GetProductsUsernameId(user_id)
    current_u = models.getUser(current_user.get_id())
    notfications = models.GetWaitingItems(user_id)

    return render_template(
                                                    "profile.html",
                                                    current_username=user["username"],
                                                    username=current_u["username"],
                                                    amount=user["balance"],
                                                    date=user["date"],
                                                    email=user["email"],
                                                    ip=user["ip"],
                                                    elements=elements,
                                                    telegram=user["telegram"],
                                                    user_id=user_id,
                                                    notfications=notfications
                            )

@app.route("/add-item", methods=["GET", "POST"])
@login_required
def AddItem():
    try:
        if request.method == "POST":
            contact = request.form.get("telegram")
            title = request.form.get("name")
            price = request.form.get("price")
            description = request.form.get("description")
            img = request.form.get("img")

            user = models.getUser(current_user.get_id())
            models.AddItemToBase(title=title, description=description, price=price, contact=contact, user_id=user["id"], img=img)

        else:
            user = models.getUser(current_user.get_id())
            return render_template("tracking-order.html", username=user["username"])

        user = models.getUser(current_user.get_id())
        return render_template("tracking-order.html", username=user["username"])
    except: return "404"

@app.route("/item/<string:item_id>")
def ViewItem(item_id):
    try:
        item = models.GetItemById(item_id)
        user = models.getUser(current_user.get_id())
        comments = models.GetComments(item_id)

        user_id = current_user.get_id()

        return render_template("single-product.html", comments=comments, user_id=user_id, item_id=item_id, username=user["username"], img=item["img"], title=item["title"], price=item["price"], description=item["description"], )

    except Exception as ex:
        print(ex)
        return "404"

@app.route("/add-comment", methods=["POST"])
@login_required
def add_comment():
    try:
        description = request.form.get("description")
        item_id = request.form.get("item_id")
        author_id = request.form.get("user_id") 
        stars = request.form.get("stars")
        username = models.getUser(author_id)["username"]

        models.AddComment(description=description, item_id=item_id, user_id=author_id, stars=stars, contact=username)        


        return redirect(f"/item/{item_id}")
    
    except: "Error"

@app.route("/upbalance", methods=["POST", "GET"])
@login_required
def upbalance():

    if request.method == "POST":

        if request.form.get('check') is None:

            price = request.form.get("price")
            s = requests.Session()

            s.headers["authorization"] = "Bearer " + config.token
            response_qiwi = s.get(f"https://edge.qiwi.com/payment-history/v2/persons/{config.number}/payments", params={"rows": 1, "operation": "IN"}),

            passwd = list("1234567890ABCDEFGHIGKLMNOPQRSTUVYXWZ")
            random.shuffle(passwd)
            random_chars = "".join([random.choice(passwd) for x in range(10)])
            generate_number_check = str(
                random.randint(100000000000, 999999999999)
            )

            qiwi = QiwiP2P(config.secret_key)
            bill = qiwi.bill(
                bill_id=generate_number_check,
                amount=int(price),
                comment=generate_number_check,
            )
            way_pay = "Form"
            send_requests = bill.pay_url

            models.AddReceipt(generate_number_check, current_user.get_id())

            return redirect(send_requests)
        else:
            try:

                receipt = models.GetReceipt(current_user.get_id())

                get_payments = (
                    config.number,
                    config.token,
                    config.secret_key,
                    config.nickname,
                    "form",
                    "True",
                )

                if (
                    get_payments[0] != "None"
                    or get_payments[1] != "None"
                    or get_payments[2] != "None"
                ):
                    qiwi = QiwiP2P(get_payments[2])
                    pay_comment = qiwi.check(
                        bill_id=receipt
                    ).comment  # Получение комментария платежа
                    pay_status = qiwi.check(bill_id=receipt).status  # Получение статуса платежа
                    pay_amount = float(
                        qiwi.check(bill_id=receipt).amount
                    )  # Получение суммы платежа в рублях
                    pay_amount = int(pay_amount)
                    if pay_status == "PAID":             
                        models.AddReceipt("#", current_user.get_id()) # Заглушка для проверок пополнений
                        models.AddBalance(current_user.get_id(), int(pay_amount))      # Выдача баланса

                        
                        
                        return f"<b>✅ Вы успешно пополнили баланс на сумму {pay_amount}руб. Удачи ❤</b>\n<b>📃 Чек:</b> <code>+{receipt}</code><br><a href='/profile'>Вернуться в профиль</a>"

                    
                    elif pay_status == "EXPIRED":
                        return "<b>❌ Время оплаты вышло. Платёж был удалён.</b><br><a href='/profile'>Вернуться в профиль</a>"
                    elif pay_status == "WAITING":
                        return "❗ Оплата не была произведена.<br><a href='/profile'>Вернуться в профиль</a>"
                    elif pay_status == "REJECTED":
                        return "<b>❌ Счёт был отклонён.</b><br><a href='/profile'>Вернуться в профиль</a>"
                else:

                    return "❗ Извиняемся за доставленные неудобства,\nпроверка платежа временно недоступна.⏳ Попробуйте чуть позже.<br><a href='/profile'>Вернуться в профиль</a>"
            except: return "❗ ERROR<br><a href='/profile'>Вернуться в профиль</a>"


    return render_template("checkout.html")

@app.route("/conclusion", methods=["POST"])
@login_required
def conclusion():
    price = request.form.get("conclusion_price")
    phone = request.form.get("conclusion_phone")

    models.AddConclusion(int(price), current_user.get_id(), phone)

    return redirect(url_for("profile", user_id=current_user.get_id()))
 
@app.route("/shop", methods=["GET", "POST"])
def shop():
    return render_template("category.html")

@app.route("/send_message", methods=["POST"])
@login_required
def send_message():
    name = request.form.get("name")
    tg_user = request.form.get("message_user")
    my_tg = request.form.get("my_id")
    description = request.form.get("description")

    
    text = f"""
            🔔 Уведомление.
            👥 Имя написавшего: {name}
            👤 USER_ID: {my_tg}

            Сообщение:

            {description}
            """

    requests.get(f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={tg_user}&text={text}")

    return redirect(url_for("profile", user_id=current_user.get_id()))

@app.route("/buy/<int:item_id>", methods=["GET", "POST"])
def buy(item_id):
    
    item = models.GetItemById(item_id)
    user = models.getUser(current_user.get_id())["username"]
    item_owner = item["user_id"]
    owner = models.getUser(item_owner)


    if request.method == "POST":
        price = request.form.get("price")
        seller = owner["id"]
        item_for_expiry = models.GetItemById(item_id)

        # models.AddBalance(seller, int(price))
        models.UnAddBalance(current_user.get_id(), int(price))
        models.AddExpiryItem(img=item_for_expiry["img"], title=item_for_expiry["title"], description=item_for_expiry["description"][:30], item_id=item_id, contact=item_for_expiry["contact"], buyer=current_user.get_id(), seller=seller, price=item["price"])
        models.ChangeStatusItem(item_id, "2")

        user = models.getUser(current_user.get_id())["username"]
        return redirect(url_for("purchases", username=user, user_id=current_user.get_id()))



    return render_template(
                                                "confirmation.html",
                                                username=user,
                                                
                                                item_id=item_id,
                                                number=item_id,
                                                date=str(datetime.now()).split(" ")[0],
                                                price=item["price"],

                                                title=item["title"],
                                                date_item=item["date"],
        
                                                seller=owner["username"],
                                                registred=owner["date"],
                                                ip=owner["ip"],
                                                raiting=None,

                                                user_id=current_user.get_id()
        )

@app.route("/purchases", methods=["POST", "GET"])
@login_required
def purchases():

    if request.method == "POST":
        item_id = request.form.get("item_id")
        price = request.form.get("price")
        seller = request.form.get("seller")

        models.AddBalance(seller, int(price))
        models.DeleteItemExpiry(item_id)


    items = models.GetExpiryItemPurchase(current_user.get_id())
    return render_template("purchases.html", elements=items)
        
@app.route("/sales", methods=["POST", "GET"])
@login_required
def sales():
    
    if request.method == "POST":
        item_id = request.form.get("item_id")
        price = request.form.get("price")
        seller = request.form.get("seller")
        buyer = request.form.get("buyer")

        models.AddBalance(buyer, int(price))
        models.DeleteItemExpiry(item_id)
        models.ChangeStatusItem(item_id, "1")

        # models.AddBalance()

    items = models.GetExpiryItemSales(current_user.get_id())
    return render_template("sales.html", elements=items)


@app.route("/products")
def products():
    return render_template("category.html")

@app.route("/find", methods=["GET", "POST"])
def find():

    if request.method == "POST":
        
        categories = request.form.get("BrowseCategories").split("<span>")[0]
        brands = request.form.get("Brands").split("<span>")[0]
        color = request.form.get("Color").split("<span>")[0]
        price = request.form.get("Price").split("<span>")[0]

        logger.success(f"categories: {categories} | brand: {brands} | color: {color} | price: {price}")

    return render_template("category.html")


