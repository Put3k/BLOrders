import csv
import io
import json
import os
import re
import sys
from datetime import datetime

from dotenv import load_dotenv
from googleapiclient.http import MediaIoBaseDownload

from Google import Create_Service

load_dotenv()

#get resource path
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


#find csv file in current folder
def find_csv_file():
    current_folder = os.getcwd()
    files = os.listdir(current_folder)

    for f in files:
        if f.endswith(".csv"):
            path = os.path.join(current_folder, f)
            return path
    return None


#transform sku to code.
def get_code(sku):

    regex_filter = re.compile("(KOSZ_MES_B|KOSZ_MES_C|KOSZ_DAM_B|KOSZ_DAM_C|KOSZ_DZIEC_CHLOP_B|KOSZ_DZIEC_CHLOP_C|KOSZ_DZIEC_DZIEW_B|KOSZ_DZIEC_DZIEW_C|KOSZ_DZIEC_B|KOSZ_DZIEC_C|KB_ZW|1KB_ZW|2KB_ZW|1_KB_ZW|2_KB_ZW|V1_KB_ZW|V2_KB_ZW|KB_MAG|1KB_MAG|2KB_MAG|V1_KB_MAG|V2_KB_MAG|V1_KB_FUN_C|V2_KB_FUN_C|POD_ZW|V1_POD_ZW|V2_POD_ZW|V1_LEZAK|_XS_|_S_|_M_|_L_|_XL_|_XXL_|_3-4_|_5-6_|_7-8_|_9-11_|_12-14_)")

    code = regex_filter.sub("", sku)
    code = re.sub(r"_XS$|_S$|_M$|_L$|_XL$|_XXL$|_3-4|_5-6|_7-8|_9-11|_12-14$", "", code)
    code = re.sub(r"^_B_|^_C_", "", code)
    code = re.sub(r"^_|_$", "", code)
    return code


#transform code to design
def get_design(code):

    design = re.sub(r"_[0-9]{2,4}[BC]", "", code)
    design = re.sub(r"\b\d{2}[BC]\b|\d{2}[BC]\b|\b\d{2}[BC]", "", design)

    return design


#returns design endcode:    PSY_LZ_TOARG_04C ===> 04C
def get_design_endcode(code):

    suffix = re.search(r"\d{2,4}[A-Z]", code)

    if suffix:
        text = suffix.group(0)
        return text
    else:
        return None


#shorten design by one part:  PSY_LZ_TOARG ===> PSY_LZ
def shorten_design(design):
    parts = design.split("_")
    if len(parts) <= 1:
        return None

    short_design = "_".join(parts[:-1])
    return short_design


#get product type:  KB_MAG_PSY_LZ_TOARG_04C ===> KB_MAG
def get_product_type(sku):
    products = ["LEZAK", "KOSZ", "POD", "KB_ZW", "KB_MAG", "KB_FUN"]

    for product in products:
        if re.search(product, sku):
            return product
    return None

#get file type to download: "pdf" or "png"
def get_file_type(product_type):
    if product_type in ["LEZAK", "KOSZ", "POD"]:
        file_type = ".png"
        return file_type
    elif product_type in ["KB_ZW", "KB_MAG", "KB_FUN"]:
        file_type = ".pdf"
        return file_type
    else:
        return None


class Order:
    def __init__(self, order_id, quantity, sku):
        self.order_id = order_id
        self.quantity = quantity

        self.sku = sku                                      #full sku - KOSZ_MES_C_ZAJZAW_Geode_04C_XXL
        self.first_code = get_code(self.sku)                #first code - to help join same order designs in different sizes
        self.code = get_code(self.sku)                      #code - ZAJZAW_GEODE_04C
        self.design_name = get_design(self.code)            #design name - ZAJZAW
        self.product_type = get_product_type(self.sku)      #product type
        self.file_type = get_file_type(self.product_type)   #design file type ===> "pdf" or "png"
        self.design_color = self.get_design_color()         #Colors are black or white.
        self.endcode = get_design_endcode(self.code)

        self.design_folder_id = self.get_folder_id()
        self.searched_codes = []
        self.file_id, self.file_name = recursive_find_exact_file_id(self)                #design file id in Google Drive

        self.status = False

    def __str__(self):
        return f"{self.order_id} - {self.sku} - x{self.quantity}"

    def get_folder_id(self):
        if self.product_type in ["KOSZ", "POD", "LEZAK"]:
            self.file_name = self.code + ".png"
            if self.design_color == "white":
                return WHITE_SHIRT_FOLDER_ID
            elif self.design_color == "black":
                return BLACK_SHIRT_FOLDER_ID
        elif self.product_type in ["KB_ZW", "KB_MAG", "KB_FUN"]:
            self.file_name = self.code + ".pdf"
            if self.design_color == "white":
                return WHITE_CUP_FOLDER_ID
            elif self.design_color =="black":
                return BLACK_CUP_FOLDER_ID

    #returns color of design
    def get_design_color(self):

        WHITE_TYPE = ["KOSZ_MES_B", "KOSZ_DAM_B", "KOSZ_DZIEC_CHLOP_B", "KB_ZW", "KB_MAG", "POD_ZW"]
        BLACK_TYPE = ["KOSZ_MES_C", "KOSZ_DAM_C", "KB_FUN_C"]

        suffix = re.search(r"\d{2,4}[A-Z]", self.code)
        if suffix:
            text = suffix.group(0)
            if "B" in text:
                return "white"
            elif "C" in text:
                return "black"
        else:
            for prod_type in WHITE_TYPE:
                if prod_type in self.sku:
                    return "white"
            for prod_type in BLACK_TYPE:
                if prod_type in self.sku:
                    return "black"
        return None

    #returns destination folder string
    @property
    def destination_folder(self):
        #Create Different folder for KUBKI, KOSZ, and KOSZ_DZIEC for sizes: 3-4, 5-6, 7-8
        SMALL_SIZES = ["3-4", "5-6", "7-8"]
        PRODUCTS = ["LEZAK", "KOSZ", "POD", "KB_ZW", "KB_MAG", "KB_FUN"]

        for product in PRODUCTS:
            if re.search(product, self.sku):
                label = product
                break
            label = None

        if label:
            if label == "KOSZ":
                for size in SMALL_SIZES:
                    if re.search(size, self.sku):
                        return "KOSZ_DZIECIECE"
                return "KOSZ_DOROSLI"
            elif label in ["KB_ZW", "KB_FUN", "KB_MAG"]:
                return "Kubki"
            else:
                return label
        else:
            save_error_to_file(f"Could not label where to save '{self.sku}' file.")


