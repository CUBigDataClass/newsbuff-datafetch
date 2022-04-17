import pymongo
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from pymongo import MongoClient
from requests import session
from bson.objectid import ObjectId

import mongodbconfig


client = pymongo.MongoClient(mongodbconfig.conn_str, serverSelectionTimeoutMS=5000)
print(client.server_info())
mydb = client["testdbnewsbuff"]
user = mydb["users"]
news = mydb["article"]

app = Flask(__name__)
jwt = JWTManager(app)

# JWT Config
app.config["JWT_SECRET_KEY"] = mongodbconfig.JWT_SECRET_KEY


@app.route("/dashboard")
@jwt_required()
def dasboard():
    if 'first_name' in session:
        print('username',session['first_name'])
        return jsonify(message="Welcome! to Newsbuff " + session['first_name'])


@app.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    # test = User.query.filter_by(email=email).first()
    test = user.find_one({"email": email})
    if test:
        return jsonify(message="User Already Exist"), 409
    else:
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        password = request.form["password"]
        user_info = dict(first_name=first_name, last_name=last_name, email=email, password=password)
        user.insert_one(user_info)
        return jsonify(message="User added sucessfully"), 201


@app.route("/login", methods=["POST"])
def login():
    if request.is_json:
        email = request.json["email"]
        password = request.json["password"]
    else:
        email = request.form["email"]
        password = request.form["password"]

    test = user.find_one({"email": email, "password": password})
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login Succeeded!", access_token=access_token), 201
    else:
        return jsonify(message="Bad Email or Password"), 401


@app.route("/like", methods=["POST"])
@jwt_required()
def like():
    newsid = request.form["newsid"]
    #like is 1 if like or -1 if unlike
    like = request.form["like"]
    login_user = get_jwt_identity()
    #if user has liked the document cannot like again, same for unlike
    if(like == '1'):
        test_like = user.update_one({"email" : str(login_user)},{'$push' : {"like" : newsid}}, upsert = True)
        #if like successful then increment the count
        if(test_like):
            test = news.find_one_and_update({"_id" : ObjectId(newsid)},{'$inc' : {"like" : 1}})
            if test:
                return jsonify(message="Like incremented"), 201
            else:
                return jsonify(message="Unable to increment like"), 401
    elif(like == '-1'):
        #test_unlike = user.update_one({"email" : str(login_user)},{'$push' : {'like' : newsid}}, upsert = True)
        test_unlike = user.find({"email" : str(login_user)},{"like" : {'$in' : [newsid]}})
        print(test_unlike)
        if(test_unlike):
            test = news.find_one_and_update({"_id" : ObjectId(newsid)},{'$inc' : {"like" : -1}})
            user.update_one({"email" : str(login_user)}, {'$pull' : {"like" : newsid}})
            if test:
                return jsonify(message="Like deccremented"), 201
            else:
                return jsonify(message="Unable to decrement like"), 401

    return jsonify(message="Unable to handle request"), 401

@app.route("/bookmark", methods=["POST"])
@jwt_required()
def bookmark():
    login_user = get_jwt_identity()
    newsid = request.form["newsid"]
    test = user.update_one({"email" : str(login_user)},{'$push' : {'bookmarks' : newsid}}, upsert = True)
    if test:
        return jsonify(message="News bookmarked"), 201
    else:
        return jsonify(message="Unable to bookmark news"), 401

if __name__ == '__main__':
    app.run(host="localhost", debug=True)