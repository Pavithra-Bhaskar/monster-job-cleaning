import pandas as pd
import re

# df = pd.read_csv('data/raw_jobs.csv')

# print("=====Head=====")
# print(df.head())

# print("\n=====Info=====")
# print(df.info())

# print("\n======Null Values=====")
# print(df.isnull().sum())

# # TASK1 : STANDARDIZE COLUMN NAMES 

# df.columns = [col.strip().lower().replace(" ","_") for col in df.columns]

# print(df.columns)

# # TASK2 : DROP DUPLICATE ROWS

# before = df.shape[0]
# df = df.drop_duplicates()
# after = df.shape[0]

# print(f"Removed {before - after } duplicate rows.")

# # TASK 3

# df["location"] = df["location"].str.strip().str.title()

# print(df["location"].unique())

# -----------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------

# NOTICED A CLASSIC CSV FORMATTING ISSUE i.e, CSV has commas inside quoted text (like in job descriptions)
# and Pandas is: 1 not detecting the correct delimiter or not parsing the quotes properly

df = pd.read_csv(
    'data/raw_jobs.csv',
    delimiter=',',             # Use default comma separator
    quotechar='"',             # Handle fields enclosed in quotes
    encoding='utf-8',          # Safe default encoding
    error_bad_lines=False,     # Skip broken lines
    warn_bad_lines=True        # Warn you if any rows were skipped (if using old Pandas)
)


# print("✅ Columns:", df.columns.tolist())
# print("✅ Shape:", df.shape)
# print("\n✅ First 2 Rows:\n", df.head(2).to_string())

# --- CLEAN job_description FIELD ---
def clean_description(text):
    if pd.isnull(text):
        return ""
    
    text = text.replace('\xa0', ' ')                   # Replace non-breaking spaces
    text = re.sub(r'\s+', ' ', text)                   # Collapse all whitespace (tabs, newlines)
    text = re.sub(r'[•●]', '-', text)                  # Convert bullet characters
    text = text.strip()                                # Remove leading/trailing spaces
    return text

df['job_description_clean'] = df['job_description'].apply(clean_description)

# --- PREVIEW RESULTS ---
# print("✅ Cleaned job_description sample:\n")
# print(df[['job_description', 'job_description_clean']].head(1).to_string())

# --- CLEAN location FIELD ---
def clean_location(location):
    # Handle missing values
    if pd.isnull(location):
        return pd.Series([None,None,None])
    
    # split city and state+zip
    # split on first comma
    parts = location.split(",")
    if len(parts) < 2:
        return pd.Series([location.strip(),None,None])
    
    city = parts[0].strip()
    state_zip = parts[1].strip().split()

    # split state and zip
    state = state_zip[0] if len(state_zip) >= 1 else None
    zip = state_zip[1] if len(state_zip) == 2 else None

    return pd.Series([city,state,zip])
 
# Apply to DataFrame
df[['city', 'state', 'zip_code']] = df['location'].apply(clean_location)

# Preview
# print(df[['location', 'city', 'state', 'zip_code']])
#Note: ROW2 has corrupt or misplaced value in the location field.(handled later)

print(df.columns)

# 🧠 Why Are the Column Names Still Standardized Even If You Comment That Line Out?
# Short Answer:
# Because you already ran the code once, and your current Python session (or your VS Code terminal) still holds that modified version of df in memory — even if you've since commented it out.

# --- CLEAN salary_str FIELD ---

def clean_salary(salary_str):
    if pd.isnull(salary_str):
        return pd.Series([None,None])
    
    #remove currency signs and commas
    salary_str = salary_str.replace("$","").replace(",","").lower()

    #extract numerical salary range e.g., "60000 - 80000"
    numbers = re.findall(r'\d+(?:\.\d+)?',salary_str)
    numbers = (float(n) for n in numbers)

    if 'hour' in salary_str or 'hr' in salary_str:
         # Assume hourly rates, convert to yearly (approximate) 40hrs/week 52 weeks
        numbers = [round(n*40*52) for n in numbers]

    if not numbers == 0:
        return pd.Series([None,None])
    if len(numbers) == 1:
        return pd.Series([numbers,numbers])
    else:
        return pd.Series([min(numbers), max(numbers)])
    
df[['salary_min', 'salary_max']] = df['salary'].apply(clean_salary)

print(df[['salary', 'salary_min', 'salary_max']].head(10))
# displayed all naan , none ,none

print(df['salary'].isnull().sum(), "missing salary values out of", len(df))
# 18554 missing salary values out of 22000

valid_salaries = df[df['salary'].notnull()][['salary', 'salary_min', 'salary_max']]
print(valid_salaries.head(10).to_string())

