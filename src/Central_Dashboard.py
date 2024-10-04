import streamlit as st
import pandas as pd
import sys
from pathlib import Path

from LBR_Handler import identify_best_cleaners

# Sample data for the leaderboards
data1 = {
    'Rank': [1, 2, 3],
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Score': [95, 90, 85]
}

data2 = {
    'Rank': [1, 2, 3],
    'Name': ['David', 'Eve', 'Frank'],
    'Score': [88, 87, 86]
}

data3 = {
    'Rank': [1, 2, 3],
    'Name': ['Grace', 'Heidi', 'Ivan'],
    'Score': [92, 89, 84]
}

# Create dataframes
df1 = identify_best_cleaners()
df2 = pd.DataFrame(data2)
df3 = pd.DataFrame(data3)

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

# Display each leaderboard below each other without index
st.subheader("Leaderboard 1")
st.table(df1.style.set_table_styles(table_style).hide(axis='index'))

st.subheader("Leaderboard 2")
st.table(df2.style.set_table_styles(table_style).hide(axis='index'))

st.subheader("Leaderboard 3")
st.table(df3.style.set_table_styles(table_style).hide(axis='index'))