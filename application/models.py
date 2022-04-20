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
    receipt = db.Column(db.String)

    def __repr__(self):
        return f"{self.id}:{self.email}:{self.username}:{self.password}:{self.balance}:{str(self.date).split(' ')[0]}:{self.receipt}"

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


    def __repr__(self):
        return f"{self.id}|{self.img}|{self.contact}|{self.title}|{self.description}|{self.price}|{self.user_id}|{str(self.date).split(' ')[0]}"

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

##############  TABLE 'ITEMS' ###################
def AddItemToBase(title, description, price, contact, user_id, img):

    item = Items(title=title, description=description, price=price, user_id=user_id, contact=contact, img=img)
    db.session.add(item)
    db.session.commit()

    return item

def GetItemById(id):
    item = str(Items.query.filter(Items.id == id).first()).split("|")



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

def GetItems():

    lst = []
    items = Items.query.all()

    items.reverse()

    for item in items[:4]:
        item = str(item).split("|")
        lst.append({
            "id" : item[0],
            "img" : item[1],
            "contact" : item[2],
            "title" : item[3],
            "description" : item[4],
            "price" : item[5],
            "user_id" : item[6]
        })

    return lst


##############  TABLE 'COMMENTS' ###################
def AddComment(item_id, user_id, stars, description, contact):
    comment = Comments(item_id=item_id, user_id=user_id, stars=stars, description=description, contact=contact)
    db.session.add(comment)
    db.session.commit()

    return comment

def GetComments(item_id):
    data = Comments.query.filter(Comments.item_id == item_id).all()
    return data

def AddReceipt(receipt, id):
    user = Users.query.filter_by(id=id).first()
    user.receipt = receipt

    db.session.commit()

def GetReceipt(id):
    user = Users.query.filter_by(id=id).first()
    return user.receipt