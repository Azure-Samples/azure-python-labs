# Python & Visual Studio Code in the browser with vscode.dev

[vscode.dev](https://vscode.dev/) is a lightweight version of [Visual Studio Code](https://code.visualstudio.com/) that runs fully in the browser, providing the ability to navigate files and repositories, and it's ideal for committing lightweight code changes.

In this lab, we will go through the process of creating and running Python code in Jupyter Notebooks on the browser. We'll create a simplified version of the popular [wordle](https://www.nytimes.com/games/wordle/index.html) game.

## Setup

1. Open a compatible browser (Chrome, Edge, Firefox or Safari).
1. Navigate to <https://vscode.dev>
1. Open the extensions view (`Ctrl + Shift + X` or `⌘ + Shift + X`) and search for the **vscode-pyodide** extension, published by  **joyceerhl**. Then click on the install button.

## Create a notebook

1. Open the command palette (`Ctrl + Shift + P` or `⌘ + Shift + P`) and run the "Create: New File..." command.
1. Select "Jupyter Notebook (.ipynb support)".
1. Add a new markdown cell by clicking on the "+ Markdown" button, and give your notebook a title. For example:
    ```
    # Wordle @ PyCon US 2022
    ```
1. Press `Shift + Enter` to leave the cell edit mode.

## Write Python code

1. Start by setting up the game. Create a new code cell by clicking on the "+ Code" button, or be pressing `Ctrl + Enter` or `⌘ + Enter` in an existing Code cell, and add the following imports:

    ```python
    import json
    import random
    from base64 import b64decode, b64encode

    from js import fetch
    ```

1. Then fetch the eligible answer words for our game. This is just a list of the words that we will try to guess when we play the game. They're encoded so we're not tempted to get any spoilers.

    Add the following code to the notebook:

    ```python
    res = await fetch("https://raw.githubusercontent.com/luabud/wordle/main/encoded_words.json")
    res_text = await res.text()
    json_words = json.loads(res_text)
    encoded_words = json_words["encoded_words"]
    ```

1. Continue with the setup by declaring a few important elements of the game, like how many turns it takes to end the game (GAME_LENGTH), the current turn, the previous guesses (to include progress in the output), and the answer word, being randomly selected from the list of eligible words we fetched in the previous step.


    ``` python
    GAME_LENGTH = 5
    current_turn = 0
    previous_guesses = {i+1 : "" for i in range(GAME_LENGTH)}
    answer_word = random.choice(encoded_words)
    ```

1. And now let's set up a few methods to validate input and to check if the game should be over. Feel free to edit this code to include any checks you'd like to have.

    ```python
    def game_over(status):
        if status == "win":
            print("Congratulations, you guessed correctly!")
        else:
            print(f"Sorry, you lost. The correct word was {answer_word}.")

        current_turn = 0
        return

    def wrong_guess_length(guess_word):
        if(len(guess_word) < 5):
            print("Not enough characters.")
        else:
            print("Too many characters.")
        print("Try a guess with 5 letters.")

    def is_right_guess(guess, word):
        return str(b64encode(guess.encode("utf-8")), "utf-8") == word
    ```

1. Now we will set up the method to print output, to indicate the progress of the game and provide feedback on which letters were in the right position, which letters are in the answer word but not in the guessed position, and which letters are not in the answer word.

    For each letter in the word you passed as a guess, you would see:

    - `_` if the letter isn't in the answer.
    - The letter between `()` if it is in the answer word but in another position.
    - The letter itself when you get it in the right position.

    This is the representation we chose for our game, but you can feel free to change it to something different if you'd like! Just make sure to add a markdown cell (by clicking on the `+ Markdown` button) to your notebook describing it, so others (or the future you!) can understand it when they try to run your notebook. 
    
    Add the following code:

    ```python
    def print_output(guess_word, green_letters, yellow_letters, gray_letters):
        output = []
        for i, g in enumerate(guess_word):
            pair = i, g
            if pair in green_letters:
                output.append(g)
            elif pair in yellow_letters:
                output.append(f"({g})")
            else:
                output.append("_")

        previous_guesses[current_turn] = " ".join(output)
        for i in previous_guesses.keys():
            print(f"{i} : {previous_guesses[i]}")
    ```

1. Last but not least, add the code for the game! We first check all the letters that were guessed in the right position (green_letters), then the ones that exist in the answer word but are in the wrong position (yellow_letters), and then finally we check the ones that are not in the answer word (gray_letters).

    ```python
    def guess_word(guess_word):

        if len(guess_word) != 5:
            return wrong_guess_length(guess_word)

        global current_turn
        current_turn += 1

        if current_turn > GAME_LENGTH:
            return game_over("lose")

        answer_pairs = set(enumerate(str(b64decode(answer_word),  "utf-8")))
        guess_pairs = set(enumerate(guess_word))

        green_letters = answer_pairs & guess_pairs

        answer_pairs -= green_letters
        guess_pairs -= green_letters

        yellow_letters = set()
        for guess in guess_pairs:
            for answer in answer_pairs:
                if guess[1] == answer[1]:
                    answer_pairs.remove(answer)
                    yellow_letters.add(guess)
                    break

        gray_letters = guess_pairs - yellow_letters

        print_output(guess_word, green_letters, yellow_letters, gray_letters)

        if is_right_guess(guess_word,answer_word):
            return game_over("win")
        if current_turn == GAME_LENGTH:
            return game_over("lose")
    ```

## Run your code & play the game!

1. Run the cell(s) with the code you added in the previous step by clicking on the run button, or by pressing `Shift + Enter`. Then create a new cell and call the `guess_word()` method passing your first guess. For example:

    ```python
    guess_word("ghost")
    ```

1. Add a new cell with a new guess depending on the feedback you get from the output, until the game is over! To play it again, run the first cells to reset it.
