
# BLOrders

A windowed Python program created to automate repetitive processes related to print-on-demand sales.  
The program's interface is in Polish.




## Features

- Download design files from Google Drive via Google APIs, based on Baselinker order report.
- Creating a print-ready file from a graphic designs.
- Merging PDF designs into one print-ready PDF file.


## Installation

1. Create virtual environment:
```bash
$ python3 -m venv venv
```

2. Clone repository, activate virtual environment, navigate to repo folder, and install required packages from `requirements.txt`:
```bash
$ git clone https://github.com/Put3k/BLOrders.git   #Clone repository
$ venv\Scripts\activate                             #Activate virtual environment
$ cd BLorders                                       #Navigate to repository folder
$ pip install -r requirements.txt                   #Install required packages
```

3. Create Google Cloud project and configure it:
* [Google Drive API Python quickstart](https://developers.google.com/drive/api/quickstart/python) follow the guide up to `Install the Google client library`. Do not install `Google client library library` because it is already included in `requirements.txt`.
* place `credentials.json` file you downloaded in `BLOrders` directory.
* get your Google Drive IDs. Currently there are 4 hardcoded slots for drives to download:
    * white PNG files
    * white PDF files
    * black PNG files
    * black PDF files
    For now, regex is set to find strictly defined codes. I'm considering introducing functionality in the future for specifying codes along with showing samples of them.
4. Run `BLOrders.py`:
```bash
$ python BLOrders.py
```

The first time you run the `BLOrders.py`, it prompts you to authorize access:
- If you're not already signed in to your Google Account, you're prompted to sign in. If you're signed in to multiple accounts, select one account to use for authorization.
- Click Accept.
Authorization information is stored in the file system, so the next time you run the sample code, you aren't prompted for authorization.


## Usage

After u run the `BLOrders.py` you should see this window:
![BLOrders_cockpit](https://imageupload.io/ib/7HOaejCootGYLJ1_1693315713.png)

No rocket-science here.

### Program Sections

**BaseLinker - Downloading designs for orders**  
`BaseLinker - Pobieranie grafik do zamówień` ===> `BaseLinker - Downloading designs for orders`
* Select the `.csv` file with the BaseLinker order list and then press "Download Designs" to download the designs associated with the orders.

* Structure of the `.csv` file downloaded from BaseLinker:
![BLOrders_csv_file](https://imageupload.io/ib/X1Brot57ypqccJs_1693317162.png)
* Columns headers are hardcoded as:
    * **A** ==> `Nr zamówienia` translates to `Order ID`
    * **B** ==> `Ilość sztuk nadruku` translates to `qunatity of design`
    * **C** ==> `SKU`
    Column indexes are determined by the headers. The headers can be anywhere in the **first row**.

**Combine Designs**  
`Łączenie Grafik` ===> `Merge Designs`
* Select the folder with the `.png` files you want to combine and then select the destination folder where you want to save the results.
* Program combines PNG files in pack of 6.

**Combine PDF**  
`Łączenie PDF` ===> `Combine PDF`
* Select the folder with the `.pdf` files you want to Combine and then select the destination folder where you want to save the results.
* Program combines PDF files as one PDF file with multiple pages.


