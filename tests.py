import app as a
import pytest

client = a.app.test_client()


def get_book_by_id(book_id):
    return next((b for b in a.books if b["id"] == book_id), None)


def get_user_by_id(user_id):
    return next((u for u in a.users if u["id"] == user_id), None)


def test_get_books():
    with a.app.app_context():
        response, status_code = a.get_books()
        assert status_code == 200, "The status code is wrong"
        books = response.get_json()
        books_length = len(books)
        assert books_length == len(a.books), "The length is not correct"
        for i in range(books_length):
            assert books[i] == a.books[i], "The returned list doesn't match the original"


def test_add_book_fail():
    with a.app.app_context():
        data =  {"id": 3, "title": "", "author": "Some One", "is_borrowed": False}
        res = client.post('/books', json = data)
        assert res.status_code == 400, "The status code is wrong"
        assert data not in a.books, "The new data was not added"

        data =  {"id": 3, "title": "Good Book", "author": "", "is_borrowed": False}
        res = client.post('/books', json = data)
        assert res.status_code == 400, "The status code is wrong"
        assert data not in a.books, "The new data was not added"


def test_add_book():
    with a.app.app_context():
        old_len = len(a.books)
        new_len = old_len + 1

        data =  {"id": 3, "title": "Good Book", "author": "Some One", "is_borrowed": False}
        res = client.post('/books', json = data)
        assert res.status_code == 201, "The status code is wrong"
        response = a.get_books()[0]
        books = response.get_json()
        books_length = len(books)
        assert books_length == new_len, "The length is incorrect"
        assert data in a.books, "The new data was not added"


def test_update_book_fail():
    with a.app.app_context():
        data =  {"id": 3, "title": "", "author": "Some One", "is_borrowed": False}
        res = client.put(f'/books/{data["id"]}', json = data)
        assert res.status_code == 400, "The status code is worng"
        assert res.get_json() == {"error": "The title is missing"}, "Incorrect error message"

        data =  {"id": 3, "title": "Good Book", "author": "", "is_borrowed": False}
        res = client.put(f'/books/{data["id"]}', json = data)
        assert res.status_code == 400, "The status code is worng"
        assert res.get_json() == {"error": "The author is missing"}, "Incorrect error message"


def test_update_book():
    with a.app.app_context():
        response = a.get_books()[0]
        books = response.get_json()
        books_length = len(books)

        data =  {"id": 3, "title": "Good Book", "author": "Some One", "is_borrowed": False}
        res = client.put(f'/books/{data["id"]}', json = data)
        assert res.status_code == 200, "Incorrect status code"
        data =  {"id": 4, "title": "Very Good Book", "author": "Someone Else", "is_borrowed": False}
        res = client.put(f'/books/{data["id"]}', json = data)
        assert res.status_code == 404, "Incorrect status code"
        assert res.get_json() == {"error": "Book not found"}, "Incorrect error message"
        new_len = len(a.books)
        assert books_length == new_len, "Incorrect list length"


def test_delete_book_fail():
    with a.app.app_context():
        book_id = len(a.books)
        another_book_id = book_id + 1
        response, status_code = a.delete_book(another_book_id)
        assert status_code == 404, "Incorrect status code"
        assert response.get_json() == {"error": "Book not found"}, "Incorrect error message"

def test_delete_book():
    with a.app.app_context():
        book_id = len(a.books)
        response, status_code = a.delete_book(book_id)
        assert status_code == 200, "Incorrect status code"
        assert response.get_json() == {"message": "Book deleted"}, "Incorrect success message"


def test_add_book_after_delete():
    with a.app.app_context():
        initial_books_count = len(a.books)
        assert initial_books_count >= 2, "Need at least 2 books for this test"
        
        book_to_delete = a.books[0]
        book_id_to_delete = book_to_delete["id"]
        response, status_code = a.delete_book(book_id_to_delete)
        assert status_code == 200, "Failed to delete the book"
        assert response.get_json() == {"message": "Book deleted"}, "Incorrect success message"
        assert book_to_delete not in a.books, "The book was not deleted"

        new_book = {"id": len(a.books) + 1, "title": "New Book", "author": "New Author", "is_borrowed": False}
        response = client.post('/books', json=new_book)
        assert response.status_code == 400, "The book should not have been added due to duplicate ID"
        assert response.get_json() == {"error": "Book ID already exists"}, "Incorrect error message"


def test_get_users():
    with a.app.app_context():
        response, status_code = a.get_users()
        assert status_code == 200, "Incorrect status code"

        users = response.get_json()
        users_length = len(users)
        assert users_length == len(a.users), "Incorrect users length"
        for i in range(users_length):
            assert users[i] == a.users[i], "The returned users list doesn't match the original"


def test_borrow_book_fail():
    with a.app.app_context():
        user_id = len(a.users)
        non_existing_user_id = user_id + 1
        book_id = len(a.books)
        non_existing_book_id = book_id + 1

        response, status_code = a.borrow_book(non_existing_user_id, book_id)
        assert status_code == 404, "Incorrect status code"
        assert response.get_json() == {"error": "User not found"}, "Incorrect error message"

        response, status_code = a.borrow_book(user_id, non_existing_book_id)
        assert status_code == 404, "Incorrect status code"
        assert response.get_json() == {"error": "Book not found"}, "Incorrect error message"

        book = get_book_by_id(book_id)
        book["is_borrowed"] = True
        response, status_code = a.borrow_book(user_id, book_id)
        assert status_code == 400, "Incorrect status code"
        assert response.get_json() == {"error": "Book already borrowed"}, "Incorrect error message"
        book["is_borrowed"] = False


def test_borrow_book():
    with a.app.app_context():
        user_id = len(a.users)
        book_id = len(a.books)

        response, status_code = a.borrow_book(user_id, book_id)
        assert status_code == 200, "Incorrect status code"
        assert response.get_json() == {"message": "Book borrowed successfully"}, "Incorrect success message"
        book = get_book_by_id(book_id)
        assert book["is_borrowed"], "The books must be marked as borrowed"

        
def test_return_book_fail():
    with a.app.app_context():
        user_id = len(a.users)
        non_existing_user_id = user_id + 1
        book_id = len(a.books)
        non_existing_book_id = book_id + 1
        user = get_user_by_id(user_id)
        book = get_book_by_id(book_id)

        response, status_code = a.return_book(non_existing_user_id, book_id)
        assert status_code == 404, "Incorrect status code"
        assert response.get_json() == {"error": "User not found"}, "Incorrect error message"

        response, status_code = a.return_book(user_id, non_existing_book_id)
        assert status_code == 404, "Incorrect status code"
        assert response.get_json() == {"error": "Book not found"}, "Incorrect error message"
        assert book["is_borrowed"], "The book is not marked as borrowed"
        assert book_id in user["borrowed_books"], "The book was not added to user's borrowed books"

def test_return_book():
    with a.app.app_context():
        user_id = len(a.users)
        book_id = len(a.books)
        user = get_user_by_id(user_id)
        book = get_book_by_id(book_id)

        response, status_code = a.return_book(user_id, book_id)
        assert status_code == 200, "Incorrect status code"
        assert response.get_json() == {"message": "Book returned successfully"}, "Incorrect success message"
        assert not book["is_borrowed"], "The book is still marked as borrowed"
        assert book_id not in user["borrowed_books"], "The book was not removed from user's borrowed books"