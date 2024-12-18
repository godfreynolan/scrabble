from flask import Flask, render_template, request, redirect, url_for, jsonify
import random
import openai
import config

app = Flask(__name__)

# Initialize a Scrabble board with empty slots
board = [["" for _ in range(15)] for _ in range(15)]

# Example letter bag
letter_bag = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") * 2
random.shuffle(letter_bag)

# Players' racks
players = {
    "player1": [letter_bag.pop() for _ in range(7)],
    "player2": [letter_bag.pop() for _ in range(7)]
}

# OpenAI API key (replace with your actual key)
openai.api_key = config.OPENAI_API_KEY

# Route for the main page
@app.route("/")
def home():
    return render_template("scrabble.html", board=board, players=players, points=None)

# Route to place a word
@app.route("/place_word", methods=["POST"])
def place_word():
    global board
    player = request.form["player"]
    word = request.form["word"]
    row = int(request.form["row"])
    col = int(request.form["col"])
    direction = request.form["direction"]  # "horizontal" or "vertical"

    try:
        if direction == "horizontal":
            for i, char in enumerate(word):
                if board[row][col + i] == "" or board[row][col + i] == char:
                    board[row][col + i] = char
                else:
                    raise ValueError("Invalid move")
        elif direction == "vertical":
            for i, char in enumerate(word):
                if board[row + i][col] == "" or board[row + i][col] == char:
                    board[row + i][col] = char
                else:
                    raise ValueError("Invalid move")
        # Replace used letters in the player's rack
        for char in word:
            if char in players[player]:
                players[player].remove(char)
                if letter_bag:
                    players[player].append(letter_bag.pop())
            else:
                raise ValueError("Player does not have the required letters")
    except Exception as e:
        return str(e), 400

    return redirect(url_for("home"))

# Route to get possible words
@app.route("/get_possible_words", methods=["POST"])
def get_possible_words():
    data = request.get_json()
    letters = data.get("letters", "")
    print(data)

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
               "content": "you are a scrabble player given a series of letters come up with some words to play"
            },
            {
                "role": "user",
                "content": letters
            }
        ],
        max_tokens=100,
        n=1,
    )
    possible_words = response.choices[0].message.content
    print(response.choices[0].message.content)

    return jsonify({"words": possible_words})

if __name__ == "__main__":
    app.run(debug=True)
