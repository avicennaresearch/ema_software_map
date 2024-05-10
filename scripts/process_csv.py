import pandas as pd

CSV_PATH = 'EMA_Feature_Comparison.csv'
# Load the CSV file
df = pd.read_csv(CSV_PATH)

# Function to split long text
def split_long_text(text, max_length):
    return '\n'.join([text[i:i+max_length] for i in range(0, len(text), max_length)])

# Apply the function to each cell in the dataframe
for col in df.columns:
    df[col] = df[col].apply(lambda x: split_long_text(str(x), 60) if len(str(x)) > 60 else x)

# Save the modified CSV
df.to_csv(CSV_PATH, index=False)