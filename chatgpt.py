import openai
from openai import OpenAI
import os
import time
import random
import pymongo  
from datetime import datetime
import re

db_client = pymongo.MongoClient("mongodb+srv://arbab998:wDl85YMTveO5ayrQ@cluster0.tjglijc.mongodb.net/")
db=db_client["medical_data"]
collection = db["summary"]

client = OpenAI(
    api_key='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'  # Make sure to replace this with your actual API key
)

def convert_date_format(date_string):
    # Regular expression to match dates in DD-MM-YYYY, DD/MM/YYYY, or DD/MM/YY formats
    date_pattern = r'\d{2}[-/]\d{2}[-/]\d{2,4}'
    match = re.search(date_pattern, date_string)
    
    if match:
        found_date = match.group(0)
        # Determine the correct format based on separator and year length
        separator = '-' if '-' in found_date else '/'
        year_length = 2 if len(found_date.split(separator)[-1]) == 2 else 4
        date_format = f'%m{separator}%d{separator}%y' if year_length == 2 else f'%m{separator}%d{separator}%Y'
        # Parse the found date using the determined format
        try:
            date_obj = datetime.strptime(found_date, date_format)
            # Format the date as DD/MM/YYYY
            formatted_date = date_obj.strftime('%m/%d/%Y')
            return formatted_date
        except ValueError as e:
            return "error"
    else:
        return "no valid"
    
def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    errors: tuple = (openai.RateLimitError,),
):
    """Retry a function with exponential backoff."""
 
    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay
 
        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            try:
                return func(*args, **kwargs)
 
            # Retry on specific errors
            except errors as e:
                # Increment retries
                num_retries += 1
 
                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )
 
                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())
                print(f"Rate limit exceeded. Waiting for {delay} seconds before retrying...")
                # Sleep for the delay
                time.sleep(delay)
 
            # Raise exceptions for any errors not specified
            except Exception as e:
                print(f"gpt error: {e}")
                raise e
 
    return wrapper

@retry_with_exponential_backoff
def completions_with_backoff(**kwargs):
    global client
    return client.chat.completions.create(**kwargs)

def extract_insertDB(data, file_name):
    choice = data.choices
    first_choice = choice[0]

    # Now, access the 'message' attribute of the choice, which is a ChatCompletionMessage object
    chat_message = first_choice.message

    # Finally, access the 'content' attribute of the chat_message to get the text of the message
    message_content = chat_message.content
    message_content = message_content.replace('*', '')
    main_sections = message_content.strip().split("///////////////////////")
    main_sections = list(filter(lambda x: x != '', main_sections))
    for sections in main_sections: 
        # Splitting the text based on the lines and processing them
        sections = sections.strip()
        sections = sections.strip('\n').split("\n")
        sections = list(filter(lambda x: x != '', sections))
        try: 
            if 'visit' in sections[0].lower():
                sections = sections[1:]
            if not ('patient' in sections[0].lower()):
                sections = sections[1:]
            summary = ''
            for i in range(8, len(sections)):
                summary = summary + sections[i]
            sections = sections[:8]
            sections.append(summary)
        except Exception as e:
            print(sections)
            print(f"error:{e}")
        # Processing each section into a structured format
        structured_data = []
        for section in sections:
            # Identifying sections that contain a list of items
            if "\n  - " in section:
                try:
                    key, value = section.split(":", 1)
                    list_items = value.split("\n  - ")
                    structured_data.append({key[2:].strip(): list_items})  # Removing the initial "- " from the key
                except Exception as e:
                     print(f"error:{e}")
            else:
                try:
                    key, value = section.split(":", 1)
                    structured_data.append({key[2:].strip(): value.strip()})  # Removing the initial "- " from the key
                except Exception as e:
                     print(f"error:{e}")
        # Printing the structured data for verification
        extracted_values = [list(item.values())[0] for item in structured_data]
        db_insert(extracted_values, file_name)
    return

