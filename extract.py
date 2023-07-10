from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os,csv,json,time,datetime
from dotenv import load_dotenv

load_dotenv()


# Replace these with the actual URL, username, and password
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

# Wait for the page to load (you may need to adjust the time)
driver.implicitly_wait(5)

# Now you are logged in and can navigate to other pages or scrape data

#check if urls.txt exists, if it does, read the file and skip the next part

#click on the link that has the span inside that has the text "Cursos"


dataset = {}
def get_info_on_page(links,year):
    if dataset.get(year) == None:
        dataset[year] = {}
    for url in links:
        datos = {}
        driver.get(url)
        materia = driver.find_element(By.XPATH,"//*[@id='content']/div[3]/div/div[1]/label").text
        cuatrimestre = driver.find_element(By.XPATH,"//*[@id='content']/div[3]/div/div[3]/div[2]/span[1]").text

        if dataset[year].get(cuatrimestre) == None:
            dataset[year][cuatrimestre] = {}
        #Click on the link that has the span inside that has the text "Comisiones"
        driver.find_element(By.CLASS_NAME,"tab1").click()

        #from the table extract all elements and save it in a dictionary
        tabla = driver.find_element(By.TAG_NAME,"tbody")

        for clases in tabla.find_elements(By.TAG_NAME,"tr"):
            cells = clases.find_elements(By.TAG_NAME,"td")
            datos[cells[0].text] = {
                "horario":cells[1].text,
                "profesores":cells[2].text.split(','),
                "inscriptos":cells[3].text,
            }

        dataset[year][cuatrimestre][materia] = datos





year_min = 2010
year_max = datetime.datetime.now().year
for year in range(year_min,year_max+1):
    next_link = 1
    driver.find_element(By.XPATH,"//*[@id='content']/div[1]/div/div/div/ul/li[3]/a").click()
    driver.find_element(By.XPATH,"//*[@id='content']/div[1]/div/div/div/ul/li[3]/ul/li[3]/a").click()
    print(year)
    options = driver.find_elements(By.CLASS_NAME,"filter-td")


    period = options[4]
    period.click()
    period.find_elements(By.TAG_NAME,"option")[0].click()
    #set current year as the year to search by typing it in the input
    search_year = options[5].find_element(By.TAG_NAME,"input")
    search_year.clear()
    search_year.click()
    search_year.send_keys(str(year))

    options[11].find_elements(By.TAG_NAME,"a")[0].click()
    time.sleep(0.5)
    while next_link:
        try:
            next_link = driver.find_element(By.CLASS_NAME,"next").get_attribute("href")
        except:
            next_link = None
        table = driver.find_element(By.TAG_NAME,"tbody")
        rows = table.find_elements(By.TAG_NAME,"tr")



        urls = []
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME,"td")
            urls.append(cells[len(cells)-1].find_element(By.TAG_NAME,"a").get_attribute("href"))

        get_info_on_page(urls, year)
        if next_link:
            driver.get(next_link)






# accesing each url in the list
with open("urls.json","r") as f:
    urls = json.load(f)




#save the data in a json file
with open("dataset.json","w") as f:
    json.dump(dataset,f)





        



# ...


# Quit the driver when you are done
driver.quit()

