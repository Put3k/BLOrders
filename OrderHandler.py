import csv
import os
import re
import sys
from datetime import datetime
from dotenv import load_dotenv
from contextlib import suppress

from Google import create_service
from DriveAPI import download_file_by_id, find_file_in_folder_by_keywords
from error_handling import save_error_to_file, save_search_log_to_file
from constants import (
    CONTRACTOR,
    SMALL_SIZES,
    PRODUCTS,
    WHITE_SHIRT_FOLDER_ID,
    WHITE_CUP_FOLDER_ID,
    BLACK_SHIRT_FOLDER_ID,
    BLACK_CUP_FOLDER_ID,
    BLACK_HALFTONE_SHIRT_FOLDER_ID,
    GOLD_CUP_FOLDER_ID,
)
from utils import resource_path

load_dotenv()


# find csv file in current folder
def find_csv_file():
    current_folder = os.getcwd()
    files = os.listdir(current_folder)

    for f in files:
        if f.endswith(".csv"):
            path = os.path.join(current_folder, f)
            return path
    return None


# transform sku to code.
def get_code(sku):
    regex_filter = re.compile(
        "(KOSZ_MES_B|KOSZ_MES_C|KOSZ_DAM_B|KOSZ_DAM_C|KOSZ_DZIEC_CHLOP_B|KOSZ_DZIEC_CHLOP_C|KOSZ_DZIEC_DZIEW_B"
        "|KOSZ_DZIEC_DZIEW_C|KOSZ_DZIEC_B|KOSZ_DZIEC_C|KB_ZW|1KB_ZW|2KB_ZW|1_KB_ZW|2_KB_ZW|V1_KB_ZW|V2_KB_ZW|KB_MAG"
        "|1KB_MAG|2KB_MAG|V1_KB_MAG|V2_KB_MAG|V1_KB_FUN_C|V2_KB_FUN_C|KB_FUN_C|KB_GOLD_GD|1POD_ZW|2POD_ZW|POD_ZW|V1_POD_ZW"
        "|V2_POD_ZW|V1_LEZA|V2_LEZA|LEZA|_XS_|_S_|_M_|_L_|_XL_|_XXL_|_3-4_|_5-6_|_7-8_|_9-11_|_12-14_)"
    )

    code = regex_filter.sub("", sku)
    code = re.sub(r"_XS$|_S$|_M$|_L$|_XL$|_XXL$|_3-4|_5-6|_7-8|_9-11|_12-14$", "", code)
    code = re.sub(r"^_B_|^_C_", "", code)
    code = re.sub(r"^_|_$", "", code)
    code = re.sub(r"_H999", "", code)
    return code


# transform code to design
def get_design(code):
    design = re.sub(r"_[0-9]{2,4}[BC]", "", code)
    design = re.sub(r"\b\d{2}[BC]\b|\d{2}[BC]\b|\b\d{2}[BC]", "", design)

    return design


# returns design endcode:    PSY_LZ_TOARG_04C ===> 04C
def get_design_endcode(code):
    suffix = re.search(r"\d{2,4}[A-Z]", code)

    if suffix:
        text = suffix.group(0)
        return text
    else:
        return None


# shorten design by one part:  PSY_LZ_TOARG ===> PSY_LZ
def shorten_design(design):
    parts = design.split("_")
    if len(parts) <= 1:
        return None

    short_design = "_".join(parts[:-1])
    return short_design


# get product type:  KB_MAG_PSY_LZ_TOARG_04C ===> KB_MAG
def get_product_type(sku):
    products = ["LEZA", "KOSZ", "POD", "KB_ZW", "KB_MAG", "KB_FUN", "KB_GOLD"]

    for product in products:
        if re.search(product, sku):
            return product
    return None


# get file type to download: "pdf" or "png"
def get_file_type(product_type):
    if product_type in ["LEZA", "KOSZ", "POD"]:
        file_type = ".png"
        return file_type
    elif product_type in ["KB_ZW", "KB_MAG", "KB_FUN", "KB_GOLD"]:
        file_type = ".pdf"
        return file_type
    else:
        return None


def find_file_id(drive_service, keywords, root_folder_id):
    file_data = find_file_in_folder_by_keywords(
        drive_service=drive_service, keywords=keywords, root_folder_id=root_folder_id
    )

    if file_data:
        return file_data["id"], file_data["name"]

    return None, None


