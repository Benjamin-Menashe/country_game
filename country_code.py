import streamlit as st
import pandas as pd
import shutil
import os

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
@st.cache_resource
def load_country_data():
    return pd.read_csv('current_game_countries.csv') if os.path.exists('current_game_countries.csv') else pd.DataFrame()

# Function to save the modified data back to the copy CSV file
def save_game_copy():
    country_data.to_csv('current_game_countries.csv', index=False)

# Initialize the copy of the original CSV file for the current game
create_game_copy()

# Load the current country data and create the letter bank
country_data = load_country_data()  # Load the copy for the current game
letter_bank = create_letter_bank(country_data)  # Initialize the letter bank

# Initialize a set to keep track of played countries
if 'played_countries' not in st.session_state:
    st.session_state.played_countries = set()

# Function to suggest a country based on the last letter of the input country
def suggest_country(input_country, letter_bank):
    last_letter = input_country[-1].lower()
    
    if last_letter in letter_bank:
        available_countries = country_data[country_data['first_letter'] == last_letter]
        
        if len(available_countries) > 1:
            min_last_letter_count = float('inf')
            suggested_country = ""
            
            for country in available_countries['country'].tolist():
                if country not in st.session_state.played_countries:
                    count = letter_bank.get(country[-1], float('inf'))
                    if count < min_last_letter_count:
                        min_last_letter_count = count
                        suggested_country = country

            if suggested_country:
                st.session_state.played_countries.add(suggested_country)
                country_data.drop(country_data[country_data['country'] == suggested_country].index, inplace=True)
                save_game_copy()
                return suggested_country

        # If only one country with the given first letter is left, suggest it
        elif len(available_countries) == 1:
            last_country = available_countries.iloc[0]['country']
            if last_country not in st.session_state.played_countries:
                st.session_state.played_countries.add(last_country)
                country_data.drop(country_data[country_data['country'] == last_country].index, inplace=True)
                save_game_copy()
                return last_country

    return f"You win!!! No country left that begins with {last_letter}"

st.title("Eden's Country Game")

if st.button("New Game"):
    input_country = ""
    delete_game_copy()
    st.cache_resource.clear()
    create_game_copy()
    st.session_state.played_countries.clear()  # Clear the set of played countries
    st.session_state.turn = 0
    st.write("New game started!")
    
input_country = st.text_input("Enter a country:", input_country).strip().lower()

if 'turn' not in st.session_state:
    st.session_state.turn = 0

if input_country:
    input_country_lower = input_country.lower()
    if input_country_lower in country_data['country'].str.lower().tolist():
        st.session_state.played_countries.add(input_country_lower)
        country_data.drop(country_data[country_data['country'].str.lower() == input_country_lower].index, inplace=True)
        letter_bank = create_letter_bank(country_data)
        last_letter = input_country_lower[-1].lower()
        suggested_country = suggest_country(input_country_lower, letter_bank)
        st.write(f"Suggested Country: {suggested_country}")
        st.session_state.turn += 1
    else:
        st.write("Error, country not found")
        if input_country_lower in st.session_state.played_countries:
            st.write(f"{input_country_lower} was already used in this game")

st.write(f"Turns taken: {st.session_state.turn}")
