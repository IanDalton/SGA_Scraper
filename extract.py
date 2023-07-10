from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os,csv,json,time,datetime
from dotenv import load_dotenv

def extract_sga_classes(year_min=2010,year_max=datetime.datetime.now().year,save=True):
    load_dotenv()

    # CONFIGURATIONS
    url = 'https://sga.itba.edu.ar'
    username = os.getenv("ITBA_USERNAME")
    password = os.getenv("ITBA_PASSWORD")

    username_selector = 'user'
    password_selector = 'password'
    submit_selector = 'login'

    # Create a new instance of the Chrome driver
    driver = webdriver.Edge()

    # Navigate to the login page
    driver.get(url)

    # Find the username, password, and submit elements
    username_element = driver.find_element(By.NAME, username_selector)
    password_element = driver.find_element(By.NAME, password_selector)
    submit_element = driver.find_element(By.NAME, submit_selector)

    # Enter the username and password
    username_element.send_keys(username)
    password_element.send_keys(password)

    # Click the submit button to log in
    submit_element.click()

    # Wait for the page to load
    driver.implicitly_wait(5)

    dataset = {}
    def get_info_on_page(links,year):
        # create a dictionary for the year
        if dataset.get(year) == None:
            dataset[year] = {}
        for url in links:
            #Get the name of the materia and the cuatrimestre
            datos = {}
            driver.get(url)
            materia = driver.find_element(By.XPATH,"//*[@id='content']/div[3]/div/div[1]/label").text
            cuatrimestre = driver.find_element(By.XPATH,"//*[@id='content']/div[3]/div/div[3]/div[2]/span[1]").text

            # create a dictionary for the cuatrimestre
            if dataset[year].get(cuatrimestre) == None:
                dataset[year][cuatrimestre] = {}
            #Click on the link that has the span inside that has the text "Comisiones"
            driver.find_element(By.CLASS_NAME,"tab1").click()

            #from the table extract all elements and save it in a dictionary
            tabla = driver.find_element(By.TAG_NAME,"tbody")

            # extract the data from the table into a dictionary
            for clases in tabla.find_elements(By.TAG_NAME,"tr"):
                cells = clases.find_elements(By.TAG_NAME,"td")
                datos[cells[0].text] = {
                    "horario":cells[1].text,
                    "profesores":cells[2].text.split(','),
                    "inscriptos":cells[3].text,
                }
            # add the dictionary to the dataset
            dataset[year][cuatrimestre][materia] = datos

    
    for year in range(year_min,year_max+1):
        #Click into cursos
        next_link = 1
        driver.find_element(By.XPATH,"//*[@id='content']/div[1]/div/div/div/ul/li[3]/a").click()
        driver.find_element(By.XPATH,"//*[@id='content']/div[1]/div/div/div/ul/li[3]/ul/li[3]/a").click()
        print(year)
        options = driver.find_elements(By.CLASS_NAME,"filter-td")

        # Set the cuatrimestre into all
        period = options[4]
        period.click()
        period.find_elements(By.TAG_NAME,"option")[0].click()
        #set current year as the year to search by typing it in the input
        search_year = options[5].find_element(By.TAG_NAME,"input")
        search_year.clear()
        search_year.click()
        search_year.send_keys(str(year))

        # Update the filter
        options[11].find_elements(By.TAG_NAME,"a")[0].click()

        # wait for the page to load
        time.sleep(0.5)

        # Do until the next button is disabled
        while next_link:
            try:
                next_link = driver.find_element(By.CLASS_NAME,"next").get_attribute("href")
            except:
                next_link = None
            table = driver.find_element(By.TAG_NAME,"tbody")
            rows = table.find_elements(By.TAG_NAME,"tr")



            urls = []
            # Get all the urls from the table
            for row in rows:
                cells = row.find_elements(By.TAG_NAME,"td")
                urls.append(cells[len(cells)-1].find_element(By.TAG_NAME,"a").get_attribute("href"))
            # Extract the info from the urls
            get_info_on_page(urls, year)

            # Go to the next page
            if next_link:
                driver.get(next_link)

    driver.quit()

    if save:
        #save the data in a json file
        with open("dataset.json","w") as f:
            json.dump(dataset,f)
    else: 
        return dataset

    # Quit the driver when you are done
    


def turn_into_csv(dataset=None):
    if not dataset:
        with open("dataset.json","r") as f:
            dataset = json.load(f)

    with open("dataset.csv","w",encoding="utf-8",newline="") as f:
        writer = csv.writer(f)
        headers = ["Año","Cuatrimestre","Materia","Comision","Horario","Profesores","Inscriptos"]
        writer.writerow(headers)
        todos:dict
        for ano,todos in dataset.items():
            for cuatrimestre,materias in todos.items():
                for materia,comisiones in materias.items():
                    for comision, datos in comisiones.items():
                        writer.writerow([ano,cuatrimestre,materia,comision,datos["horario"],datos["profesores"],datos["inscriptos"]])
if __name__ == "__main__":
    turn_into_csv(extract_sga_classes())
    