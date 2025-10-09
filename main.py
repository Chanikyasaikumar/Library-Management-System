import datetime


from bson import ObjectId
from flask import Flask, request, render_template, redirect, session
import pymongo
import os
import re
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
PROFILES_PATH = APP_ROOT+"/static/book_image"
IMAGES_PATH = APP_ROOT+"/static/media_image"

app = Flask(__name__)
app.secret_key = "LMS"

user_name = "admin"
user_password = "admin"


my_client = pymongo.MongoClient("mongodb://localhost:27017")
my_database = my_client["LMS"]
admin_collection = my_database["Admin"]
Librarian_collection = my_database["Librarian"]
Books_collection = my_database["Books"]
Genres_collection = my_database["Genres"]
Locations_collection = my_database["Locations"]
User_collection = my_database["User"]
Book_Copy_number_collection = my_database["Book_Copies_Numbers"]
Media_collection = my_database["Media"]
Borrowings_collection = my_database["Borrowings"]
Payments_collection = my_database["Payments"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("home.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    if username == user_name and password == user_password:
        session['role'] = 'admin'
        return redirect("admin_home")
    else:
        return render_template("message.html", message="Invalid Details")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/add_location")
def add_location():
    query = {}
    locations = Locations_collection.find(query)
    locations = list(locations)
    return render_template("add_location.html", locations=locations)


@app.route("/add_location_action")
def add_location_action():
    location = request.args.get("location")
    query = {"location_name": location}
    count = Locations_collection.count_documents(query)
    if count > 0:
        return redirect("add_location?message=Location Already Entered")
    else:
        Locations_collection.insert_one(query)
        return redirect("add_location?message=Location Entered")


@app.route("/update_location")
def update_location():
    location_id = request.args.get('location_id')
    location = Locations_collection.find_one({'_id': ObjectId(location_id)})
    return render_template("update_location.html", location_id=location_id, location=location)


@app.route("/update_location_action")
def update_location_action():
    location_id = request.args.get('location_id')
    location = request.args.get('location_name')
    query = {"_id": ObjectId(location_id)}
    query2 = {"$set": {"location_name": location}}
    Locations_collection.update_one(query, query2)
    return redirect("add_location?message=Location Updated")


@app.route("/add_librarian")
def add_librarian():
    query = {}
    librarians = Librarian_collection.find(query)
    librarians = list(librarians)
    query = {}
    locations = Locations_collection.find(query)
    locations = list(locations)
    return render_template("add_librarian.html", locations=locations, librarians=librarians, get_location_name_by_location_id=get_location_name_by_location_id)


@app.route("/library_registration_action", methods=['post'])
def library_registration_action():
    library_title = request.form.get("library_title")
    librarian_name = request.form.get("librarian_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    address = request.form.get("address")
    location = request.form.get("location")
    query = {"email": email}
    count = Librarian_collection.count_documents(query)
    if password != confirm_password:
        return render_template("message.html", message="Password Doesn't Match")
    if count > 0:
        return render_template("message.html", message="Duplicate e-mail id")
    query = {"phone": phone}
    count = Librarian_collection.count_documents(query)
    if count > 0:
        return redirect("add_librarian?message = Duplicate phone number")
    query = {"library_title": library_title, "librarian_name": librarian_name, "email": email, "phone": phone, "password": password, "address": address, "location": ObjectId(location)}
    Librarian_collection.insert_one(query)
    return redirect("add_librarian?message = Librarian Registered Successfully")


@app.route("/update_librarian")
def update_librarian():
    librarian_id = request.args.get('librarian_id')
    librarian = Librarian_collection.find_one({'_id': ObjectId(librarian_id)})
    query = {}
    locations = Locations_collection.find(query)
    locations = list(locations)
    return render_template("update_librarian.html", librarian_id=librarian_id, librarian=librarian, locations=locations)


@app.route("/update_librarian_action")
def update_librarian_action():
    librarian_id = request.args.get('librarian_id')
    library_title = request.args.get('library_title')
    librarian_name = request.args.get('librarian_name')
    email = request.args.get('email')
    phone = request.args.get('phone')
    address = request.args.get('address')
    location = request.args.get('location')
    query = {"_id": ObjectId(librarian_id)}
    query2 = {"$set": {"library_title": library_title, "librarian_name": librarian_name, "email": email, "phone": phone, "address": address, "location": ObjectId(location)}}
    Librarian_collection.update_one(query, query2)
    return redirect("add_librarian?message = Librarian Updated")


def get_location_name_by_location_id(location_id):
    query = {'_id': location_id}
    locations = Locations_collection.find_one(query)
    return locations


@app.route("/librarian_login")
def librarian_login():
    return render_template("librarian_login.html")


@app.route("/librarian_login_action", methods=['post'])
def librarian_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = Librarian_collection.count_documents(query)
    if count > 0:
        librarian = Librarian_collection.find_one(query)
        session['librarian_id'] = str(librarian['_id'])
        session['role'] = 'librarian'
        return render_template("librarian_home.html")
    else:
        return render_template("message.html", message="Invalid Login Details")


@app.route("/librarian_home")
def librarian_home():
    return render_template("librarian_home.html")


@app.route("/user_home")
def user_home():
    name = request.args.get("name")
    return render_template("user_home.html", name=name)


@app.route("/user_login")
def user_login():
    return render_template("user_login.html")


@app.route("/user_registration")
def user_registration():
    return render_template("user_registration.html")


@app.route("/user_registration_action", methods=['post'])
def user_registration_action():
    access_type = request.form.get("access_type")
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    address = request.form.get("address")
    state = request.form.get("state")
    city = request.form.get("city")
    query = {"access_type": access_type, "email": email}
    count = User_collection.count_documents(query)
    if password != confirm_password:
        return render_template("message.html", message="Password Doesn't Match")
    if count > 0:
        return render_template("message.html", message="Duplicate e-mail id")
    query = {"access_type": access_type, "phone": phone}
    count = User_collection.count_documents(query)
    if count > 0:
        return render_template("message.html", message="Duplicate phone number")
    query = {"access_type": access_type, "name": name, "email": email, "phone": phone, "password": password, "address": address, "state": state, "city": city}
    User_collection.insert_one(query)
    return render_template("message.html", message=" Registered Successfully", access_type=access_type)


@app.route("/user_login_action", methods=['post'])
def user_login_action():
    user_role = request.form.get("user_role")
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"access_type": user_role, "email": email, "password": password}
    count = User_collection.count_documents(query)
    if count > 0:
        user = User_collection.find_one(query)
        session['user_id'] = str(user['_id'])
        session['role'] = 'user'
        session['user_role'] = user_role
        return render_template("user_home.html")
    else:
        return render_template("message.html", message="Invalid Login Details")


@app.route("/add_genre")
def add_genre():
    query = {}
    genres = Genres_collection.find(query)
    genres = list(genres)
    return render_template("add_genre.html", genres=genres)


@app.route("/add_genre_action")
def add_genre_action():
    genre = request.args.get("genre")
    query = {"genre_name": genre}
    count = Genres_collection.count_documents(query)
    if count > 0:
        return redirect("add_genre?message=Genre Already Entered")
    else:
        Genres_collection.insert_one(query)
        return redirect("add_genre?message=Genre Successfully Entered")


@app.route("/add_books")
def add_books():
    search_keyword = request.args.get('search_keyword')
    if search_keyword == None:
        search_keyword = ""
    if search_keyword == "":
        query = {}
    else:
        keyword = re.compile(".*"+str(search_keyword)+".*", re. IGNORECASE)
        query = {"$or": [{"book_title": keyword}, {"author": keyword}]}
    books = Books_collection.find(query)
    books = list(books)
    query = {}
    geners = Genres_collection.find(query)
    genres = list(geners)
    query = {}
    librarians = Librarian_collection.find(query)
    librarians = list(librarians)
    if session['role'] == "librarian":
        librarian_id = session['librarian_id']
    else:
        librarian_id = 0
    return render_template("add_books.html", librarians=librarians, genres=genres, librarian_id=librarian_id, str=str, books=books, get_genre_name_by_genre_id=get_genre_name_by_genre_id, get_book_copies_by_book_id=get_book_copies_by_book_id, get_librarian_id_by_book_id=get_librarian_id_by_book_id, search_keyword=search_keyword)


@app.route("/add_book_action", methods=['post'])
def add_book_action():
    if session['role'] == "admin":
        librarian_id = request.form.get('librarian_id')
    else:
        librarian_id = session['librarian_id']
    book_title = request.form.get('book_title')
    author = request.form.get('author')
    book_copies = request.form.get('book_copies')
    year = request.form.get('year')
    description = request.form.get('description')
    picture = request.files.get('picture')
    genre = request.form.get('genre')
    path = PROFILES_PATH + "/" + picture.filename
    picture.save(path)
    query = {"book_title": book_title}
    count = Books_collection.count_documents(query)
    if session['role'] == 'librarian':
        librarian_id = session['librarian_id']
        if count > 0:
            return render_template("l_message.html", message="Book Already Registered")

        query = {"book_title": book_title, "author": author, "book_copies": book_copies, "year": year, "description": description, "picture": picture.filename, "genre_id": ObjectId(genre), "librarian_id": ObjectId(librarian_id)}
        result = Books_collection.insert_one(query)
        book_id = result.inserted_id
        query = {"book_id": ObjectId(book_id)}
        count = Book_Copy_number_collection.count_documents(query)
        for i in range(count+1, int(book_copies)+count+1):
            book_copy_number = {
                "book_copy_number": i,
                "book_id": ObjectId(book_id),
                "librarian_id": ObjectId(librarian_id),
            }
            Book_Copy_number_collection.insert_one(book_copy_number)
        return redirect("add_books?message=Book Registered Successfully")
    else:
        if count > 0:
            return render_template("l_message.html", message="Book Already Registered")
        query = {"book_title": book_title, "author": author, "year": year, "description": description, "picture": picture.filename, "genre_id": ObjectId(genre)}
        Books_collection.insert_one(query)
        return redirect("add_books?message=Book Registered Successfully")


@app.route("/view_copies")
def view_copies():
    book_id = request.args.get("book_id")
    librarian_id = session['librarian_id']
    query = {"book_id": ObjectId(book_id), "librarian_id": ObjectId(librarian_id)}
    Copies = Book_Copy_number_collection.find(query)
    Copies = list(Copies)
    return render_template("/view_copies.html", Copies=Copies, get_is_book_assigned=get_is_book_assigned)


@app.route("/view_media_copies")
def view_media_copies():
    media_id = request.args.get("media_id")
    librarian_id = session['librarian_id']
    query = {"media_id": ObjectId(media_id), "librarian_id": ObjectId(librarian_id)}
    Media_Copies = Book_Copy_number_collection.find(query)
    Media_Copies = list(Media_Copies)
    return render_template("/view_media_copies.html", Media_Copies=Media_Copies, get_is_book_assigned=get_is_book_assigned)


@app.route("/update_book_copies")
def update_book_copies():
    book_id = request.args.get("book_id")
    return render_template("update_book_copies.html", book_id=book_id)


@app.route("/update_media_copies")
def update_media_copies():
    media_id = request.args.get("media_id")
    return render_template("update_media_copies.html", media_id=media_id)


@app.route("/update_book_copies_action", methods=['post'])
def update_book_copies_action():
    book_id = request.form.get("book_id")
    book_copies = request.form.get("book_copies")
    book = Books_collection.find_one({'_id': ObjectId(book_id)})
    if 'book_copies' in book:
        book_copies2 = int(book['book_copies'])
    else:
        book_copies2 = 0
    add_copies = int(book_copies2)+int(book_copies)
    query2 = {"$set": {"book_copies": add_copies}}
    Books_collection.update_one({"_id": ObjectId(book_id)}, query2)
    librarian_id = session['librarian_id']
    query = {"book_id": ObjectId(book_id), "librarian_id": ObjectId(librarian_id)}
    count = Book_Copy_number_collection.count_documents(query)
    for i in range(count + 1, int(book_copies) + count + 1):
        book_copy_number = {
            "book_copy_number": i,
            "book_id": ObjectId(book_id),
            "librarian_id": ObjectId(librarian_id),
        }
        Book_Copy_number_collection.insert_one(book_copy_number)
    return redirect("add_books?message=Book Copies Updated")


@app.route("/update_media_copies_action", methods=['post'])
def update_media_copies_action():
    media_id = request.form.get("media_id")
    book_copies = request.form.get("book_copies")
    book = Media_collection.find_one({'_id': ObjectId(media_id)})
    if 'media_copies' in book:
        book_copies2 = int(book['media_copies'])
    else:
        book_copies2 = 0
    add_copies = int(book_copies2) + int(book_copies)
    query2 = {"$set": {"media_copies": add_copies}}
    Media_collection.update_one({"_id": ObjectId(media_id)}, query2)
    librarian_id = session['librarian_id']
    query = {"media_id": ObjectId(media_id), "librarian_id": ObjectId(librarian_id)}
    count = Book_Copy_number_collection.count_documents(query)
    for i in range(count + 1, int(book_copies) + count + 1):
        book_copy_number = {
            "book_copy_number": i,
            "media_id": ObjectId(media_id),
            "librarian_id": ObjectId(librarian_id),
        }
        Book_Copy_number_collection.insert_one(book_copy_number)
    return redirect("add_media?message=Book Copies Updated")


@app.route("/add_media")
def add_media():
    query = {}
    medias = Media_collection.find(query)
    medias = list(medias)
    return render_template("add_media.html", medias=medias, get_librarian_id_by_book_id=get_librarian_id_by_book_id, get_book_copies_by_media_id=get_book_copies_by_media_id)


def get_book_copies_by_media_id(media_id):
    book_copies = Book_Copy_number_collection.find_one({"media_id": ObjectId(media_id)})
    return book_copies


@app.route("/add_media_action", methods=['post'])
def add_media_action():
    media_title = request.form.get('media_title')
    media_type = request.form.get('media_type')
    media_author = request.form.get('media_author')
    picture = request.files.get('picture')
    about_media = request.form.get('about_media')
    media_copies = request.form.get('media_copies')
    year = request.form.get('year')
    path = IMAGES_PATH + "/" + picture.filename
    picture.save(path)

    if session['role'] == 'librarian':
        librarian_id = session['librarian_id']
        query = {"media_title": media_title}
        count = Media_collection.count_documents(query)
        if count > 0:
            return redirect("add_media?message = Media Already Entered")
        query = {"media_title": media_title, "media_type": media_type, "media_author": media_author, "picture": picture.filename, "about_media": about_media, "year": year}
        result = Media_collection.insert_one(query)
        media_id = result.inserted_id
        query = {"media_id": ObjectId(media_id)}
        count = Book_Copy_number_collection.count_documents(query)
        for i in range(count + 1, int(media_copies) + count + 1):
            media_copy_number = {
                "book_copy_number": i,
                "media_id": ObjectId(media_id),
                "librarian_id": ObjectId(librarian_id),
            }
            Book_Copy_number_collection.insert_one(media_copy_number)
        return redirect("add_media?message=Media added Successfully")
    else:
        query = {"media_title": media_title}
        count = Media_collection.count_documents(query)
        if count > 0:
            return render_template("l_message.html", message="Media Already Registered")
        query = {"media_title": media_title, "media_type": media_type, "media_author": media_author, "picture": picture.filename, "about_media": about_media, "year": year}
        Media_collection.insert_one(query)
        return redirect("add_media?message=Media added Successfully")


def get_genre_name_by_genre_id(genre_id):
    query = {"_id": ObjectId(genre_id)}
    generes = Genres_collection.find_one(query)
    return generes


def get_book_copies_by_book_id(book_id):
    query = {"book_id": ObjectId(book_id)}
    book_copies = Book_Copy_number_collection.find_one(query)
    return book_copies


def get_librarian_id_by_book_id(librarian_id):
    query = {"_id": ObjectId(librarian_id)}
    libraians = Librarian_collection.find_one(query)
    return libraians


@app.route("/search_book")
def search_book():
    book = request.args.get("book")
    media = request.args.get("media")
    if media == None:
        media = ""
    if book == None:
        book = ""
    if book != "":
        search_keyword = request.args.get('search_keyword')
        if search_keyword == None:
            search_keyword = ""
        if search_keyword == "":
            query = {}
        else:
            keyword = re.compile(".*" + str(search_keyword) + ".*", re.IGNORECASE)
            query = {"$or": [{"book_title": keyword}, {"author": keyword}]}
        books = list(Books_collection.find(query))
        return render_template("view_books.html", books=books, get_genre_name_by_genre_id=get_genre_name_by_genre_id, get_librarian_id_by_book_id=get_librarian_id_by_book_id, get_book_copies_by_book_id=get_book_copies_by_book_id)
    elif media != "":
        search_keyword = request.args.get('search_keyword')
        if search_keyword == None:
            search_keyword = ""
        if search_keyword == "":
            query = {}
        else:
            keyword = re.compile(".*" + str(search_keyword) + ".*", re.IGNORECASE)
            query = {"$or": [{"media_title": keyword}, {"media_author": keyword}]}
        medias = Media_collection.find(query)
        return render_template("view_media.html", medias=medias, get_librarian_id_by_book_id=get_librarian_id_by_book_id, get_book_copies_by_book_id=get_book_copies_by_book_id, get_book_copies_by_media_id=get_book_copies_by_media_id)
    return render_template("search_book.html")


@app.route('/view_books')
def view_books():
    search_keyword = request.args.get('search_keyword')
    librarian_id = session['librarian_id']
    if search_keyword == None:
        search_keyword = ""
    if search_keyword == "":
        query = {}
    else:
        keyword = re.compile(".*" + str(search_keyword) + ".*", re.IGNORECASE)
        query = {"$or": [{"book_title": keyword}, {"author": keyword}]}
    books = list(Books_collection.find(query))
    return render_template('view_books.html', books=books, search_keyword=search_keyword, get_genre_name_by_genre_id=get_genre_name_by_genre_id, get_book_copies_by_book_id=get_book_copies_by_book_id, get_librarian_id_by_book_id=get_librarian_id_by_book_id)

#
# @app.route('/view_books')
# def view_books():
#     search_keyword = request.args.get('search_keyword')
#     librarian_id = session['librarian_id']
#
#     if not search_keyword:
#         query = {}
#     else:
#         keyword = re.compile(".*" + str(search_keyword) + ".*", re.IGNORECASE)
#         query = {"$or": [{"book_title": keyword}, {"author": keyword}]}
#
#     books = list(Books_collection.find(query))
#
#     copies_cursor = Book_Copy_number_collection.find({
#         "librarian_id": librarian_id,
#         "book_id": {"$exists": True}
#     })
#
#     copies_by_book = {}
#     for entry in copies_cursor:
#         book_id = str(entry["book_id"])
#         copies_by_book[book_id] = copies_by_book.get(book_id, 0) + 1
#
#     # Filter books that have copies under this librarian
#     books = [book for book in books if str(book['_id']) in copies_by_book]
#
#     return render_template(
#         'view_books.html',
#         books=books,
#         search_keyword=search_keyword,
#         get_genre_name_by_genre_id=get_genre_name_by_genre_id,
#         copies_by_book=copies_by_book
#     )


@app.route('/view_media')
def view_media():
    search_keyword = request.args.get('search_keyword')
    librarian_id = session['librarian_id']
    if search_keyword == None:
        search_keyword = ""
    if search_keyword == "":
        query = {}
    else:
        keyword = re.compile(".*" + str(search_keyword) + ".*", re.IGNORECASE)
        query = {"$or": [{"media_title": keyword}, {"media_author": keyword}]}
    medias = Media_collection.find(query)
    return render_template('view_media.html', medias=medias, get_librarian_id_by_book_id=get_librarian_id_by_book_id, search_keyword=search_keyword, get_book_copies_by_media_id=get_book_copies_by_media_id)


@app.route("/buy")
def buy():
    book_id = request.args.get("book_id")
    media_id = request.args.get("media_id")
    request_date = datetime.datetime.now()
    query = {}
    librarians = Librarian_collection.find(query)
    librarians = list(librarians)
    query = {}
    locations = Locations_collection.find(query)
    locations = list(locations)
    if book_id == None:
        book_id = ""
    if media_id == None:
        media_id = ""
    if media_id == "":
        Book_Copy_numbers = Book_Copy_number_collection.distinct("librarian_id", {"book_id": ObjectId(book_id)}
        )
    elif book_id == "":
        Book_Copy_numbers = Book_Copy_number_collection.distinct("librarian_id", {"media_id": ObjectId(media_id)})
        Book_Copy_numbers = list(Book_Copy_numbers)
    return render_template("buy.html", get_location_by_location_id=get_location_by_location_id, locations=locations, librarians=librarians, media_id=media_id, book_id=book_id, Book_Copy_numbers=Book_Copy_numbers, get_library_librarian_id=get_library_librarian_id, get_location_name_by_location_id=get_location_name_by_location_id)


def get_location_by_location_id(location_id):
    location = Locations_collection.find_one({"_id": ObjectId(location_id)})
    return location


@app.route("/buy_request")
def buy_request():
    book_id = request.args.get("book_id")
    media_id = request.args.get("media_id")
    if media_id == "":
        request_date = datetime.datetime.now()
        librarian_id = request.args.get("librarian_id")
        user_id = session['user_id']
        query = {"book_id": ObjectId(book_id), "librarian_id": ObjectId(librarian_id), "returnlibrarian_id": ObjectId(librarian_id), "request_date": request_date, "user_id": ObjectId(user_id), "status": 'Requested'}
        Borrowings_collection.insert_one(query)
        return render_template("b_message.html", message="Request sent Successfully")
    elif book_id == "":
        request_date = datetime.datetime.now()
        librarian_id = request.args.get("librarian_id")
        user_id = session['user_id']
        query = {"media_id": ObjectId(media_id), "librarian_id": ObjectId(librarian_id), "returnlibrarian_id": ObjectId(librarian_id), "request_date": request_date, "user_id": ObjectId(user_id), "status": 'Requested'}
        Borrowings_collection.insert_one(query)
        return render_template("b_message.html", message="Request sent Successfully")


@app.route("/view_borrowings")
def view_borrowings():
    query = {}
    if session['role'] == 'user':
        query = {"user_id": ObjectId(session['user_id']), "$or": [{"status": 'Requested'}, {"status": 'Assigned'}, {'status': 'Return Request Sent'}]}
    elif session['role'] == 'librarian':
        query = {"returnlibrarian_id": ObjectId(session['librarian_id']), "$or": [{"status": 'Requested'}, {"status": 'Assigned'}, {'status': 'Return Request Sent'}]}
    elif session['role'] == 'admin':
        query = {"$or": [{"status": 'Requested'}, {"status": 'Assigned'}, {'status': 'Return Request Sent'}]}
    borrowings = Borrowings_collection.find(query)
    borrowings = list(borrowings)
    return render_template("view_borrowings.html", int=int, borrowings=borrowings, get_user_name_by_user_id=get_user_name_by_user_id, get_book_copies_by_book_copies_id=get_book_copies_by_book_copies_id, get_media_by_book_copies_id=get_media_by_book_copies_id, get_book_by_book_copies_id=get_book_by_book_copies_id, get_library_librarian_id=get_library_librarian_id, get_location_name_by_location_id=get_location_name_by_location_id, get_fine=get_fine)


@app.route("/borrowings_history")
def borrowings_history():
    query = {}
    if session['role'] == 'user':
        query = {"user_id": ObjectId(session['user_id']), "$or": [{"status": 'Rejected'}, {"status": 'Book Returned'}, {"status": 'Return_Rejected'}]}
    elif session['role'] == 'librarian':
        query = {"returnlibrarian_id": ObjectId(session['librarian_id']), "$or": [{"status": 'Rejected'}, {"status": 'Book Returned'}, {"status": 'Return_Rejected'}]}
    elif session['role'] == 'admin':
        query = {"$or": [{"status": 'Rejected'}, {"status": 'Book Returned'}, {"status": 'Return_Rejected'}]}
    borrowings = Borrowings_collection.find(query)
    borrowings = list(borrowings)
    return render_template("borrowings_history.html", int=int, borrowings=borrowings, get_user_name_by_user_id=get_user_name_by_user_id, get_book_copies_by_book_copies_id=get_book_copies_by_book_copies_id, get_media_by_book_copies_id=get_media_by_book_copies_id, get_book_by_book_copies_id=get_book_by_book_copies_id, get_library_librarian_id=get_library_librarian_id, get_location_name_by_location_id=get_location_name_by_location_id, get_fine=get_fine)


def get_book_copies_by_book_copies_id(book_id):
    query = {"_id": ObjectId(book_id)}
    book_copies = Book_Copy_number_collection.find_one(query)
    return book_copies


def get_media_by_book_copies_id(media_id):
    query = {"_id": ObjectId(media_id)}

    medias = Media_collection.find_one(query)
    return medias


def get_book_by_book_copies_id(book_id):
    query = {"_id": ObjectId(book_id)}
    books = Books_collection.find_one(query)
    return books


def get_user_name_by_user_id(user_id):
    query = {"_id": ObjectId(user_id)}
    users = User_collection.find_one(query)
    return users


@app.route("/reject")
def reject():
    borrowing_id = request.args.get("borrowing_id")
    query = {"_id": ObjectId(borrowing_id)}
    query1 = {"$set": {"status": "Rejected"}}
    Borrowings_collection.update_one(query, query1)
    return redirect("view_borrowings")


@app.route("/assign_book")
def assign_book():
    borrowing_id = request.args.get("borrowing_id")
    librarian_id = request.args.get("librarian_id")
    borrowing = Borrowings_collection.find_one({"_id": ObjectId(borrowing_id)})
    query = {}

    if 'book_id' in borrowing:
        book_id = borrowing['book_id']
        query = {"book_id": ObjectId(book_id), "librarian_id": ObjectId(librarian_id)}
    if 'media_id' in borrowing:
        media_id = borrowing['media_id']
        query = {"media_id": ObjectId(media_id), "librarian_id": ObjectId(librarian_id)}
    book_copies = Book_Copy_number_collection.find(query)

    return render_template("assign_book.html", get_is_book_assigned=get_is_book_assigned, int=int, book_copies=book_copies, borrowing=borrowing, get_book_copy_book_id=get_book_copy_book_id, get_library_librarian_id=get_library_librarian_id)


def get_is_book_assigned(borrowing_id, book_copies_id):
    query = {"$or": [{"status": 'Requested'}, {"status": 'Assigned'}, {'status': 'Return Request Sent'}], "book_copies_id": ObjectId(book_copies_id)}
    count = Borrowings_collection.count_documents(query)
    return count


def get_book_copy_book_id(librarian_id, book_id):
    query = {"librarian_id": ObjectId(librarian_id), "book_id": ObjectId(book_id)}
    book_copy = Book_Copy_number_collection.find(query)
    return book_copy


def get_library_librarian_id(librarian_id):
    query = {"_id": ObjectId(librarian_id)}
    librarian = Librarian_collection.find_one(query)
    return librarian


@app.route("/assign")
def assign():
    borrowing_id = request.args.get("borrowing_id")
    book_copies_id = request.args.get("book_copies_id")
    query = {"_id": ObjectId(borrowing_id)}
    borrowing_date = datetime.datetime.now()
    returning_date = borrowing_date + datetime.timedelta(days=15)
    query1 = {"$set": {"status": "Assigned", "book_copies_id": ObjectId(book_copies_id), "borrowing_date": borrowing_date, "returning_date": returning_date}}
    Borrowings_collection.update_one(query, query1)
    Borrowings_collection.find_one({"_id": ObjectId(borrowing_id)})
    return redirect("/view_borrowings")


@app.route("/renewal_book")
def renewal_book():
    borrowing_id = request.args.get("borrowing_id")
    borrowing = Borrowings_collection.find_one({"_id": ObjectId(borrowing_id)})
    returning_date = borrowing['returning_date']
    renewal_date = returning_date + datetime.timedelta(days=15)
    if session['user_role'] == 'student':
        if 'renewal_count' in borrowing:
            if int(borrowing['renewal_count']) == 1:
                return render_template("user_message.html", message="You Can not renewal twice , only one time")
    else:
        if 'renewal_count' in borrowing:
            if int(borrowing['renewal_count']) == 2:
                return render_template("user_message.html", message="You Can not renewal , only two times")
    if 'renewal_count' in borrowing:

        renewal_count = int(borrowing['renewal_count'])
    else:
        renewal_count = 0
    query = {"$set": {"status": 'Assigned', "returning_date": renewal_date, "renewal_date": datetime.datetime.now(), "renewal_count": renewal_count+1}}
    Borrowings_collection.update_one({"_id": ObjectId(borrowing_id)}, query)
    return render_template("user_message.html", message="Book Renewal Successfully")


@app.route("/return_book")
def return_book():
    borrowing_id = request.args.get("borrowing_id")
    query = {}
    Book_Copies = Book_Copy_number_collection.find(query)
    Book_Copies = list(Book_Copies)
    query = {}
    librarians = Librarian_collection.find(query)
    librarians = list(librarians)
    return render_template("return_book.html", borrowing_id=borrowing_id, librarians=librarians, Book_Copies=Book_Copies, get_librarian_by_librarian_id=get_librarian_by_librarian_id, get_library_librarian_id=get_library_librarian_id, get_location_name_by_location_id=get_location_name_by_location_id)


@app.route("/return_book1")
def return_book1():
    borrowing_id = request.args.get("borrowing_id")
    librarian_id = request.args.get("librarian_id")
    query = {"$set": {"status": 'Return Request Sent', "status2": 'Location Change Request Sent', "returnlibrarian_id": ObjectId(librarian_id)}}
    Borrowings_collection.update_one({"_id": ObjectId(borrowing_id)}, query)
    return render_template("user_message.html", message="Return Request Sent")


def get_librarian_by_librarian_id(librarian_id):
    librarian = Librarian_collection.find_one({"_id": ObjectId(librarian_id)})
    return librarian


# @app.route("/accept_request")
# def accept_request():
#     borrowing_id = request.args.get('borrowing_id')
#     borrowing = Borrowings_collection.find_one({"_id":ObjectId(borrowing_id)})
#     returnlibrarian_id = borrowing['returnlibrarian_id']
#     book_copies_id = borrowing['book_copies_id']
#     book_cope_count = Book_Copy_number_collection.count_documents({"_id":ObjectId(book_copies_id),"librarian_id":ObjectId(returnlibrarian_id)})
#     print(book_cope_count)
#     if book_cope_count ==0:
#         Book_copie = Book_Copy_number_collection.find_one({"_id":ObjectId(book_copies_id)})
#         # media_id = result.inserted_id
#         if 'media_id' in Book_copie:
#             Book_Copy_number_collection.delete_one({"_id":ObjectId(book_copies_id)})
#             media = Media_collection.find_one({"_id":ObjectId(Book_copie['media_id'])})
#             media_copies = media['media_copies']
#             query = {"media_id": ObjectId(Book_copie['media_id'])}
#             count = Book_Copy_number_collection.count_documents(query)
#             print(count)
#             for i in range(count + 1, int(media_copies) + count + 1):
#                 media_copy_number = {
#                     "book_copy_number": i,
#                     "media_id": ObjectId(Book_copie['media_id']),
#                     "librarian_id": ObjectId(returnlibrarian_id),
#                 }
#                 Book_Copy_number_collection.insert_one(media_copy_number)
#             media_copies2 = int(media_copies)+1
#             query = {"$set": {"media_copies": media_copies2}}
#             Media_collection.update_one({"_id": ObjectId(Book_copie['media_id'])}, query)
#         elif 'book_id' in Book_copie:
#             Book_Copy_number_collection.delete_one({"_id":ObjectId(book_copies_id)})
#             book = Books_collection.find_one({"_id": ObjectId(Book_copie['book_id'])})
#             book_copies = book['book_copies']
#             query = {"book_id": ObjectId(Book_copie['book_id'])}
#             count = Book_Copy_number_collection.count_documents(query)
#             for i in range(count + 1, int(book_copies) + count + 1):
#                 media_copy_number = {
#                     "book_copy_number": i,
#                     "book_id": ObjectId(Book_copie['media_id']),
#                     "librarian_id": ObjectId(returnlibrarian_id),
#                 }
#                 Book_Copy_number_collection.insert_one(media_copy_number)
#             book_copies2 = int(book_copies) + 1
#             query = {"$set": {"book_copies": book_copies2}}
#             Books_collection.update_one({"_id": ObjectId(Book_copie['book_id'])}, query)
#     query = {"$set": {"status": "Book Returned", "status2": 'Book Returned'}}
#     Borrowings_collection.update_one({"_id": ObjectId(borrowing_id)}, query)
#     return redirect("/view_borrowings")


@app.route("/accept_request")
def accept_request():
    borrowing_id = request.args.get('borrowing_id')
    borrowing = Borrowings_collection.find_one({"_id": ObjectId(borrowing_id)})
    if not borrowing:
        return "Borrowing record not found", 404

    return_librarian_id = borrowing.get('returnlibrarian_id')
    book_copies_id = borrowing.get('book_copies_id')
    if not return_librarian_id or not book_copies_id:
        return "Incomplete borrowing data", 400

    book_copy_count = Book_Copy_number_collection.count_documents({
        "_id": ObjectId(book_copies_id),
        "librarian_id": ObjectId(return_librarian_id)
    })

    print("Book copy count:", book_copy_count)

    if book_copy_count == 0:
        book_copy = Book_Copy_number_collection.find_one({"_id": ObjectId(book_copies_id)})
        if not book_copy:
            return "Book copy not found", 404

        Book_Copy_number_collection.delete_one({"_id": ObjectId(book_copies_id)})

        if 'media_id' in book_copy:
            media_id = ObjectId(book_copy['media_id'])
            media = Media_collection.find_one({"_id": ObjectId(media_id)})
            if not media:
                return "Media not found", 404

            media_copies = media.get('media_copies', 0)
            count = Book_Copy_number_collection.count_documents({"media_id": ObjectId(media_id)})
            print(count)
            Book_Copy_number_collection.insert_one({
                "book_copy_number": count+1,
                "media_id": ObjectId(media_id),
                "librarian_id": ObjectId(return_librarian_id),
            })

            Media_collection.update_one(
                {"_id": ObjectId(media_id)},
                {"$set": {"media_copies": int(media_copies) + 1}}
            )

        elif 'book_id' in book_copy:
            book_id = ObjectId(book_copy['book_id'])
            book = Books_collection.find_one({"_id": ObjectId(book_id)})
            if not book:
                return "Book not found", 404

            book_copies = book.get('book_copies', 0)
            count = Book_Copy_number_collection.count_documents({"book_id": ObjectId(book_id)})

            Book_Copy_number_collection.insert_one({
                "book_copy_number": count+1,
                "book_id": ObjectId(book_id),
                "librarian_id": ObjectId(return_librarian_id),
            })

            Books_collection.update_one(
                {"_id": ObjectId(book_id)},
                {"$set": {"book_copies": int(book_copies) + 1}}
            )

    Borrowings_collection.update_one(
        {"_id": ObjectId(borrowing_id)},
        {"$set": {"status": "Book Returned", "status2": "Book Returned"}}
    )

    return redirect("/view_borrowings")


@app.route("/reject_request")
def reject_request():
    borrowing_id = request.args.get('borrowing_id')
    return render_template("reject_request.html", borrowing_id=borrowing_id)


@app.route("/reject_request_action")
def reject_request_action():
    borrowing_id = request.args.get('borrowing_id')
    reject_request = request.args.get('reject_request')
    query = {"_id": ObjectId(borrowing_id)}
    query1 = {"$set": {"status": "Return_Rejected", "Rejected_status": reject_request}}
    Borrowings_collection.update_one(query, query1)
    return redirect("/borrowings_history")


def get_fine(returning_date, borrowing_id):
    current_date = datetime.datetime.now()
    if current_date > returning_date:
        diff = current_date-returning_date
        day = diff.days
        fine = day * 1  # $1 per day fine
        return fine, True
    else:
        return 0, False


@app.route("/pay_fine")
def pay_fine():
    borrowing_id = request.args.get('borrowing_id')
    fine = request.args.get('fine')
    return render_template("pay_fine.html", fine=fine, borrowing_id=borrowing_id)


@app.route("/pay_fine_action", methods=['post'])
def pay_fine_action():
    borrowing_id = request.form.get('borrowing_id')
    fine = request.form.get('fine')
    card_number = request.form.get('card_number')
    holder_name = request.form.get('holder_name')
    expire_date = request.form.get('expire_date')
    payment_date = datetime.datetime.now()
    query = {"$set": {"status2": 'Fine Paid'}}
    Borrowings_collection.update_one({"_id": ObjectId(borrowing_id)}, query)
    query = {"fine": fine, "card_number": card_number, "holder_name": holder_name, "expire_date": expire_date, "payment_date": payment_date, "status": "Payment Successful", "borrowing_id": ObjectId(borrowing_id)}
    Payments_collection.insert_one(query)
    return render_template("user_message.html", message="Fine Paid")


@app.route("/view_payments")
def view_payments():
    borrowing_id = request.args.get('borrowing_id')
    query = {"borrowing_id": ObjectId(borrowing_id)}
    payments = Payments_collection.find(query)
    return render_template("view_payments.html", payments=payments, get_borrowing_by_borrowing_id=get_borrowing_by_borrowing_id, get_user_by_user_id=get_user_by_user_id)


def get_borrowing_by_borrowing_id(borrowing_id):
    query = {'_id': ObjectId(borrowing_id)}
    borrowings = Borrowings_collection.find_one(query)
    return borrowings


def get_user_by_user_id(user_id):
    query = {'_id': ObjectId(user_id)}
    user = User_collection.find_one(query)
    return user





app.run(host="0.0.0.0", port=5000)
