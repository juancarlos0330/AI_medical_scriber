import fitz  # Import PyMuPDF
import os
import json
import requests
import threading
from datetime import datetime
import sys

base_path = ""
img_pdf_path = 'pdf/img'
img_text_path = 'json/img'
api_url = "https://portal.vision.cognitive.azure.com/api/demo/analyze?features=read"

def ocr(src, dst):
    while True:
        try:
            # print("processing: ", src)
            file_name = os.path.basename(src)

            with open(src, 'rb') as f:
                files=[('file',(file_name,f,'image/png'))]
                response = requests.request("POST", api_url, data={}, files=files)
                # print(json.loads(response.text)["modelVersion"])
                temp_file = os.path.join(dst+'/', file_name[:-4] + '.json')
                with open(temp_file, 'w', encoding='utf-8-sig') as ff:
                    json.dump(json.loads(response.text), ff, indent=4)

            return
        except Exception as err:
            print('Error:', err)

def extract(pdf_file_path, pdf_file):
    print("processing ", pdf_file_path)

    pdf_document = fitz.open(pdf_file_path)

    # Define your desired output width and height
    desired_width = 1654  # example width in pixels
    desired_height = 2339  # example height in pixels

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        
        # Original dimensions of the PDF page
        orig_width, orig_height = page.rect.width, page.rect.height

        # Calculate scale factors to achieve desired dimensions
        scale_x = desired_width / orig_width
        scale_y = desired_height / orig_height

        # Create a matrix for the transformation
        mat = fitz.Matrix(scale_x, scale_y)

        # Generate the pixmap with the transformation
        pix = page.get_pixmap(matrix=mat)
        
        temp_img_dir = img_pdf_path+'/'+pdf_file[:-4]
        output_image_path = os.path.join(img_pdf_path+'/'+pdf_file[:-4]+'/', 'page{:03d}.png'.format(page_num))
        pix.save(output_image_path)

    pdf_document.close()

    temp_img_files = os.listdir(temp_img_dir)
    for temp_img_file in temp_img_files:
        temp_img_file_path = os.path.join(temp_img_dir+'/', temp_img_file)
        ocr(temp_img_file_path, img_text_path + '/' + pdf_file[:-4])
    
    print("ocr finished")

if __name__ == "__main__":
    print(datetime.now())
    args = sys.argv
    if len(args) <= 1:
        src_path = 'imgpdfs'
    else:
        src_path = args[1]

    current_path = os.path.dirname(args[0])

    pdf_files = os.listdir(src_path)
    threads = []

    for pdf_file in pdf_files:
        pdf_file_path = os.path.join(src_path, pdf_file)
        img_folder_path = os.path.join(img_pdf_path+'/', pdf_file[:-4])
        json_folder_path = os.path.join(img_text_path+'/', pdf_file[:-4])
        os.makedirs(img_folder_path, exist_ok=True)
        os.makedirs(json_folder_path, exist_ok=True)
        print(pdf_file_path,pdf_file)
        threads.append(threading.Thread(target=extract, args=(pdf_file_path,pdf_file)))

    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()









