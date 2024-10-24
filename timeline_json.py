import fitz  # Import PyMuPDF
import os
import json

base_path = ""
timeline_pdf_path = 'pdf/timeline'
timeline_json_path = 'json/timeline'

#open all files in timeline directory
files = [f for f in os.listdir(timeline_pdf_path) if os.path.isfile(os.path.join(timeline_pdf_path, f))]

for file in files:
  file_name_with_extension = os.path.basename(file)
  file_name, file_extension = os.path.splitext(file_name_with_extension)
  
  pdf_document = fitz.open(os.path.join(timeline_pdf_path,file))
  pages_data = []
  # Iterate through each page
  for page_num in range(len(pdf_document)):
    # Get a page
    page = pdf_document.load_page(page_num)

    # Extract text from the page
    text = page.get_text("json")
    pages_data.append(json.loads(text))
  
  json_filename = file_name + ".json"
  with open(os.path.join(timeline_json_path, json_filename), "w", encoding="utf-8") as f:
    json.dump(pages_data, f, indent=2)

  # Close the document
  pdf_document.close()    
  print(f"done {file_name}")








