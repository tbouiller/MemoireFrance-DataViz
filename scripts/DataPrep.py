import pandas as pd
import glob

# Get a list of annotation files
annotation_files = glob.glob('data/cummun/*.csv')

# Read and concatenate the dataframes from the annotation files
annotated_dataframes = [pd.read_csv(file, on_bad_lines='skip', encoding='latin-1', sep=';') for file in annotation_files]
df = pd.concat(annotated_dataframes)

# Count the number of NaN values in each row
df['nan_counts'] = df.isna().sum(axis=1)

# Sort the dataframe by nan_counts in ascending order
df_sorted = df.sort_values(by='nan_counts')

# Drop duplicates based on a specific column, keeping rows with the least NaN values
clean_df = df_sorted.drop_duplicates(subset='c_id_primaire_fiche')

# Reset the index of the resulting dataframe
clean_df.reset_index(drop=True, inplace=True)

# Define the date columns for death and birth dates
death_dates = ['annot_deces_jour_mois_annee_yyyy', 'annot_deces_jour_mois_annee_mm', 'annot_deces_jour_mois_annee_dd']
birth_dates = ['c_naissance_jour_mois_annee_yyyy', 'c_naissance_jour_mois_annee_mm', 'c_naissance_jour_mois_annee_dd']

# Convert the date columns to the 'Int64' data type
clean_df[death_dates] = clean_df[death_dates].astype('Int64')
clean_df[birth_dates] = clean_df[birth_dates].astype('Int64')

# Create new date columns using the concatenated year, month, and day columns
clean_df['pd_death_date'] = pd.to_datetime(clean_df[death_dates].astype(str).agg('-'.join, axis=1), errors='coerce')
clean_df['pd_birth_date'] = pd.to_datetime(clean_df[birth_dates].astype(str).agg('-'.join, axis=1), errors='coerce')

# Calculate the age at death by subtracting birth date from death date
clean_df['age_at_death'] = (clean_df['pd_death_date'] - clean_df['pd_birth_date'])


clean_df.to_csv('mdf_df.csv')
