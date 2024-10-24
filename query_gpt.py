import tkinter as tk
from tkinter import ttk
import pymongo  
from fuzzywuzzy import fuzz, process
import re
import webbrowser
import sys
import os

client = pymongo.MongoClient("mongodb+srv://arbab998:wDl85YMTveO5ayrQ@cluster0.tjglijc.mongodb.net/")
db=client["medical_data"]
collection = db["summary"]
threshold = 55
threshold_doctor = 70

selected_patient = ''
selected_doctor = ''

similar_groups_patient = []
similar_groups_doctor = []

def get_docotr_positon(doctor_name):
  if ',' in doctor_name:
    return doctor_name
  
  for similar_names in similar_groups_doctor:
    for name in similar_names:
      if name == doctor_name:
        for name in similar_names:
          if ',' in name:
            return name
  return doctor_name

def load_patiences():
  global similar_groups_patient
  distinct_patients = collection.distinct('patient_name')
  checked = []
    
  for patience in distinct_patients:
    if patience not in checked:
      # Find matches in the list itself, with a similarity above the threshold
      matches = process.extract(patience, distinct_patients, limit=None, scorer=fuzz.token_sort_ratio)
      # Filter matches by the threshold, excluding the current patient (100% match)
      similar = [match for match, score in matches if score >= threshold and match != patience]
      if similar:
        similar.append(patience)  # Add the current patient to the group
        similar_groups_patient.append(similar)  # Add this group to the list of groups
        checked.extend(similar)  # Mark these patients as checked
      else:
        checked.append(patience)  # Mark this patient as checked if no similar found
  
  # Flatten array2 into a single list of elements to remove
  elements_to_remove = [element for sublist in similar_groups_patient for element in sublist]
  # Remove elements from array1 that are present in elements_to_remove
  filtered_array = [element for element in distinct_patients if element not in elements_to_remove]

  for item in similar_groups_patient:
    for sub_item in item:
      if not ('not' in sub_item.lower() or 'and' in sub_item.lower() or 'the' in sub_item.lower() or 'junior' in sub_item.lower()):
        listbox.insert(tk.END, item[0])
        break
  for item in filtered_array:
    if 'not' in item.lower() or 'and' in item.lower() or 'the' in item.lower() or 'jose' in item.lower():
      continue

    listbox.insert(tk.END, item)

def load_doctors():
  distinct_doctors = collection.distinct('doctor_name')
  global similar_groups_doctor
  checked = []
    
  for doctor in distinct_doctors:
    if 'not' in doctor.lower() or 'and' in doctor.lower() or 'the' in doctor.lower() or 'junior' in doctor.lower():
      continue

    if doctor not in checked:
      # Find matches in the list itself, with a similarity above the threshold
      matches = process.extract(doctor, distinct_doctors, limit=None, scorer=fuzz.token_sort_ratio)
      # Filter matches by the threshold, excluding the current patient (100% match)
      similar = [match for match, score in matches if score >= threshold_doctor and match != doctor]
      if similar:
        similar.append(doctor)  # Add the current patient to the group
        similar_groups_doctor.append(similar)  # Add this group to the list of groups
        checked.extend(similar)  # Mark these patients as checked
      else:
        checked.append(doctor)  # Mark this patient as checked if no similar found
  # Flatten array2 into a single list of elements to remove
  elements_to_remove = [element for sublist in similar_groups_doctor for element in sublist]
  # Remove elements from array1 that are present in elements_to_remove
  filtered_array = [element for element in distinct_doctors if element not in elements_to_remove]

  for item in similar_groups_doctor:
    for sub_item in item:
      if not ('not' in sub_item.lower() or 'and' in sub_item.lower() or 'the' in sub_item.lower() or 'junior' in sub_item.lower()):
        listbox_doctor.insert(tk.END, sub_item)
        break

  for item in filtered_array:
    if 'not' in item.lower() or 'and' in item.lower() or 'the' in item.lower() or 'jose' in item.lower():
      continue
    
    listbox_doctor.insert(tk.END, item)

