import csv
import json

def dicts_to_csv(data, filename):
    if not data:
        return
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

data = None
with open("EMA_Feature_Comparison.json", "r") as f:
    data = json.load(f)

output_filename = 'EMA_Feature_Comparison.csv'
dicts_to_csv(data, output_filename)
