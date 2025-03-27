from dataiku.customrecipe import get_recipe_config, get_input_names, get_output_names
import pandas as pd
from ocr_plugin import main

# Get recipe inputs
config = get_recipe_config()
bucket_name = config.get("bucket_name")
prefix = config.get("prefix", "")
file_type = config.get("file_type").lower()
prompt = config.get("prompt")

# Perform OCR and information extraction
extracted_info = main(bucket_name, prefix, file_type, prompt)

# Prepare the output dataset
output_df = pd.DataFrame([{"Extracted Information": extracted_info}])
output_dataset = dataiku.Dataset(get_output_names()[0])
output_dataset.write_with_schema(output_df)