def on_click(event):
    tree_summary_pat.delete(*tree_summary_pat.get_children())
    tree_summary_pat.heading('provider', text='Doctor')
    # Get the index of the clicked item
    index = listbox.curselection()[0]
    # Get the text of the clicked item
    item_text = listbox.get(index)
    for similar_names in similar_groups_patient:
      for name in similar_names:
        if name == item_text:
          results = collection.find({'patient_name': {'$in': similar_names}}).sort([
            ('visit_date', pymongo.ASCENDING)
          ])

          for res in results:
            pattern = r"^(.*?)_[\d\-]*\.txt$" 
            pattern_page = r"_(\d+(?:-\d+)?)\.txt$"
            match = re.match(pattern, res['file_name'])
            file_pdf = match.group(1)
            print("file0 name:",  res['file_name'])

            match = re.search(pattern_page, res['file_name'])
            str_page = match.group(1)
            arr_page = str_page.split('-')
            page_index = ''
            if len(arr_page) == 1:
              page_index = str((int(arr_page[0]) + 1) * 5 - 4) + '-' + str((int(arr_page[0]) + 1) * 5)
            else:
              page_index = str((int(arr_page[0]) + 1) * 5 - 4) + '-' + str((int(arr_page[1]) + 1) * 5)

            if isinstance(res['visit_date'], str):
              date_string = res['visit_date']
            else:
              date_string = res['visit_date'].strftime('%m/%d/%Y')

            if isinstance(res['signed_date'], str):
              sign_date_string = res['signed_date']
            else:
              sign_date_string = res['signed_date'].strftime('%m/%d/%Y')

            doctor_name = get_docotr_positon(res['doctor_name'])

            if not ('not' in res['collaborator_name'].lower()):
              doctor_name = doctor_name + ', ' + res['collaborator_name']
            tree_summary_pat.insert('', 'end', values=(doctor_name, date_string, res['facility'], res['activity'],res['signer'], sign_date_string, file_pdf+'.pdf', page_index, res['summary']))
          
          return

    results = collection.find({'patient_name': item_text}).sort([
      ('visit_date', pymongo.ASCENDING)
    ])

    for res in results:
      pattern = r"^(.*?)_[\d\-]*\.txt$" 
      pattern_page = r"_(\d+(?:-\d+)?)\.txt$"
      match = re.match(pattern, res['file_name'])
      file_pdf = match.group(1)
      match = re.search(pattern_page, res['file_name'])
      print("file name:",  res['file_name'])
      str_page = match.group(1)
      arr_page = str_page.split('-')
      page_index = ''
      if len(arr_page) == 1:
        page_index = str((int(arr_page[0]) + 1) * 5 - 4) + '-' + str((int(arr_page[0]) + 1) * 5)
      else:
        page_index = str((int(arr_page[0]) + 1) * 5 - 4) + '-' + str((int(arr_page[1]) + 1) * 5)

      if isinstance(res['visit_date'], str):
        date_string = res['visit_date']
      else:
        date_string = res['visit_date'].strftime('%m/%d/%Y')

      if isinstance(res['signed_date'], str):
        sign_date_string = res['signed_date']
      else:
        sign_date_string = res['signed_date'].strftime('%m/%d/%Y')

      doctor_name = get_docotr_positon(res['doctor_name'])

      if not ('not' in res['collaborator_name'].lower()):
        doctor_name = doctor_name + ', ' + res['collaborator_name']
      tree_summary_pat.insert('', 'end', values=(doctor_name, date_string, res['facility'], res['activity'],res['signer'],sign_date_string, file_pdf+'.pdf', page_index, res['summary']))

