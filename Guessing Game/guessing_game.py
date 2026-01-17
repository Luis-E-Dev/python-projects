# This script imeplements a number guessing game using Python.

# Importing the random module to generate random numbers
import random

def generate_random_number():
    """
    Generate a random number between 1 and 100
    Returns:
        int: A randomly selected number.
    """
    return random.randint(1, 100)

def get_user_guess():
    """
    Prompts the users to enter a guess and validates the input.
    Returns:
        int: The user's valid guess.
    """
    while True:
        try:
            guess = int(input("Enter your guess (between 1 and 100): "))
            if 1 <= guess <= 100:
                return guess
            else:
                print("Please enter a number within the range of 1 to 100.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def play_game():
    """
    Runs the number guessing game.
    The user attempts to guess the randomly generated number within 5 tries.
    """
    print("Welcome to the Number Guessing Game!")
    print("You have 5 attempts to guess the number between 1 and 100.")
    random_number = generate_random_number()

    for i in range(5):
        print(f"Attempt {i+1}")
        user_guess = get_user_guess()
        if user_guess < random_number:
            print("Too low!")
        elif user_guess > random_number:
            print("Too high!")
        else:
            print(f"Congratulations! You've guessed the number {random_number} correctly in {i+1} attempts.")
            break
    else:
        print(f"Sorry, you've used all your attempts. The correct number was {random_number}.")

play_game()