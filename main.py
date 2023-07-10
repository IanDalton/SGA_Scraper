import os,csv
from analisis import clean_db
if not os.path.isfile("dataset.csv"):
    import extract

    extract.extract_sga_classes()
    extract.turn_into_csv()

with open("dataset.csv","r",encoding="utf-8") as f:
    reader = csv.DictReader(f)
    data = list(reader)

clean_db(data)




