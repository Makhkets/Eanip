from datetime import datetime
from loguru import logger
from pyqiwip2p import QiwiP2P
import requests
import config
import random

import json
from appl.UserLogin import UserLogin as uslg
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from appl import *

@app.route("/")
def index():
    try:
        with app.app_context():
            db.create_all()

        user = models.getUser(current_user.get_id())["username"]
        return render_template("index.html", username=user, elements=models.GetItems(), user_id=current_user.get_id())
    except Exception as ex: return str(ex)

@app.errorhandler(401)
def autherr(error):
    return render_template("error.html", code="401", message="Войдите в свой аккаунт или зарегистрируйтесь")

@app.errorhandler(404)
def notfound(error):
    return render_template("error.html", code="404", message="Страница не найдена")


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
                    return redirect(url_for('index'))
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

@app.route("/set-contact", methods=["POST"])
def set_contact():
    
    contact = request.form.get("contactt")
    models.UpdateContacts(contact, current_user.get_id())
    return redirect("/profile/" + current_user.get_id())

@app.route("/profile/<string:user_id>", methods=["GET", "POST"])
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
                                                    notfications=notfications,
                                                    contactt=user["contact"]
                            )


@app.route("/add-blog", methods=["GET", "POST"])
@login_required
def AddBlog():

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        img = request.form.get("img")

        models.AddBlog(title=title, description=description, img=img, user_id=current_user.get_id())
        return redirect(url_for('blog'))

    return render_template("add_blog.html", username=models.getUser(current_user.get_id())["username"])

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

            categories = request.form.get("gender")
            color = request.form.get("color")
            condition = request.form.get("condition")

            categories = config.categories[categories]
            color = config.colors[color]
            condition = config.conditions[condition]

            

            user = models.getUser(current_user.get_id())
            models.AddItemToBase(
                                                                    title=title,
                                                                    description=description,
                                                                    price=price,
                                                                    contact=contact,
                                                                    user_id=user["id"],
                                                                    img=img,
                                                                    color=color,
                                                                    categories=categories,
                                                                    condition=condition
                                )

        else:
            user = models.getUser(current_user.get_id())
            return render_template("tracking-order.html", username=user["username"])

        user = models.getUser(current_user.get_id())
        return render_template("tracking-order.html", username=user["username"])
    except Exception as ex: return str(ex)

@app.route("/item/<string:item_id>")
def ViewItem(item_id):

    item = models.GetItemByIdDEF(item_id)
    comments = models.GetComments(item_id)
    user = models.getUser(user_id=current_user.get_id())


    return render_template("single-product.html", username=user["username"], comments=comments, user_id=current_user.get_id(), item_id=item_id, product=item, recomended=models.GetItemsDef())

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

        price = request.form.get("price")
        bill_id = random.randint(111111, 999999)
        new_bill = p2p.bill(bill_id=bill_id, amount=int(price), lifetime=40,
                            comment=bill_id)


        # models.AddConclusion(price, current_user.get_id(), "79388954250")

    print(new_bill.bill_id, new_bill.pay_url)
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
    return render_template("category.html", username=models.getUser(current_user.get_id())["username"], recomended=models.GetItemsDef())

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
@login_required
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
    return render_template("purchases.html", elements=items, username=models.getUser(current_user.get_id())["username"])
        
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


    
    items = models.GetExpiryItemSales(current_user.get_id())
    return render_template("sales.html", elements=items, username=models.getUser(current_user.get_id())["username"])

@app.route("/products")
def products():

    products = models.GetElementFind("Без разницы", "Без разницы", "Без разницы", "Без разницы")
    
    return render_template("category.html", products=products, username=models.getUser(current_user.get_id())["username"], recomended=models.GetItemsDef())

@app.route("/find", methods=["GET", "POST"])
def find():


    if request.method == "POST":
        
        categories = request.form.get("BrowseCategories").split("<span>")[0]
        condition = request.form.get("Brands").split("<span>")[0]
        color = request.form.get("Color").split("<span>")[0]
        price = request.form.get("Price").split("<span>")[0]

        if len(categories) <= 1: categories = "Без разницы"
        if len(condition) <= 1: condition = "Без разницы"
        if len(color) <= 1: color = "Без разницы"
        



        products = models.GetElementFind(categories=categories, condition=condition, color=color, price=price)

        return render_template("category.html", products=products, username=models.getUser(current_user.get_id())["username"], recomended=models.GetItemsDef())


    else:
        return "Доступ закрыт!"

@app.route("/api/products")
def API_products():
    products = models.API_GetProducts()
    return json.dumps(products, ensure_ascii=False)

@app.route("/blog")
def blog():

    

    return render_template("blog.html", username=models.getUser(current_user.get_id())["username"], cards=models.NewBlogArticles())
    

# Добавлены обработки ошибок и страница ошибки которая обрабатывает ошибки (401, 404)
# Добавлен блок новости сайта