#get data from csv file
def get_orders(csv_file_path):

    with open(csv_file_path, encoding='utf-8') as f:
        csvReader = csv.reader(f, delimiter=";")

        order_list = []

        for row in csvReader:
            if 0<len(row):
                if len(row[0])>1 or len(row[1])>1 or len(row[2])>1:
                    if "Nr zamówienia" in row and "Ilość sztuk nadruku" in row and "SKU" in row:
                        order_id_index = row.index("Nr zamówienia")
                        quantity_index = row.index("Ilość sztuk nadruku")
                        sku_index = row.index("SKU")      
                        continue
                    
                    order_id = row[order_id_index]
                    quantity = int(row[quantity_index])
                    sku = row[sku_index]
                    code = get_code(sku)
                    product_type = get_product_type(sku)

                    matching_order = next((order for order in order_list if order.order_id == order_id and product_type == order.product_type and (order.code == code or order.first_code == code)), None)

                    if matching_order is not None:
                        matching_order.quantity += quantity
                    else:
                        order = Order(order_id=order_id, quantity=quantity, sku=sku)
                        order_list.append(order)

    return order_list


def find_exact_file_id(order):

    log = "\n"

    if order.design_folder_id and order.code and order.file_type:
        design_code = order.code + order.file_type

        query = f"'{order.design_folder_id}' in parents and name = '{design_code}'"
        page_token = None

        print(f"Search: {design_code}")
        log += f"\nSearch: {design_code}"
        while True:
            response = service.files().list(q=query, fields='files(id, name)', pageToken=page_token).execute()
            if 'files' in response:
                for file in response.get('files', []):
                    print(f"Found file: {file.get('name')}, {file.get('id')}\n")
                design_id_response = response.get('files', [])
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break
            else:
                design_id_response = None
                break

        if design_id_response:
            log += f"\nFound file: {file.get('name')}, {file.get('id')}\n"
            save_search_log_to_file(log)
            design_id = design_id_response[0]['id']
            file_name = design_id_response[0]['name']
            return design_id, file_name

        else:
            print(f"Not found: {design_code}")
            log += f"\nNot found: {design_code}"
            save_search_log_to_file(log)
            return None, None
    
    else:
        print(f"Not found: {order.code}{order.file_type}")
        return None, None


def recursive_find_exact_file_id(order):
    design_id, file_name = find_exact_file_id(order)
    order.searched_codes.append(order.code)
    
    if not design_id:
        next_code_1 = recursive_code_generator(order)

        if next_code_1 and order.code not in order.searched_codes:
            result = recursive_find_exact_file_id(order)
            if result:
                return result

        next_code_2 = get_no_endcode(order)
        if next_code_2 and order.code not in order.searched_codes:
            result = recursive_find_exact_file_id(order)
            if result:
                return result

        return None, None
    else:
        return design_id, file_name
        


def recursive_code_generator(order):
    if order.design_name and order.endcode:

        current_code = order.code
        next_search_code = "_".join([order.design_name, order.endcode])

        if not current_code == next_search_code:
            order.code = next_search_code
            return True

    return None


def get_no_endcode(order):
    if order.design_name and order.endcode:

        current_code = order.code
        if order.design_color == "white":
            code_suffix = "B"
        elif order.design_color == "black":
            code_suffix = "C"
        else:
            return None

        next_search_code = order.design_name + code_suffix

        if not current_code == next_search_code:
            order.code = next_search_code
            return True

    return None


