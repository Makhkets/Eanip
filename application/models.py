
from loguru import logger
from datetime import datetime

from application import *


class Users(db.Model):

    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    balance = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    ip = db.Column(db.String, nullable=False)
    user_id_telegram = db.Column(db.String)
    receipt = db.Column(db.String)
    contact = db.Column(db.String)

    def __repr__(self):
        return f"{self.id}:{self.email}:{self.username}:{self.password}:{self.balance}:{str(self.date).split(' ')[0]}:{self.receipt}:{self.ip}:{self.user_id_telegram}:{self.contact}"

class Items(db.Model):

    __tablename__ = "items"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    img = db.Column(db.String, nullable=False)
    contact = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    view = db.Column(db.String, default="1") # active - 1, waiting - 2, close - 3

    color = db.Column(db.String, nullable=False)
    categories = db.Column(db.String, nullable=False)
    condition = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"{self.id}|{self.img}|{self.contact}|{self.title}|{self.description}|{self.price}|{self.user_id}|{str(self.date).split(' ')[0]}|{self.categories}"

class Comments(db.Model):

    __tablename__ = "comments"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, nullable=False)
    stars = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    contact = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


    def __repr__(self):
        return f"{self.id}|{self.contact}|{self.description}|{self.user_id}|{str(self.date).split(' ')[0]}"

class Expiry(db.Model):

    __tablename__ = "expiry"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    item_id = db.Column(db.String, nullable=False)
    contact = db.Column(db.String, nullable=False)
    buyer = db.Column(db.String, nullable=False)
    seller = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    price = db.Column(db.Integer)

class Conclusion(db.Model):

    __tablename__ = "conclusion"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    qiwi = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

##############  TABLE 'USERS' ###################
def getUser(user_id):
    try:
        data = Users.query.filter(Users.id == user_id).first()
        info = str(data).split(":")
        
        return {
            "id" : info[0],
            "email" : info[1],
            "username" : info[2],
            "password" : info[3],
            "balance" : info[4],
            "date" : info[5],
            "ip" : info[7],
            "telegram" : info[8],
            "contact" : info[9]
        }

    except:
        return {"username" : False}

def getUserByUsername(username):

    try:
        data = Users.query.filter(Users.username == username).first()

        info = str(data).split(":")

        print(info)

        return {
            "id" : info[0],
            "email" : info[1],
            "username" : info[2],
            "password" : info[3],
            "balance" : info[4],
            "date" : info[5],
        }

    except:
        return {"username" : False}

def getUserByEmail(email):

    try:
        data = Users.query.filter(Users.email == email).first()

        info = str(data).split(":")

        print(info)

        return {
            "id" : info[0],
            "email" : info[1],
            "username" : info[2],
            "password" : info[3],
            "balance" : info[4],
            "date" : info[5],
        }

    except:
        return {"username" : False}

def add_user(username, password, email):

    user = models.Users(username=username, password=password, email=email, ip=request.remote_addr)
    db.session.add(user)
    db.session.commit()

def AddBalance(id, value):
    user = Users.query.filter_by(id=id).first()
    user.balance += value

    db.session.commit()

def UnAddBalance(id, value):
    user = Users.query.filter_by(id=id).first()
    user.balance -= value

    db.session.commit()

def AddConclusion(price, user_id, phone):
    
    user = Users.query.filter(Users.id == user_id).first()
    user.balance -= price

    conc = Conclusion(user_id=user_id, qiwi=phone, price=price)

    db.session.add(conc)
    db.session.commit()

def GetProductsUsernameId(user_id):
    return Items.query.filter(Items.user_id == int(user_id)).filter(Items.view == "1").all()

def ChangeTelegramId(user_id, user_id_tg):
    u = Users.query.filter(Users.id == user_id).first()
    u.user_id_telegram = user_id_tg
    db.session.commit()

def UpdateContacts(contact, user_id):
    user = Users.query.filter(user_id == user_id).first()
    user.contact = contact
    db.session.commit()
    
##############  TABLE 'ITEMS' ###################
def AddItemToBase(title, description, price, contact, user_id, img, color, categories, condition):

    item = Items(
                                                    title=title, 
                                                    description=description, 
                                                    price=price, 
                                                    user_id=user_id, 
                                                    contact=contact,
                                                    img=img, 
                                                    color=color, 
                                                    categories=categories, 
                                                    condition=condition
                )
    db.session.add(item)
    db.session.commit()

    return item

