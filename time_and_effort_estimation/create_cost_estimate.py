import csv

def read_csv_to_dict(filename):
    """Reads the CSV file and structures it as a dictionary."""
    data = {}
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            category = row['Category']
            if category not in data:
                data[category] = []
            data[category].append({
                "Item": row['Item'],
                "Effort in Days": float(row['Effort in Days']) if row['Effort in Days'].strip() else 0.0,
                "Rate per Hour (INR)": float(row['Rate per Hour (INR)']) if row['Rate per Hour (INR)'].strip() else 0.0,
                "Pricing (INR)": row['Pricing (INR)'].strip() if row['Pricing (INR)'].strip() else "₹0.00",
                "Tech": row['Tech'],
                "Team": int(row['Team']) if row['Team'].strip().isdigit() else 0,
                "Team Effort": float(row['Team Effort']) if row['Team Effort'].strip() else 0.0
            })
    return data

def generate_context(data):
    """Converts structured data into a context string for LLM."""
    context = "The following is structured pricing data for various applications in a medical software system:\n"
    
    for category, items in data.items():
        context += f"\nCategory: {category}\n"
        for item in items:
            context += f"- {item['Item']} requires {item['Effort in Days']} days, "
            context += f"billed at INR {item['Rate per Hour (INR)']} per hour, totaling {item['Pricing (INR)']} INR.\n"
    
    return context

def save_context_to_file(context, output_filename):
    """Saves the generated context to a text file."""
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(context)

def main():
    csv_filename = "C:/Users/Fatima/OneDrive/Desktop/AI-Powered Presales Automation/ai-model/time_and_effort_estimation/estimate_data/pricing_data.csv"
    output_filename = "cost_estimate_context.txt"
    
    data = read_csv_to_dict(csv_filename)
    context = generate_context(data)
    save_context_to_file(context, output_filename)
    
    print(f"Pricing context saved to {output_filename}")

if __name__ == "__main__":
    main()
