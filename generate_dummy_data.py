import pandas as pd
import yaml
from faker import Faker
import sys
import random
import string
from utils import generate_medicaid_id, get_supported_states

def generate_medicare_id():
    # Define the allowed characters
    letters = ''.join(set(string.ascii_uppercase) - set('SLOIBZ'))
    numbers = '123456789'

    # Generate the Medicare ID
    medicare_id = [
        random.choice(numbers),  # 1st character
        random.choice(letters),  # 2nd character
        random.choice(numbers),  # 3rd character
        random.choice(numbers),  # 4th character
        random.choice(letters),  # 5th character
        random.choice(numbers),  # 6th character
        random.choice(numbers),  # 7th character
        random.choice(letters),  # 8th character
        random.choice(letters),  # 9th character
        random.choice(numbers),  # 10th character
        random.choice(numbers)   # 11th character
    ]

    return ''.join(medicare_id)

def get_supported_state():
    return random.choice(get_supported_states())

def generate_member_id():
    prefix = "MEMB"
    number = ''.join(random.choices('0123456789', k=11))
    return f"{prefix}{number}"

def generate_name_details(fake: Faker, gender: str) -> dict:
    if gender == "1":
        full_name = fake.name_male()
        prefix = fake.prefix_male()
        suffix = fake.suffix_male()
    else:
        full_name = fake.name_female()
        prefix = fake.prefix_female()
        suffix = fake.suffix_female()

    name_parts = full_name.split()
    return {
        "first_name": name_parts[0],
        "middle_name": name_parts[1] if len(name_parts) > 2 else "",
        "last_name": name_parts[-1],
        "prefix": prefix,
        "suffix": suffix,
        "full_name": full_name
    }

def generate_fake_data(yaml_file, output_file, num_rows=800):
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
        state = get_supported_state()
        gender = fake.random_element(elements=("1", "2"))  # 1 for
        name_details = generate_name_details(fake, gender)
        dob = fake.date_of_birth(minimum_age=18, maximum_age=98)
        for column in columns:
            if 'date' in column.lower() and 'birth' in column.lower() or 'dob' in column.lower():
                row.append(dob)
            elif 'date' in column.lower() and 'death' in column.lower():
                age = (pd.Timestamp.now() - pd.Timestamp(dob)).days // 365
                if age > 95:
                    death_date = dob + pd.DateOffset(years=random.randint(70, 95))
                    row.append(death_date.strftime('%Y%m%d'))
                else:
                    if random.random() < 0.2:
                        death_date = dob + pd.DateOffset(years=random.randint(70, 95))
                        row.append(death_date.strftime('%Y%m%d'))
                    else:
                        row.append('')
            elif 'email' in column.lower():
                row.append(fake.email())
            elif 'phone' in column.lower():
                row.append(fake.phone_number())
            elif 'name' in column.lower() and 'first' in column.lower():
                row.append(name_details['first_name'])
            elif 'name' in column.lower() and 'last' in column.lower():
                row.append(name_details['last_name'])
            elif 'name' in column.lower() and 'middle' in column.lower():
                row.append(name_details['middle_name'])
            elif 'name' in column.lower() and 'prefix' in column.lower():
                row.append(name_details['prefix'])
            elif 'name' in column.lower() and 'suffix' in column.lower():
                row.append(name_details['suffix'])
            elif 'name' in column.lower() and 'preferred' in column.lower():
                row.append(name_details['full_name'])
            elif 'address' in column.lower():
                row.append(fake.street_address())
            elif 'city' in column.lower():
                row.append(fake.city())
            elif 'state' in column.lower():
                row.append(state)
            elif 'zip' in column.lower():
                row.append(fake.zipcode())
            elif 'country' in column.lower():
                row.append(fake.country_code())
            elif 'gender' in column.lower():
                row.append(gender)  # 1 for Male, 2 for Female
            elif 'ethnicity' in column.lower():
                row.append(fake.random_element(elements=("Hispanic", "Caucasian", "African American", "Asian", "Not Provided", "", "American Indian", "Pacific Islander")))
            elif 'race' in column.lower():
                row.append(fake.random_element(elements=("White (Non-Hispanic)", "Black or African American", "Asian or Pacific Islander", "Other")))
            elif 'language' in column.lower():
                row.append(fake.random_element(elements=("English", "Spanish", "Vietnamese", "Russian", "Chinese Cantonese", "Khmer", "Korean", "Arabic", "Persian", "Hmong", "French", "German")))
            elif 'relationship' in column.lower():
                row.append(fake.random_element(elements=("Self", "Spouse", "Child")))
            elif 'marital' in column.lower():
                row.append(fake.random_element(elements=("Single", "Married", "Divorced", "Widowed")))
            elif 'medicare' in column.lower():
                row.append(generate_medicare_id())
            elif 'medicaid' in column.lower():
                row.append(generate_medicaid_id(state))
            elif 'memberid' in column.lower() or 'member_id' in column.lower():
                row.append(generate_member_id())
            else:
                row.append(fake.uuid4())
        data.append(row)

    # Create DataFrame
    df = pd.DataFrame(data, columns=columns)

    # Save to CSV
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_dummy_data.py <yaml_file> <output_file>")
    else:
        yaml_file = sys.argv[1]
        output_file = sys.argv[2]
        generate_fake_data(yaml_file, output_file)