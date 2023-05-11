from flask import Flask, request, render_template, jsonify
import requests
from bs4 import BeautifulSoup
app = Flask(__name__)
from pymongo import MongoClient
import certifi

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.0hxfvkf.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

@app.route('/')
def home():
   return render_template('index.html')

@app.route("/restaurant", methods=["POST"]) 
def restaurant_post():    
    url_receive = request.form['url_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']
    category_receive = request.form['category_give']

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    name = soup.select_one('h1[class="restaurant_name"]').text
    image = soup.select_one('img[class="center-croping"]')["src"]    
    address = soup.select_one('body > main > article > div.column-wrapper > div.column-contents > div > section.restaurant-detail > table > tbody > tr.only-desktop > td').text
    information = soup.select('body > main > article > div.column-wrapper > div.column-contents > div > section.restaurant-detail > table > tbody > tr')
    num = len(list(db.restaurant.find({},{'_id':False})))
    doc = {
        'image':image,
        'name':name,
        'address' : address,
        'category':category_receive,
        'star':star_receive,
        'comment':comment_receive,
        'information': [],
        'like' : 0,
        'num' : num +1
    }
    
    for infs in information:
        if infs.select_one('th').text != "웹 사이트" and infs.select_one('th').text != "메뉴" :
            th = infs.select_one('th').text
            td = infs.select_one('td').text.strip("\n")
            doc['information'].append({
                th: td,
            })

    db.restaurant.insert_one(doc)
    return jsonify({'msg':'작성완료'})

@app.route("/restaurant/like", methods=["POST"]) 
def restaurant_like():
    num_receive = request.form['num_give']
    like_receive = request.form['like_give']

    db.restaurant.update_one({'num': int(num_receive) },{'$set': {'like' : int(like_receive) + 1 }})
    return jsonify({'msg':'좋아요'})


@app.route("/restaurant", methods=["GET"])
def restaurant_get():
    restaurant_list = list(db.restaurant.find({},{'_id':False}))
    return jsonify({'restaurant':restaurant_list})


if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)