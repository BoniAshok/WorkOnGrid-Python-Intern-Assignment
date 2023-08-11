from flask import Flask, request, jsonify
import requests
import sqlite3

app = Flask(__name__)

DATABASE = 'user_database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/users', methods=['GET'])
def search_users():
    first_name = request.args.get('first_name')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users WHERE first_name LIKE ?
    ''', (f"{first_name}%",))
    matching_users = cursor.fetchall()

    if matching_users:
        return jsonify([dict(user) for user in matching_users])

    response = requests.get(f'https://dummyjson.com/users/search?q={first_name}')

    try:
        external_users = response.json()
        if isinstance(external_users, list):
            for user in external_users:
                cursor.execute('''
                    INSERT INTO users (first_name, last_name, age, gender, email, phone, birth_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user.get('first_name', ''), user.get('last_name', ''), user.get('age', None),
                    user.get('gender', ''), user.get('email', ''), user.get('phone', ''), user.get('birth_date', '')
                ))
            conn.commit()
        else:
            return "Invalid JSON format from the external API", 500

    except Exception as e:
        return f"Error: {e}", 500

    return jsonify(external_users)

if __name__ == '__main__':
    app.run(debug=True)
