import os
import pandas as pd

def convert_to_excel(input_folder, output_folder):
    # Extract data from the text files
    data = []
    for file in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file)
        if file_path.endswith(".txt"):
            with open(file_path, "r") as f:
                answer = f.read()
                row_data = {"Filename": file, "Answer": answer}
                data.append(row_data)

    # Create a DataFrame from the data list
    df = pd.DataFrame(data)

    # Define the columns and reorder the DataFrame with these columns
    columns_order = ['Filename', 'Answer']
    df = df.reindex(columns=columns_order)

    # Save the DataFrame as an Excel file in the output folder
    output_file = os.path.join(output_folder, "output.xlsx")
    df.to_excel(output_file, index=False)