def GetItemById(id):
    item = str(Items.query.filter(Items.id == id).filter(Items.view == "1").first()).split("|")

    return {
        "id" : item[0],
        "img" : item[1],
        "contact" : item[2],
        "title" : item[3],
        "description" : item[4],
        "price" : item[5],
        "user_id" : item[6],
        "date" : item[7]
    }

def GetItemByIdDEF(item_id):
    return Items.query.filter(Items.id == item_id).first()

def GetItemsDef():
    return Items.query.all()

def GetItems():

    lst = []
    items = Items.query.filter(Items.view == "1").all()

    items.reverse()

    for item in items:


        item = str(item).split("|")
        lst.append({
            "id" : item[0],
            "img" : item[1],
            "contact" : item[2],
            "title" : item[3],
            "description" : item[4],
            "price" : item[5],
            "user_id" : item[6],
            "categories" : item[8]
        })


    return lst

def ChangeStatusItem(item_id, number):
    item = Items.query.filter(Items.id == item_id).first()
    item.view = number

    db.session.commit()

def GetWaitingItems(user_id):
    return Items.query.filter(Items.user_id == user_id).filter(Items.view == "2").all()

def GetElementFind(categories, condition, color, price):
    
    if price == "Без разницы":
        return Items.query.all()

    price1 = int(str(price).split(",")[0].split(".")[0])
    price2 = int(str(price).split(",")[1].split(".")[0])

    if categories == "Без разницы" and condition == "Без разницы" and color == "Без разницы":
        return Items.query.all()
    elif categories != "Без разницы" and condition != "Без разницы" and color != "Без разницы":
        return Items.query.filter(Items.categories == categories).filter(Items.condition == condition).filter(Items.color == color).filter(Items.price > price1).filter(Items.price < price2).all()
    elif len(categories) > 1 and condition == "Без разницы" and color == "Без разницы":
        return Items.query.filter(Items.categories == categories).all()
    elif len(condition) > 1 and categories == "Без разницы" and color == "Без разницы":
        return Items.query.filter(Items.condition == condition).all()
    elif len(color) > 1 and categories == "Без разницы" and condition == "Без разницы":
        return Items.query.filter(Items.color == color).all()
    elif len(categories) > 1 and len(condition) > 1 and color == "Без разницы":
        return Items.query.filter(Items.categories == categories).filter(Items.condition == condition).all()
    elif len(categories) > 1 and len(color) > 1 and condition == "Без разницы":
        return Items.query.filter(Items.categories == categories).filter(Items.color == color).all()
    elif len(condition) > 1 and len(color) > 1 and categories == "Без разницы":
        return Items.query.filter(Items.condition == condition).filter(Items.color == color).all()

    return Items.query.all()

##############  TABLE 'COMMENTS' ###################
def AddComment(item_id, user_id, stars, description, contact):
    comment = Comments(item_id=item_id, user_id=user_id, stars=stars, description=description, contact=contact)
    db.session.add(comment)
    db.session.commit()

    return comment

def GetComments(item_id):
    data = Comments.query.filter(Comments.item_id == item_id).all()
    return data

##############  TABLE 'EXPIRY' ###################
def AddExpiryItem(img, title, description, item_id, contact, buyer, seller, price):
    item = Expiry(img=img, title=title, description=description, item_id=item_id, contact=contact, buyer=buyer, seller=seller, price=price)
    
    db.session.add(item)
    db.session.commit()

def GetExpiryItemPurchase(user_id):
    return Expiry.query.filter(Expiry.buyer == user_id).all()

def GetExpiryItemSales(user_id):
    return Expiry.query.filter(Expiry.seller == user_id).all()

def DeleteItemExpiry(item_id):
    item = Expiry.query.filter(Expiry.item_id == item_id).first()

    db.session.delete(item)
    db.session.commit()

##############  TABLE 'OTHER' ###################
def AddReceipt(receipt, id):
    user = Users.query.filter_by(id=id).first()
    user.receipt = receipt

    db.session.commit()

def GetReceipt(id):
    user = Users.query.filter_by(id=id).first()
    return user.receipt

##############  TABLE 'API' ###################
def API_GetProducts():
    
    products = Items.query.all()
    elements = {}

    for el in products:
        el = str(el).split("|")
        elements[  str(el[0])  ] = {
                                                                    "id" : el[0],
                                                                    "image" : el[1],
                                                                    "contact" : "+7XXXXXXXXXX",
                                                                    "title" : el[3],
                                                                    "price" : el[4],
                                                                    "date" : el[5],
                                                                    "categories" : el[6]
        }

    return elements