class Order:
    drive_service = None

    def __init__(self, order_id, quantity, sku):
        self.order_id = order_id
        self.quantity = quantity

        self.sku = sku  # full sku - KOSZ_MES_C_ZAJZAW_Geode_04C_XXL
        self.first_code = get_code(
            self.sku
        )  # first code - to help join same order designs in different sizes
        self.code = get_code(self.sku)  # code - ZAJZAW_GEODE_04C
        self.design_name = get_design(self.code)  # design name - ZAJZAW
        self.product_type = get_product_type(self.sku)  # product type
        self.file_type = get_file_type(
            self.product_type
        )  # design file type ===> "pdf" or "png"
        self.design_color = self.get_design_color()  # Colors are black or white.
        self.endcode = get_design_endcode(self.code)

        self.design_folder_id = self.get_folder_id()
        self.searched_codes = []
        self.file_id, self.file_name = find_file_id(
            drive_service=self.drive_service,
            keywords=self.get_keywords(),
            root_folder_id=self.design_folder_id,
        )
        self.is_adult = is_adult(
            self.sku
        )  # Is a small or big format print (big => adults; samll => kids)

        self.status = False

    def __str__(self):
        return f"{self.order_id} - {self.sku} - x{self.quantity}"

    def get_folder_id(self):
        if self.product_type in ["KOSZ", "POD", "LEZA"]:
            self.file_name = self.code + ".png"
            if self.design_color == "black_ht":
                return BLACK_HALFTONE_SHIRT_FOLDER_ID
            elif self.design_color == "white":
                return WHITE_SHIRT_FOLDER_ID
            elif self.design_color == "black":
                return BLACK_SHIRT_FOLDER_ID
        elif self.product_type in ["KB_ZW", "KB_MAG", "KB_FUN", "KB_GOLD"]:
            self.file_name = self.code + ".pdf"
            if self.design_color == "white":
                return WHITE_CUP_FOLDER_ID
            elif self.design_color == "black":
                return BLACK_CUP_FOLDER_ID
            elif self.design_color == "gold":
                return GOLD_CUP_FOLDER_ID

    def get_keywords(self):
        keywords = []
        keywords.extend(self.code.split(sep="_"))
        if self.design_color == "black_ht":
            keywords.append("H999")

        return keywords

    # returns color of design
    def get_design_color(self):
        WHITE_TYPE = [
            "KOSZ_MES_B",
            "KOSZ_DAM_B",
            "KOSZ_DZIEC_CHLOP_B",
            "KB_ZW",
            "KB_MAG",
            "POD_ZW",
        ]
        BLACK_TYPE = ["KOSZ_MES_C", "KOSZ_DAM_C", "KB_FUN_C"]

        if "H999" in self.sku:
            return "black_ht"
        if "KB_GOLD_GD" in self.sku:
            return "gold"

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

    # returns destination folder string
    @property
    def destination_folder(self):
        # Create Different folder for KUBKI, KOSZ, and KOSZ_DZIEC for sizes: 3-4, 5-6, 7-8

        for product in PRODUCTS:
            if re.search(product, self.sku):
                label = product
                break
            label = None

        if label:
            if label == "KOSZ":
                for size in SMALL_SIZES:
                    if re.search(size, self.sku):
                        if self.design_color == "black_ht":
                            return "HALFTONE_KOSZ_DZIECIECE"
                        return "KOSZ_DZIECIECE"
                if self.design_color == "black_ht":
                    return "HALFTONE_KOSZ_DOROSLI"
                return "KOSZ_DOROSLI"
            elif label in ["KB_ZW", "KB_FUN", "KB_MAG", "KB_GOLD"]:
                return "Kubki"
            else:
                return label
        else:
            save_error_to_file(f"Could not label where to save '{self.sku}' file.")


def is_adult(sku):
    for product in PRODUCTS:
        if re.search(product, sku):
            label = product
            break
        label = None

    if label:
        if label == "KOSZ":
            for size in SMALL_SIZES:
                if re.search(size, sku):
                    return False
            return True
        else:
            return False
    else:
        save_error_to_file(
            f"Could not determine product type from: '{sku}' file.",
            folder_path,
            datetime_string,
        )


# get data from csv file
def get_orders(csv_file_path):
    with open(csv_file_path) as f:
        csv_reader = csv.reader(f, delimiter=";")

        order_list = []

        for row in csv_reader:
            if len(row) > 0:
                # if (
                #     "Nr zamówienia" in row
                #     and "Ilość sztuk nadruku" in row
                #     and "SKU" in row
                # ):
                #     order_id_index = row.index("Nr zamówienia")
                #     quantity_index = row.index("Ilość sztuk nadruku")
                #     sku_index = row.index("SKU")
                #     continue
                # elsek'IloĹ›Ä‡ sztuk nadruku':
                #     order_id_index = 0
                #     quantity_index = 1
                #     sku_index = 2

                order_id_index = 0
                quantity_index = 1
                sku_index = 2

                with suppress(ValueError):
                    order_id = row[order_id_index]
                    quantity = int(row[quantity_index])
                    sku = row[sku_index]
                    code = get_code(sku)
                    product_type = get_product_type(sku)

                    matching_order = next(
                        (
                            order
                            for order in order_list
                            if order.order_id == order_id
                            and product_type == order.product_type
                            and (order.code == code or order.first_code == code)
                            and is_adult(sku) == order.is_adult
                        ),
                        None,
                    )

                    if matching_order is not None:
                        matching_order.quantity += quantity
                    else:
                        order = Order(order_id=order_id, quantity=quantity, sku=sku)
                        order_list.append(order)

    return order_list


