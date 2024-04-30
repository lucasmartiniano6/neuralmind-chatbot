import requests
from bs4 import BeautifulSoup

def fetch_and_convert(url):
    # Fetch the webpage
    response = requests.get(url)
    response.raise_for_status()  # Raises an exception for HTTP errors
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Open a text file to write the contents
    with open('output.txt', 'w', encoding='utf-8') as file:
        # Extract and write all text
        for text in soup.stripped_strings:
            file.write(text + '\n')
        
        # Find all table tags
        tables = soup.find_all('table')
        for table in tables:
            for row in table.find_all('tr'):
                row_text = ' | '.join(cell.get_text(strip=True) for cell in row.find_all(['td', 'th']))
                #file.write(row_text + '\n')
            #file.write('\n')  # Add a newline after each table for better readability

fetch_and_convert('https://www.pg.unicamp.br/norma/31594/0')