def db_insert(data, file_name):
    try:
        visit_date = convert_date_format(data[3])
        signed_date = convert_date_format(data[7])
        if visit_date == 'error' or visit_date == 'no valid':
            if signed_date == 'error' or signed_date == 'no valid':
                return
            else:
                pattern = r'_([0-9]+)\.txt'
                match = re.search(pattern, file_name)
                file_index = match.group(1)
                print(file_index)
                if int(file_index) == 0:
                    return
                
                last_file_index = int(file_index) - 1
                pattern = r'^(.*?)_[0-9]+\.txt'
                match = re.search(pattern, file_name)
                extracted_text = match.group(1)
                last_file_name = extracted_text + '_' + str(last_file_index) + '.txt'
                last_document = collection.find_one({'file_name':last_file_name, 'signer':'no provided'})
                up_filename = extracted_text + '_' + str(last_file_index) + '-' + str(file_index) + '.txt'
                update_query = {
                    "$set": {
                        "signer": data[6],
                        "signed_date": datetime.strptime(signed_date, '%m/%d/%Y'),
                        "file_name": up_filename
                    }
                }
                collection.update_one({"_id": last_document["_id"]}, update_query)
                return
        else:
            if signed_date == 'error' or signed_date == 'no valid':
                doc = {'patient_name':data[0], 'doctor_name': data[1], 'collaborator_name': data[2], 'visit_date':datetime.strptime(visit_date, '%m/%d/%Y'), 'facility':data[4], 'activity': data[5], 'signer': 'no provided', 'signed_date': datetime.now().strftime('%m/%d/%Y'), 'summary': data[8], 'file_name':file_name}
                result = collection.insert_one(doc)
                return
            else:
                doc = {'patient_name':data[0], 'doctor_name': data[1], 'collaborator_name': data[2], 'visit_date':datetime.strptime(visit_date, '%m/%d/%Y'), 'facility':data[4], 'activity': data[5], 'signer': data[6], 'signed_date': datetime.now().strptime(signed_date, '%m/%d/%Y'), 'summary': data[8], 'file_name':file_name}
                result = collection.insert_one(doc)
                return
    except Exception as e:
        print("-------------------")
        print(data)
        print(f"db error: {e}")
        return
    
def main():
    src_path = 'json/text'
    txt_files = os.listdir(src_path)
    results = collection.find({})
    for result in results:
        print(f"sum :", result["file_name"])
    return

    for file in txt_files:
        results = collection.find({'file_name': file})
        count = sum(1 for _ in results)
        if count > 0:
            continue

        text_file_path = os.path.join(src_path, file)
        context = ""
        with open(text_file_path, 'r', encoding='utf-8-sig') as ff:
            context = ff.read() 
        messages=[
            {"role": "system", "content": """Please analyze the provided medical document and extract essential information for each patient visit. Present the extracted information in a structured list format for each visit, using the '//////////' as a separate header. Instead, include the date of the visit as one of the listed details. Each visit's information should be clear, concise, and organized without unnecessary descriptions or symbols. Follow this template for consistency:
                ///////////////////////
                Patient Name: [patient's full name]
                Doctor Name: [doctor's full name]
                Collaborator Name: [main Collaborator's full name, if not exist then 'not provided']
                Date of Visit: MM/DD/YYYY
                Medical Facility: [name of the medical facility]
                Main Service Provided: [most specific service provided]
                Signed Off By: [name of the person who signed off on the service]
                Sign-off Date: MM/DD/YYYY
                Summary: [brief summary of the services provided organized by these sections.
                    - reviewed radiology report (if doesn't exist, then 'not provided')
                    - physical examination (if doesn't exist, then 'not provided')
                    - assesment (if doesn't exist, then 'not provided')
                    - plan (if doesn't exist, then 'not provided')
                    - date of accident (if doesn't exist, then 'not provided')
                    - history of injury (if doesn't exist, then 'not provided')
                    - history of present illness (if doesn't exist, then 'not provided')
                    - discussion/plan (if doesn't exist, then 'not provided')]
                The summary should be succinct and informative, capturing the essence of the visit without extraneous details. Ensure that all information respects the document's context and content, with each visit's information clearly separated."""},
            {"role": "user", "content": context}
        ]
        try:
            time.sleep(3)
            response = completions_with_backoff(
                        model="gpt-4-turbo-preview",
                        messages=messages,
                        frequency_penalty=0,
                        temperature=0.5,
                        seed=2
                    )
            # print(response)
            # print(file)
            extract_insertDB(response, file)
            # db_insert(values, file)
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please run after one hour again!")
            return 0
        
if __name__ == "__main__":
    # Run the main function
    print("processing")
    result = main()
    if result != 0:
        print("done")
