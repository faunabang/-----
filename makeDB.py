import requests
from bs4 import BeautifulSoup
import sqlite3

# URL of the webpage
url = "https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dm_main_source_catalogue/ssec_dm_gaia_source.html"

# Initialize SQLite Database
conn = sqlite3.connect('gaia_parameters.db')
c = conn.cursor()

# Ensure the table is set up correctly
c.execute('DROP TABLE IF EXISTS gaia_parameters')  # Drop existing table for debugging
c.execute('''
CREATE TABLE gaia_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    brief_description TEXT,
    long_description TEXT
)
''')
conn.commit()

# Send an HTTP GET request
response = requests.get(url)

if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Start from the paragraph with ID 'p3'
    current_p = soup.find(id='p3')
    if not current_p:
        print("Paragraph 'p3' not found")
        exit()

    current_entry = None

    while current_p and current_p.get('id') != 'p415':  # Ensure it stops before 'p415'
        ltx_anchor = current_p.find(class_='ltx_anchor')
        if ltx_anchor:
            # Strip the prefix "gaia_source-" if present in the name
            name = ltx_anchor.get('name').replace('gaia_source-', '')
            
            if current_entry:  # Check if there is an ongoing entry
                # Save the completed current entry to the database
                c.execute('INSERT INTO gaia_parameters (name, brief_description, long_description) VALUES (?, ?, ?)',
                          (current_entry['name'], current_entry['brief_description'], current_entry['long_description']))
                print("Inserted:", current_entry)  # Debugging info
            
            # Prepare a new entry
            text_after_colon = current_p.text.split(':', 1)[1].strip() if ':' in current_p.text else current_p.text.strip()
            current_entry = {
                'name': name,
                'brief_description': text_after_colon,
                'long_description': ''  # Initialize long description
            }
        elif current_entry:  # Make sure there's an active entry before appending
            current_entry['long_description'] += (current_p.text.strip() + ' ')

        # Move to the next paragraph element
        current_p = current_p.find_next('p')

    # Append the last entry if not already saved
    if current_entry:
        c.execute('INSERT INTO gaia_parameters (name, brief_description, long_description) VALUES (?, ?, ?)',
                  (current_entry['name'], current_entry['brief_description'], current_entry['long_description']))
        print("Inserted last entry:", current_entry)  # Debugging info

    conn.commit()
    print("Data successfully saved to SQLite database.")
else:
    print("Failed to retrieve the webpage. Status code:", response.status_code)

# Close the database connection
conn.close()
