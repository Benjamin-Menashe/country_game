import streamlit as st
import pandas as pd
import shutil  # For copying the CSV file
import os     # For file deletion

# Function to create a copy of the original CSV file for the current game
def create_game_copy():
    shutil.copy('countries.csv', 'current_game_countries.csv')

# Function to delete the copy of the CSV file for the current game
def delete_game_copy():
    if os.path.exists('current_game_countries.csv'):
        os.remove('current_game_countries.csv')

# Function to create a letter bank given the current country data
def create_letter_bank(data):
    letter_bank = {}
    for _, row in data.iterrows():
        first_letter = row['first_letter']
        letter_bank[first_letter] = letter_bank.get(first_letter, 0) + 1
    return letter_bank

# Load the CSV file containing the countries and their first/last letters
@st.cache_data
def load_country_data():
    return pd.read_csv('current_game_countries.csv') if os.path.exists('current_game_countries.csv') else pd.DataFrame()

# Function to save the modified data back to the copy CSV file
def save_game_copy():
    country_data.to_csv('current_game_countries.csv', index=False)

# Initialize the copy of the original CSV file for the current game
if 'turn' not in st.session_state:
    create_game_copy()

# Load the current country data and create the letter bank
country_data = load_country_data()  # Load the copy for the current game
letter_bank = create_letter_bank(country_data)  # Initialize the letter bank

# Function to suggest a country based on the last letter of the input country
def suggest_country(input_country):
    last_letter = input_country[-1].lower()
    if last_letter in letter_bank:
        available_countries = country_data[country_data['first_letter'] == last_letter]
        if len(available_countries) > 0:
            min_last_letter_count = float('inf')
            suggested_country = ""
            for country in available_countries['country'].tolist():
                count = letter_bank.get(country[-1], float('inf'))
                if count < min_last_letter_count:
                    min_last_letter_count = count
                    suggested_country = country

            if suggested_country:
                country_data.drop(country_data[country_data['country'] == suggested_country].index, inplace=True)
                letter_bank[last_letter] -= 1
                if letter_bank[last_letter] == 0:
                    del letter_bank[last_letter]
                save_game_copy()
                return suggested_country
    return f"You win!!! No country found for {last_letter}"

st.title("Eden's Country Game")
input_country = st.text_input("Enter a country:", "").strip().lower()

if input_country:
    input_country_lower = input_country.lower()
    if input_country_lower in country_data['country'].str.lower().tolist():
        country_data.drop(country_data[country_data['country'].str.lower() == input_country_lower].index, inplace=True)
        last_letter = input_country_lower[-1].lower()
        if last_letter in letter_bank:
            letter_bank[last_letter] -= 1
            if letter_bank[last_letter] == 0:
                del letter_bank[last_letter]
        suggested_country = suggest_country(input_country_lower)
        st.write(f"Suggested Country: {suggested_country}")
        st.session_state.turn += 1
    else:
        st.write("Wrong input. The country is not in the current country bank.")

if st.button("Reset Game"):
    delete_game_copy()
    st.cache_data.clear()
    create_game_copy()
    st.session_state.turn = 0
    st.write("Game has been reset. Start a new game!")

st.write(f"Turns taken: {st.session_state.turn}")
