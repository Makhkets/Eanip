import time
from loguru import logger
from pyqiwip2p import QiwiP2P
import requests
import config
import random
import datetime

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
        return render_template("index.html", username=user, elements=models.GetItems())
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

@app.route("/profile")
@login_required
def profile():
    try:
        user = models.getUser(current_user.get_id())
        return render_template("profile.html", username=user["username"], amount=user["balance"], date=user["date"], email=user["email"])
    except: return "404"

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

        for comment in comments:
            logger.success(f"username: {comment.contact}")
            logger.success(f"stars: {comment.stars}")
            logger.success(f"date: {comment.date}")
            logger.success(f"description: {comment.description}")


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

                        logger.success("УСПЕШНАЯ ОПЛАТА")
                        
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

# @login_required - только для зарегистрированных
# 183812630043