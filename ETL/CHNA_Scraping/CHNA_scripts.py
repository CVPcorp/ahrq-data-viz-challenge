from bs4 import BeautifulSoup
import requests
import os
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, XMLConverter, HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO


def scrape_kaiser(kaiser_site, base_link, download_location):
    """
    Scrapes the Northern California CHNA section of the Kaiser site and downloads
    the PDF files
    
    Parameters
    ---------------------
    kaiser_site: the link to where the PDFs are located
    base_link: the base link to the Kaiser site (usually 'https://about.kaiserpermanente.org')
    download_location: the location where you'd like the files downloaded
    """
    
    response = requests.get(kaiser_site)
    soup = BeautifulSoup(response.text, "html.parser")
    
    for header in soup.find_all('h3'):
        if header.get_text() == 'Northern California':
            tables = header.nextSibling.nextSibling
    
    tables = tables.find_all('a')   
        
    # Creating a dictionary to store the links and region names
    links = {}
    for table in tables:
        links[table.get_text().strip()] = base_link + table.get('href')
    
    folder_name = os.path.join(download_location,'Kaiser_CHNA')
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    
    os.chdir(folder_name)
    for region_name, link in links.items():
        r = requests.get(link)
        filename = region_name +'.pdf'
        with open(filename, 'wb') as f:
            f.write(r.content)
            
    print("\nPDF files were downloaded to: {}".format(os.getcwd()))
    return os.getcwd()          
            

def convert_pdf(pdf_dir, filename, format='txt', codec='utf-8', password=''):
    
    """
    Converts PDF files to either txt, html, or xml files
    
    Parameters
    ---------------------------
    pdf_dir: the path to where the pdf file is located
    filename: the name of the file
    format: the format the pdf will be extracted to
    codec: the decoding format
    password: password, if any
    """
    
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    laparams = LAParams()
    if format == 'txt':
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'html':
        device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'xml':
        device = XMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    else:
        raise ValueError('provide format, either text, html or xml!')
    fp = open(os.path.join(pdf_dir, filename)+'.pdf', 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue().decode()
    fp.close()
    device.close()
    retstr.close()
    os.chdir(pdf_dir)
    if not os.path.exists('CHNA'+'_'+format):
        os.mkdir('CHNA'+'_'+format)
    os.chdir('CHNA'+'_'+format)
    with open(filename+"."+format, "w",encoding="utf-8") as f:
        f.write(text)  
     
