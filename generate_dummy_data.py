import pandas as pd
import yaml
from faker import Faker
import sys

def generate_fake_data(yaml_file, output_file, num_rows=100):
    # Initialize Faker
    fake = Faker()

    # Read the YAML file
    with open(yaml_file, 'r') as file:
        config = yaml.safe_load(file)

    # Extract column names
    columns = list(config['columns'].keys())

    # Generate dummy data
    data = []
    for _ in range(num_rows):
        row = []
        for column in columns:
            if 'date' in column.lower():
                row.append(fake.date())
            elif 'email' in column.lower():
                row.append(fake.email())
            elif 'phone' in column.lower():
                row.append(fake.phone_number())
            elif 'name' in column.lower():
                row.append(fake.name())
            elif 'address' in column.lower():
                row.append(fake.address())
            elif 'zip' in column.lower():
                row.append(fake.zipcode())
            elif 'state' in column.lower():
                row.append(fake.state_abbr())
            elif 'country' in column.lower():
                row.append(fake.country_code())
            elif 'gender' in column.lower():
                row.append(fake.random_element(elements=("M", "F")))
            elif 'ethnicity' in column.lower():
                row.append(fake.random_element(elements=("Hispanic", "Non-Hispanic")))
            elif 'race' in column.lower():
                row.append(fake.random_element(elements=("White", "Black", "Asian", "Other")))
            elif 'language' in column.lower():
                row.append(fake.language_name())
            elif 'relationship' in column.lower():
                row.append(fake.random_element(elements=("Self", "Spouse", "Child", "Other")))
            elif 'marital' in column.lower():
                row.append(fake.random_element(elements=("Single", "Married", "Divorced", "Widowed")))
            else:
                row.append(fake.uuid4())
        data.append(row)

    # Create DataFrame
    df = pd.DataFrame(data, columns=columns)

    # Save to CSV
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_fake_data.py <yaml_file> <output_file>")
    else:
        yaml_file = sys.argv[1]
        output_file = sys.argv[2]
        generate_fake_data(yaml_file, output_file)