import pymongo  
import os
import json
import re
from datetime import datetime

client = pymongo.MongoClient("")
db=client["medical_data"]
collection = db["timeline"]

base_path = ""
timeline_json_path = 'json/timeline'

#open all files in timeline directory
files = [f for f in os.listdir(timeline_json_path) if os.path.isfile(os.path.join(timeline_json_path, f))]

doc = {'patient_name':'', 'activity': '', 'doctors':[], 'date':''}
date_pattern = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")

def db_management():
  global doc
  document_count = collection.count_documents(doc)
  if document_count == 0:
    result = collection.insert_one(doc)
    doc = {'patient_name':'', 'activity': '', 'doctors':[], 'date':''}

def proc_line(lines, name):
  global doc
  doc["patient_name"] = name
  prop_value_activity = ''
  prop_value_doctor = ''
  prop_value_date = ''
  for line in lines:
    if line["spans"][0]["font"] == 'DejaVuSerifCondensed-Bol':
      prop_value_activity = prop_value_activity + line["spans"][0]["text"] + ' '
    elif line["spans"][0]["font"] == 'DejaVuSerifCondensed' and (not date_pattern.search(line["spans"][0]["text"])):
      prop_value_doctor = prop_value_doctor + line["spans"][0]["text"] + ' '
    elif line["spans"][0]["font"] == 'DejaVuSerifCondensed' and date_pattern.search(line["spans"][0]["text"]):
      prop_value_date = prop_value_date + line["spans"][0]["text"] + ' '

  if prop_value_activity != '':
    doc["activity"] = prop_value_activity[:-1]
  if prop_value_doctor != '':
    doc["doctors"] = []
    prop_value_doctor = prop_value_doctor[:-1]
    prop_value_doctor = prop_value_doctor.replace('.', '')
    doc["doctors"] = prop_value_doctor.split('/')
  if prop_value_date != '':
    prop_value_date = prop_value_date[:-1]
    doc["date"] = datetime.strptime(prop_value_date, '%m/%d/%Y')
    db_management()

def proc_data(data):
  patient_name = ''
  for page in data:
    for block in page["blocks"]:
      if block.get('lines') is not None:
        if patient_name == '':
          for line in block["lines"]:
            patient_name = line["spans"][0]["text"]
            break
        else:
          proc_line(block["lines"], patient_name)

def main():
  for file in files:
    print(f"processing {file}")
    data = []
    with open(os.path.join(timeline_json_path,file), 'r') as json_file:
      data = json.load(json_file)
    
    proc_data(data)

if __name__ == "__main__":
    # Run the main function
    main()
    print("done")