def find_exact_file_id(drive_service, order):
    log = "\n"

    if order.design_folder_id and order.code and order.file_type:
        if order.design_color == "black_ht":
            design_code = order.code + "_H999" + order.file_type
        else:
            design_code = order.code + order.file_type

        query = f"'{order.design_folder_id}' in parents and name = '{design_code}'"
        page_token = None

        print(f"\nSearch: {design_code}")
        log += f"\nSearch: {design_code}"
        while True:
            response = (
                drive_service.files()
                .list(q=query, fields="files(id, name)", pageToken=page_token)
                .execute()
            )
            if "files" in response:
                for file in response.get("files", []):
                    print(f"Found file: {file.get('name')}, {file.get('id')}\n")
                design_id_response = response.get("files", [])
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    break
            else:
                design_id_response = None
                break

        if design_id_response:
            log += f"\nFound file: {file.get('name')}, {file.get('id')}\n"
            save_search_log_to_file(log, folder_path, datetime_string)
            design_id = design_id_response[0]["id"]
            file_name = design_id_response[0]["name"]
            return design_id, file_name

        else:
            print(f"Not found: {design_code}")
            log += f"\nNot found: {design_code}"
            save_search_log_to_file(log, folder_path, datetime_string)
            return None, None

    else:
        print(f"Not found: {order.code}{order.file_type}")
        return None, None


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


def find_file_and_download(drive_service, order, folder_path, download_files=True):
    file_counter = None
    if CONTRACTOR == "FAKTORIA":
        file_counter = order.quantity
        base = " - ".join(
            [
                order.destination_folder,
                order.order_id,
                order.file_name,
            ]
        )
        # .png/.pdf is added -> need to be removed
        base_file_name = base.replace(order.file_type, "")

    else:
        file_name = " - ".join(
            [
                order.destination_folder,
                order.order_id,
                f"x{order.quantity}",
                order.file_name,
            ]
        )

    if order.destination_folder == "Kubki":
        if CONTRACTOR == "FAKTORIA":
            category_folder = os.path.join(folder_path, "Kubki")
        else:
            category_folder = os.path.join(folder_path, "Kubki", order.design_color)
    elif order.destination_folder == "LEZA":
        category_folder = os.path.join(folder_path, "black", "Lezaki")
    else:
        category_folder = os.path.join(
            folder_path, order.design_color or "", order.destination_folder
        )

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if not os.path.exists(category_folder):
        os.makedirs(category_folder)

    if download_files:
        if CONTRACTOR == "FAKTORIA":
            file_name = base_file_name + f" ({file_counter}){order.file_type}"
            file_counter -= 1

        download_file_by_id(
            drive_service,
            order.file_id,
            file_name,
            category_folder,
            is_adult=order.is_adult,
        )
        if CONTRACTOR == "FAKTORIA":
            import shutil

            origin_file_name = file_name
            for i in range(file_counter, 0, -1):
                file_name = base_file_name + f" ({file_counter}){order.file_type}"
                src = os.path.join(category_folder, origin_file_name)
                dst = os.path.join(category_folder, file_name)
                shutil.copyfile(src, dst)
                file_counter -= 1


def main(csv_file_path, download_files=True):
    # Get credentials file path
    if getattr(sys, "frozen", False):
        client_secret_file = resource_path("credentials.json")
    else:
        client_secret_file = "credentials.json"

    drive_service = create_service(
        client_secret_file, "drive", "v3", ["https://www.googleapis.com/auth/drive"]
    )
    Order.drive_service = drive_service

    if not (
        WHITE_SHIRT_FOLDER_ID
        and WHITE_CUP_FOLDER_ID
        and BLACK_SHIRT_FOLDER_ID
        and BLACK_CUP_FOLDER_ID
        and BLACK_HALFTONE_SHIRT_FOLDER_ID
    ):
        print(f"Could not get drive folders ID's")
        return False

    global datetime_string
    datetime_string = datetime.now().strftime("%d-%m-%Y - %H%M%S")

    global folder_path
    folder_path = os.path.join(os.getcwd(), f"Baselinker - {datetime_string}")

    if csv_file_path and drive_service:
        # TODO add counter for found files and downloaded files
        order_list = get_orders(csv_file_path)
        order_count = len(order_list)
        order_file_exists_count = 0
        order_download_count = 0

        for order in order_list:
            if order.file_id:
                find_file_and_download(
                    drive_service, order, folder_path, download_files=download_files
                )

                order_file_exists_count += 1
                if download_files:
                    order_download_count += 1
            else:
                save_error_to_file(
                    f"\nOrder file id not found: {order.order_id} - {order.sku}\n",
                    folder_path,
                    datetime_string,
                )

        print(f"Downloaded {order_download_count} files.")

        if order_count != order_download_count:
            save_error_to_file(
                f"\nOrders: {order_count}\nFound files: {order_download_count}\nMissing files: {order_count-order_download_count}",
                folder_path,
                datetime_string,
            )

        return order_count, order_download_count, order_file_exists_count

    else:
        return False
