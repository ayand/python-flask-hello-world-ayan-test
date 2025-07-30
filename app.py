from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

app = Flask(__name__)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table_name = 'users'

@app.route('/health', methods=['GET'])
def health_check():
    return "All good. You don't need to be authenticated to call this"

@app.route("/hello/<username>", methods=["PUT"])
def save_user_data(username):
    print(f"Received request to save user data for {username}")
    data = request.get_json()
    date_of_birth = data["dateOfBirth"]
    
    if not username.isalpha():
        return jsonify({"error": "Username must contain only letters"}), 400
    
    try:
        date_of_birth_parsed = datetime.strptime(date_of_birth, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    if date_of_birth_parsed >= datetime.now():
        return jsonify({"error": "Date of birth must be in the past."}), 400
    
    table = dynamodb.Table(table_name)
    try:
        table.put_item(
            Item={
                'username': username,
                'date_of_birth': date_of_birth
            }
        )
        return "", 204
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/hello/<username>", methods=["GET"])
def get_hello_message(username):
    print(f"Received request to get hello message for {username}")
    table = dynamodb.Table(table_name)
    try:
        response = table.get_item(Key={'username': username})
        item = response.get('Item')
        if not item:
            return jsonify({"message": f"User {username} not found"}), 404
        
        date_of_birth = datetime.strptime(item['date_of_birth'], "%Y-%m-%d")
        today = datetime.today()
        this_year_birthday = datetime(today.year, date_of_birth.month, date_of_birth.day)
        
        if today > this_year_birthday:
            next_birthday = this_year_birthday.replace(year=today.year + 1)
        else:
            next_birthday = this_year_birthday

        days_until_birthday = (next_birthday - today).days + 1

        if days_until_birthday == 365:
            message = f"Hello, {username}! Happy birthday!"
        else:
            message = f"Hello, {username}! Your birthday is in {days_until_birthday} day(s)."
        
        return jsonify({"message": message}), 200

    except ClientError as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True,threaded=True, host='0.0.0.0', port=5000)