def on_click_doctor(event):
    tree_summary_pat.delete(*tree_summary_pat.get_children())
    tree_summary_pat.heading('provider', text='Patient')
    # Get the index of the clicked item
    index = listbox_doctor.curselection()[0]
    # Get the text of the clicked item
    item_text = listbox_doctor.get(index)
    for similar_names in similar_groups_doctor:
      for name in similar_names:
        if name == item_text:
          results = collection.find({'doctor_name': {'$in': similar_names}}).sort([
            ('visit_date', pymongo.ASCENDING)
          ])

          for res in results:
            pattern = r"^(.*?)_[\d\-]*\.txt$" 
            pattern_page = r"_(\d+(?:-\d+)?)\.txt$"
            match = re.match(pattern, res['file_name'])
            file_pdf = match.group(1)
            match = re.search(pattern_page, res['file_name'])
            str_page = match.group(1)
            arr_page = str_page.split('-')
            page_index = ''
            if len(arr_page) == 1:
              page_index = str((int(arr_page[0]) + 1) * 5 - 4) + '-' + str((int(arr_page[0]) + 1) * 5)
            else:
              page_index = str((int(arr_page[0]) + 1) * 5 - 4) + '-' + str((int(arr_page[1]) + 1) * 5)

            if isinstance(res['visit_date'], str):
              date_string = res['visit_date']
            else:
              date_string = res['visit_date'].strftime('%m/%d/%Y')

            if isinstance(res['signed_date'], str):
              sign_date_string = res['signed_date']
            else:
              sign_date_string = res['signed_date'].strftime('%m/%d/%Y')
            tree_summary_pat.insert('', 'end', values=(res['patient_name'], date_string, res['facility'], res['activity'],res['signer'],sign_date_string, file_pdf+'.pdf', page_index, res['summary']))
          
          return

    results = collection.find({'doctor_name': item_text}).sort([
      ('visit_date', pymongo.ASCENDING)
    ])

    for res in results:
      pattern = r"^(.*?)_[\d\-]*\.txt$" 
      pattern_page = r"_(\d+(?:-\d+)?)\.txt$"
      match = re.match(pattern, res['file_name'])
      file_pdf = match.group(1)
      match = re.search(pattern_page, res['file_name'])
      str_page = match.group(1)
      arr_page = str_page.split('-')
      page_index = ''
      if len(arr_page) == 1:
        page_index = str((int(arr_page[0]) + 1) * 5 - 4) + '-' + str((int(arr_page[0]) + 1) * 5)
      else:
        page_index = str((int(arr_page[0]) + 1) * 5 - 4) + '-' + str((int(arr_page[1]) + 1) * 5)

      if isinstance(res['visit_date'], str):
        date_string = res['visit_date']
      else:
        date_string = res['visit_date'].strftime('%m/%d/%Y')

      if isinstance(res['signed_date'], str):
        sign_date_string = res['signed_date']
      else:
        sign_date_string = res['signed_date'].strftime('%m/%d/%Y')
      tree_summary_pat.insert('', 'end', values=(res['patient_name'], date_string, res['facility'], res['activity'],res['signer'],sign_date_string, file_pdf+'.pdf', page_index, res['summary']))

def on_treeview_select(event):
    selected_item = tree_summary_pat.selection()[0]
    # Get the values of all columns in the selected row
    values = tree_summary_pat.item(selected_item, 'values')

    tree_pdf.delete(*tree_pdf.get_children())
    tree_pdf.insert('', 'end', values=(values[6], values[7]))

    summary_column_value = values[8]
    # print(summary_column_value)
    # entries = summary_column_value.strip().split("\n")
    # summary = ''
    # for entry in entries:
    #   if not ('not' in entry):
    #     summary = summary + entry + '/n'
        
    text_summary_view.delete('1.0', 'end')
    text_summary_view.insert(tk.END, summary_column_value) 

def on_pdf_select(event):
    selected_item = tree_pdf.selection()[0]
    # Get the values of all columns in the selected row
    values = tree_pdf.item(selected_item, 'values')
    # Get the value in the 5th column (index 4)
    pdf = values[0]
    page = values[1]
    exe_path = sys.executable

    # Get the directory of the executable
    exe_dir = os.path.dirname(exe_path)

    pdf_path = os.path.join(exe_dir + '/pdf/', pdf)
    url = f'file:///{pdf_path}#page={page}'
    
    # Specify the path to Chrome's executable
    # For Windows, it might be something like 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
    # For Linux, it might be '/usr/bin/google-chrome' or similar, depending on your installation
    chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
    
    # Register Chrome in webbrowser under a name like 'chrome'
    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
    
    # Open the URL in Chrome, using the name registered above
    webbrowser.get('chrome').open_new(url)


