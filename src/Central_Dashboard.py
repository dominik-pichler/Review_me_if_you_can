import os
from LBR_Handler import identify_best_cleaners,identify_best_appartments,identify_central_appartments,identify_central_cleaners
import streamlit as st
import pandas as pd


data3 = {
    'Rank': [1, 2, 3, 4],
    'Name': ['Grace', 'Heidi', 'Ivan', 'Judy'],
    'Score': [92, 89, 84, 80]
}

# Create dataframes
df1 = identify_best_cleaners()  # Assuming this returns a DataFrame similar to data1
df2 = identify_best_appartments()
df3 = identify_central_cleaners()
df4 = identify_central_appartments()

# Streamlit app layout
st.title("Leaderboard Display")

# Define a common style for all tables
table_style = [
    {'selector': 'thead th',
     'props': [('background-color', '#f4f4f9'),
               ('color', '#333'),
               ('font-weight', 'bold'),
               ('border-bottom', '2px solid #ddd')]},
    {'selector': 'tbody tr:nth-child(even)',
     'props': [('background-color', '#f9f9f9')]},
    {'selector': 'tbody tr:hover',
     'props': [('background-color', '#e0e0e0')]}
]


# Function to display leaderboard with expand option
def display_leaderboard(title, df):
    st.subheader(title)

    # Display top 5 rows initially (or fewer if the DataFrame has less than five rows)
    st.table(df.head(5).style.set_table_styles(table_style).hide(axis='index'))

    # Expander for full leaderboard
    with st.expander("Show full leaderboard"):
        st.table(df.style.set_table_styles(table_style).hide(axis='index'))


# Display each leaderboard below each other without index
display_leaderboard("Best-Performing Cleaners (Review-based)", df1)
display_leaderboard("Best-Performing Appartments (Review-based)", df2)
display_leaderboard("Central Cleaners in \"digusting\" cleanings ", df3)
display_leaderboard("Central Cleaners in \"digusting\" appartements", df4)
