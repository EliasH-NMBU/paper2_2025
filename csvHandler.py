import csv
import os
from datetime import datetime

DATE = datetime.now().strftime("%Y%m%d")


def load_and_validate_csv(filepath: str):

    required_columns = ["ID", "NL description", "FRETish", "LTL"]

    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}") 

    with open(filepath, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)

        # Normalize header names (strip spaces, handle BOM)
        headers = [h.strip() for h in reader.fieldnames or []]

        # Verify all required columns
        missing = [col for col in required_columns if col not in headers]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        # Normalize data rows
        data = []
        for row in reader:
            clean_row = {k.strip(): (v.strip() if v else "") for k, v in row.items()}
            data.append(clean_row)

    print(f"✅ Loaded {len(data)} rows successfully.")
    return data


def get_master_variable_table_info():

    return (
        "Variable Mapping Table:\n"
        "------------------------\n"
        "Alert (Output, boolean): Mitigation to sound an alert under determined condition.\n"
        "Classifier (Input, integer): Identification variable for human detected by system. 0 = None, 1 = worker, 2 = untrained person\n"
        "dgt_3 (Internal, boolean): Critical threshold in distance (3 meters).\n"
        "dgt_7 (Internal, boolean): Critical threshold in distance (7 meters).\n"
        "distance_to_target (Input, integer): Distance to identified human in meters.\n"
        "Halt (Output, boolean): Mitigation to stop the robot.\n"
        "OpState (Output, integer): Current active mitigation state. From 0 to 3\n"
        "Slowdown (Output, boolean): Mitigation to slow down the robot.\n"
        "TurnoffUVC (Output, boolean): Mitigation to turn off UV lights.\n"
    )


def save_results_to_csv(results, output_path=None):

    # Ensure directory exists
    os.makedirs("results", exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d%H%M%S")

    # Default filename
    if output_path is None:
        output_path = f"results/{date_str}_ptLTL_results.csv"

    fieldnames = ["ID", "ptLTL", "Generated ptLTL", "Equivalence Check"]

    with open(output_path, mode="w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ Results saved to {output_path}")


if __name__ == "__main__":
    # Test the function
    filepath = "masterFiles/masterUseCaseReq.csv"  # Replace with your CSV file path
    try:
        data = load_and_validate_csv(filepath)
        for entry in data:
            print(entry)

        print("Test data acquasition: ", data[0]["NL description"])  # Example access
    except Exception as e:
        print(f"Error: {e}")