def list_order_files_id(order_list):

    for order in order_list:

        file_id = find_exact_file_id(order)
        if not file_id:
            next_search_code = "_".join(order.design_name, order.endcode)
            order.code = next_search_code
            find_exact_file_id(order)
        order.file_id = file_id


def download_file(order):
    file_id = order.file_id

    #check wheter shirt is for small size or not. If True, add 'DZIECIECE' to file name.
    if order.destination_folder == "KOSZ_DZIECIECE":
        file_name = " - ".join(["KOSZ_DZIECIECE", order.order_id, f"x{order.quantity}", order.file_name])
    else:
        file_name = " - ".join([order.order_id, f"x{order.quantity}", order.file_name])
    request = service.files().get_media(fileId=file_id)

    file = io.BytesIO()

    downloader = MediaIoBaseDownload(fd=file, request=request)
    done = False

    # if order.product_type in ["KB_ZW", "KB_MAG", "KB_FUN"]:
    #     file_path = os.path.join(folder_path, "Kubki", file_name)
    #     category_folder = os.path.join(folder_path, "Kubki")
    # else:
    #     file_path = os.path.join(folder_path, order.product_type, file_name)
    #     category_folder = os.path.join(folder_path, order.product_type)

    file_path = os.path.join(folder_path, order.destination_folder, file_name)
    category_folder = os.path.join(folder_path, order.destination_folder)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if not os.path.exists(category_folder):
        os.makedirs(category_folder)

    try:
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}% - {file_name}')
    except:
        save_error_to_file(f"Download Error - ID: {real_file_id}, FILE_NAME: {file_name}\n")
            
    file.seek(0)

    with open(file_path, "wb") as f:
        f.write(file.read())


def save_error_to_file(message):

    current_folder = os.getcwd()
    download_path = os.path.join(current_folder, f"BaseLinker - {dt_string}")
    logs_folder_path = os.path.join(current_folder, "logs")
    error_path = os.path.join(folder_path, logs_folder_path)

    if not os.path.exists(error_path):
        os.makedirs(error_path)

    with open(os.path.join(error_path, f"error_log - {dt_string}.txt"), "a") as e:
        e.write(message)


def save_search_log_to_file(message):

    current_folder = os.getcwd()
    download_path = os.path.join(current_folder, f"BaseLinker - {dt_string}")
    logs_folder_path = os.path.join(current_folder, "logs")
    error_path = os.path.join(folder_path, logs_folder_path)

    if not os.path.exists(error_path):
        os.makedirs(error_path)

    with open(os.path.join(error_path, f"search_log - {dt_string}.txt"), "a") as e:
        e.write(message)


def main(csv_file_path):

    # Get credentials file path
    if getattr(sys, 'frozen', False):
        CLIENT_SECRET_FILE = resource_path('credentials.json')
    else:
        CLIENT_SECRET_FILE = 'credentials.json'

    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']


    global service
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    global WHITE_SHIRT_FOLDER_ID
    global WHITE_CUP_FOLDER_ID
    global BLACK_SHIRT_FOLDER_ID
    global BLACK_CUP_FOLDER_ID


    DRIVES_PATH = resource_path('drive_folders_destination.json')
    with open(DRIVES_PATH) as f:
        drive_dest = json.load(f)

        WHITE_SHIRT_FOLDER_ID = drive_dest.get('WHITE_SHIRT_FOLDER_ID')
        WHITE_CUP_FOLDER_ID = drive_dest.get('WHITE_CUP_FOLDER_ID')
        BLACK_SHIRT_FOLDER_ID = drive_dest.get('BLACK_SHIRT_FOLDER_ID')
        BLACK_CUP_FOLDER_ID = drive_dest.get('BLACK_CUP_FOLDER_ID')

    if not WHITE_SHIRT_FOLDER_ID and WHITE_CUP_FOLDER_ID and BLACK_SHIRT_FOLDER_ID and BLACK_CUP_FOLDER_ID:
        print(f"Could not get drive folders ID's")
        return False

    date_time_now = datetime.now()
    global dt_string
    dt_string = date_time_now.strftime("%d-%m-%Y - %H%M%S")

    global folder_path
    global error_path
    folder_path = os.path.join(os.getcwd(), f"Baselinker - {dt_string}")

    if csv_file_path and service:
        order_list = get_orders(csv_file_path)
        order_count = len(order_list)
        order_download_count = 0

        for order in order_list:
            if order.file_id:
                download_file(order)
                order_download_count += 1
            else:
                save_error_to_file(f"\nOrder file id not found: {order.order_id} - {order.sku}\n")

        print(f"Downloaded {order_download_count} files.")
        
        if order_count != order_download_count:
            save_error_to_file(f"\nOrders: {order_count}\nFound files: {order_download_count}\nMissing files: {order_count-order_download_count}")

        return order_count, order_download_count

    else:
        return False