import requests
from bs4 import BeautifulSoup

# URL of the webpage
url = "https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/sec_dm_main_source_catalogue/ssec_dm_gaia_source.html"

# Send an HTTP GET request
response = requests.get(url)

# Initialize the data storage
data = []
current_entry = None

if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Start from the paragraph with ID 'p3'
    current_p = soup.find(id='p3')
    if not current_p:
        print("Paragraph 'p3' not found")
        exit()

    while current_p and current_p.get('id') != 'p415':  # Ensure it stops before 'p415'
        ltx_anchor = current_p.find(class_='ltx_anchor')
        if ltx_anchor:
            if current_entry:  # Check if there is an ongoing entry
                # Append the completed current entry before starting a new one
                data.append(current_entry)
                print("Added entry:", current_entry['name'])  # Debugging info
            # Prepare a new entry
            text_after_colon = current_p.text.split(':', 1)[1].strip() if ':' in current_p.text else current_p.text.strip()
            current_entry = {
                'name': ltx_anchor.get('name'),
                'brief_description': text_after_colon,
                'long_description': ''  # Initialize long description
            }
        elif current_entry:  # Make sure there's an active entry before appending
            current_entry['long_description'] += (current_p.text.strip() + ' ')

        # Move to the next paragraph element
        current_p = current_p.find_next('p')

    # Append the last entry if not already saved
    if current_entry:
        data.append(current_entry)
        print("Added last entry:", current_entry['name'])  # Debugging info
    
    data.pop(0)

    # Output the collected data
    if data:
        print("\nCollected Data:\n")
        flag=0
        for entry in data:
            print("Name: ", entry['name'])
            print("Brief Description: ", entry['brief_description'])
            print("Long Description: ", entry['long_description'])
            print("--------------------------------------------------\n")
            flag+=1
            if flag>20: break
else:
    print("Failed to retrieve the webpage. Status code:", response.status_code)
