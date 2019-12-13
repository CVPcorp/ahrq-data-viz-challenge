# CHNA Scraping

These scripts serve to download the CHNA PDFs for Northern California from the Kaiser Site

**CHNA_scripts.py:** contains the "scrape_kaiser" and "convert_pdf" functions, which 
    download the correct files and convert the PDF to HTML.

**get_prioritized_text.py:** scrapes the text from the Section C. of
    the Northern California CHNA HTML files.
    
**CHNA_scraping.py:** this is the only file that needs to be run. It executes the 
    functions needed to get the information from the PDFs and loads it into the
    data warehouse specified and a CSV file.


## Instructions to Run:

In the CHNA_scraping.py file, insert the data warehouse information as the "DB_INFO" variable. 
    The required format is: dialect+driver://username:password@host:port/database.
     Then, under the "download_location" variable,
    insert the location on your local machine where you'd like the files to be
    downloaded. Finally, run the CHNA_scraping.py file.
