import os
from datetime import datetime

from pypdf import PdfWriter


def merge_pdf(path_to_file_folder, destination_path):
   count = 0
   dt_string = datetime.now().strftime("%d-%m-%Y - %H%M%S")

   #Create instance of PdfWriter() class
   merger = PdfWriter()

   #Get the file names in the directory
   for root, dirs, file_names in os.walk(path_to_file_folder):
      for file_name in file_names:
         #Append PDF files
         if ".pdf" in file_name:
            merger.append(os.path.join(path_to_file_folder, file_name))
            count += 1

   #Write out merged PDF file
   merger.write(os.path.join(destination_path, f"PDF-WinLuk-{dt_string}.pdf"))
   merger.close()

   return True, count