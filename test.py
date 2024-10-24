import os
import json

base_path = ""
timeline_json_path = 'json/img'
text_path = 'json/test'

def proc_data(data, filename):
  for page in data:
    blocks_data = page["readResult"]["blocks"]
    for block in blocks_data:
      lines_data = block["lines"]
      for line in lines_data:
        text = line["text"]
        with open(os.path.join(text_path, filename)+'.txt', 'a', encoding='utf-8') as ff:
          ff.write(text + '\n')

def main():
  for root, dirs, files in os.walk(timeline_json_path):
      data = []
      for file in files:
        try:
          with open(os.path.join(root, file), 'r', encoding='utf-8-sig') as json_file:
            temp = json_file.read()
            if temp:  # Ensure 'temp' is not empty
              data.append(json.loads(temp))
            else:
              print("Warning: The file is empty.")
        except FileNotFoundError:
          print("Error: The file was not found.")
        except json.JSONDecodeError as e:
          print(f"Error decoding JSON: {e}")
      
      if len(data) > 0:
        proc_data(data, root[9:])    

if __name__ == "__main__":
    # Run the main function
    main()
    print("txt file generated")








