"""
This script takes all of the PDF files from the Northern California CHNA folder
and converts them to an easy to use csv format
"""

import os
import pandas as pd
from get_prioritized_text import get_prioritized_text
from CHNA_scripts import scrape_kaiser, convert_pdf
from sqlalchemy import create_engine
import re

# Enter the database information here so that the data can be loaded into it
DB_INFO = ""

# Where you'd like the files to be downloaded on your system
download_location = ""


## Download the pdf files from the kaiser site to a new folder
# The site location where the PDFs are
kaiser_site = "https://about.kaiserpermanente.org/community-health/about-community-health/community-health-needs-assessments"

# The base link of the site to combine with the PDF links
base_link = "https://about.kaiserpermanente.org"



# Running the PDF scraping process -> returns where the files are located
pdf_location = scrape_kaiser(kaiser_site, base_link, download_location)


# Convert all files in the Northern California directory to html
Northern_CA_pdf = os.listdir(pdf_location)

# Converting the PDF files to HTML
print('\nConverting PDF files to HTML')
for file in Northern_CA_pdf:
    filename, file_extension = os.path.splitext(file)
    if file_extension == '.pdf':
        print('\t', filename)
        convert_pdf(pdf_dir=pdf_location, format = "html", filename=filename)
    
        
# Getting the information under Prioritized Text from each html file and 
# placing them in a text file
df_list = []
base_dir = os.getcwd()
print("\nPlacing the HTML files in text files")
for file in os.listdir(base_dir):
    if os.path.splitext(file)[-1] == '.html':
        filename = os.path.splitext(file)[0]
        try:
            header = get_prioritized_text(os.path.join(base_dir, file))
            print("\t", file, '--> Completed')
        # the Modesto file has issues rendering the html correctly
        except IndexError:
            print("\n\t***{} had an error with the rendering of the HTML***\n".format(file))
            continue
        
        # appending the information to a list that can be converted to a pandas DataFrame
        number = 1
        for k,v in header.items():
            if re.match("^ *[0-9]+",k) is not None:
                ranking = int(re.match("^ *[0-9]+",k).group())
                number += 1
                
            # dropping rows with the prioritized description information and priority sections
            elif not re.search('(?i)C. Prioritized description|(?i)priority',k):
                ranking = number
                number += 1
            else:
                continue
            df_list.append(['Kaiser', 'California', filename.split(" CHNA")[0],
                            filename.replace(" ","-"), ranking, k, v])
            
# Creating a pandas DataFrame with the information from the df_list          
test_df = pd.DataFrame(df_list,columns=['source', 'state', 'region', 'document', 'importance_ranking', 'category', 'description']) 


# reformatting the category names so that they all match
test_df['category'] = test_df['category'].replace({'\(tie\)':"",'\(TIE\)':""}, regex=True)
test_df['category'] = test_df['category'].replace({"^ *[0-9]+ *\. *":""}, regex=True)
test_df['category'] = test_df['category'].replace({"\&":"and"}, regex=True)
test_df['category'] = test_df['category'].replace({"^(?i)heal$":"Healthy Eating And Active Living (HEAL)"}, regex=True)
test_df['category'] = test_df['category'].replace({"^(?i)healthy eating/active living$":"Healthy Eating And Active Living (HEAL)"}, regex=True)
test_df['category'] = test_df['category'].replace({"^(?i)healthy eating and active living.*":"Healthy Eating And Active Living (HEAL)"}, regex=True)


# Capitalizing the first letter of each word in the categories
test_df['category'] = test_df['category'].str.title()


# saving the dataframe as a csv
test_df.to_csv('CHNA_report.csv',index=False, encoding="utf-8-sig")


# Moving the DataFrame to the SQL database
engine = create_engine(DB_INFO)
test_df.to_sql('CHNA_upload_test', con=engine, if_exists='replace')



