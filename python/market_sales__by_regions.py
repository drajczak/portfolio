import pandas as pd
import os

# Month and year of the report
year_month = "2024-09"

# Load the xlsx file
xlsx_path = rf'K:\Mój dysk\Arkusze\Analiza Rynku Maszyn Budowlanych\_Analiza rynku maszyn budowlanych {year_month}.xlsx'
df = pd.read_excel(xlsx_path, sheet_name='dane', usecols=('kategoria', 'sekcja', 'wojewodztwo', 'okres', 'liczba'))

# Convert the "okres" column to text format representing the report period
df['okres'] = year_month

# Remove rows from the "kategoria" column that contain specific words
categories_to_remove = ['STABILIZATORY', 'FREZARKI', 'ROZŚCIEŁACZE', 'WALCE', 'RÓWNIARKI', 'SPYCHARKI', 'TELESKOPOWE', 'KOPARKO ŁADOWARKI', 'MINI', 'SZTYWNORAMOWE']
df = df[~df['kategoria'].str.contains('|'.join(categories_to_remove))]

# Remove rows in the category 'ŁADOWARKI KOŁOWE' from sections 0 - 120 KM
df = df[~((df['kategoria'] == 'ŁADOWARKI KOŁOWE  (<150KM)') & ((df['sekcja'] == '0 < 30 KM') | (df['sekcja'] == '30 < 60 KM') | (df['sekcja'] == '60 < 70 KM') | (df['sekcja'] == '70 < 80 KM') | (df['sekcja'] == '80 < 100 KM') | (df['sekcja'] == '100 < 120 KM'))) ]

# Remove rows where the "liczba" column is 0
df = df[df['liczba'] != 0]

# Duplicate rows for values greater than 1 in the "liczba" column
while True:
    mask = df['liczba'] > 1
    if not mask.any():
        break
    new_rows = df[mask].copy()
    new_rows['liczba'] = 1
    df.loc[mask, 'liczba'] -= 1
    df = pd.concat([df, new_rows], ignore_index=True)

# Create new columns
df['PH'] = ''
df['Maszyna'] = ''
df['Klient'] = ''
df['Uwagi'] = ''

# Create a new dictionary with salespeople's initials and their regions
sales_regions = {
    'JKU': ['LUBUSKIE', 'ZACHODNIOPOMORSKIE', 'WIELKOPOLSKIE'],
    'PKO': ['LUBELSKIE', 'PODKARPACKIE', 'ŚWIĘTOKRZYSKIE'],
    'AKU': ['ŚLĄSKIE', 'OPOLSKIE'],
    'ŁKR': ['ŁÓDZKIE', 'ŚLĄSKIE'],
    'JKR': ['MAZOWIECKIE'],
    'MKI': ['WARMIŃSKO_MAZURSKIE', 'KUJAWSKO_POMORSKIE', 'POMORSKIE'],
    'ŁKA': ['DOLNOŚLĄSKIE', 'LUBUSKIE', 'OPOLSKIE'],
    'PKL': ['MAŁOPOLSKIE'],
    'PSZ': ['PODLASKIE', 'WARMIŃSKO_MAZURSKIE'],
}

# Check if the target folder exists
folder_path = rf"K:/Mój dysk/Arkusze/Analiza Rynku Maszyn Budowlanych/DOSTARCZONE/{year_month}/PUSTE"
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Create a dictionary with new DataFrames
new_dfs = {}
for key, regions in sales_regions.items():
    # Select rows that match values in the 'wojewodztwo' column from the dictionary
    new_df = df[df['wojewodztwo'].isin(regions)].copy()
    # Sort the DataFrame by 'kategoria' and 'sekcja'
    new_df.sort_values(by=['kategoria', 'sekcja'], inplace=True)
    # Fill the 'PH' column with the key from the dictionary;
    new_df.loc[:, 'PH'] = key
    # Add the new DataFrame to the dictionary using the dictionary key
    new_dfs[key] = new_df

    # Create an Excel file for the given DataFrame
    filename = f'{folder_path}/{year_month}_DOSTARCZONE_{key}.xlsx'
    with pd.ExcelWriter(filename) as writer:
        new_df.to_excel(writer, index=False)

# Save the main DataFrame sorted by 'kategoria' and 'sekcja'
df.sort_values(by=['kategoria', 'sekcja'], inplace=True)

# Save the final file
output_path = rf'K:/Mój dysk/Arkusze/Analiza Rynku Maszyn Budowlanych/DOSTARCZONE/{year_month}/{year_month} DOSTARCZONE.xlsx'
df.to_excel(output_path, index=False)
print(f'Report files generated for {year_month}')