# Create the main window
root = tk.Tk()
root.title("Medical scribe expert")
root.geometry("1360x680")  # Set the size of the window

# list patients
label = tk.Label(root, text="Patients List")
label.pack(pady=10)  # Add some padding around the label
label.place(x=25, y=25)
listbox = tk.Listbox(root)
listbox.pack(pady=5)
listbox.place(x=15, y=60, width=200, height=230)
listbox.bind('<ButtonRelease-1>', on_click)
load_patiences()

# list treatments about the patiences
label_summary_pat = tk.Label(root, text="Treatment List")
label_summary_pat.pack(pady=10)  # Add some padding around the label
label_summary_pat.place(x=725, y=25)
tree_summary_pat = ttk.Treeview(root, columns=('provider','visit_date','facility','activity', 'signer', 'signed_date', 'pdf', 'page', 'summary'), show='headings')
tree_summary_pat.pack(pady=5)
tree_summary_pat.place(x=230, y=60, width=1110, height=400)
tree_summary_pat.column('provider', width=250, anchor='center')
tree_summary_pat.heading('provider', text='Doctor')
tree_summary_pat.column('visit_date', width=70, anchor='center')
tree_summary_pat.heading('visit_date', text='Visit_date')
tree_summary_pat.column('facility', width=200, anchor='center')
tree_summary_pat.heading('facility', text='Facility')
tree_summary_pat.column('activity', width=250, anchor='center')
tree_summary_pat.heading('activity', text='Activity')
tree_summary_pat.column('signer', width=130, anchor='center')
tree_summary_pat.heading('signer', text='Signer')
tree_summary_pat.column('signed_date', width=70, anchor='center')
tree_summary_pat.heading('signed_date', text='Signed date')
tree_summary_pat.column('pdf', width=0, anchor='center')
tree_summary_pat.heading('pdf', text='')
tree_summary_pat.column('page', width=0, anchor='center')
tree_summary_pat.heading('page', text='')
tree_summary_pat.column('summary', width=0, anchor='center')
tree_summary_pat.heading('summary', text='')
tree_summary_pat.bind("<<TreeviewSelect>>", on_treeview_select)
# list doctors
label_doctor = tk.Label(root, text="Doctors List")
label_doctor.pack(pady=10)  # Add some padding around the label
label_doctor.place(x=25, y=310)
listbox_doctor = tk.Listbox(root)
listbox_doctor.pack(pady=5)
listbox_doctor.place(x=15, y=335, width=200, height=325)
listbox_doctor.bind('<ButtonRelease-1>', on_click_doctor)
load_doctors()

label_summary_view = tk.Label(root, text="Summary")
label_summary_view.pack(pady=10)  # Add some padding around the label
label_summary_view.place(x=725, y=470)

tree_pdf = ttk.Treeview(root, columns=('pdf','page'), show='headings')
tree_pdf.pack(pady=5)
tree_pdf.place(x=230, y=490, width=1110, height=50)
tree_pdf.column('pdf', width=250, anchor='center')
tree_pdf.heading('pdf', text='PDF')
tree_pdf.column('page', width=70, anchor='center')
tree_pdf.heading('page', text='Page')
tree_pdf.bind("<<TreeviewSelect>>", on_pdf_select)

text_summary_view = tk.Text(root)
text_summary_view.pack(pady=5)
text_summary_view.place(x=230, y=560, width=1110, height=100)
#excel
# button_excel = tk.Button(root, text="Excel", command=write_excel)
# button_excel.pack(pady=5)  # Add some padding around the button
# button_excel.place(x=800, y=250, height=20)
# Start the GUI event loop
root.mainloop()
