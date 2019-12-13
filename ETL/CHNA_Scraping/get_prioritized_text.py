import os
from bs4 import BeautifulSoup
import re


def get_prioritized_text(filepath):
    """
    This function specifically scrapes the HTML format of the Northern California
    CHNA PDFs and extracts the information from the section:
        `C. Prioritized description of all the community needs identified through the CHNA`
        
    Returns as output a dictionary with the format -> {header: text}
    
    Also saves a txt file of the html scraping as filepath.html
    
    """
    
    # opening the file and making it parseable through BeautifulSoup
    with open(filepath, encoding="utf-8") as f:
        soup = BeautifulSoup(f, features="lxml")
        
    # Getting the indices for the relevant sections
    indices_section_c = []
    indices_section_d = []
    for i, div in enumerate(soup.find_all("span")):
        if "C. Prioritized description" in div.get_text():
            indices_section_c.append(i)
        elif "D. Community resources potentially" in div.get_text():
            indices_section_d.append(i)  
    
    # Only selecting the data from the relevant section
    relevant_section = soup.find_all("span")[indices_section_c[-1]:indices_section_d[-1]]
    
    # defining lists to append information to
    # bold_list contains the header information
    # text_list contains the body information
    bold_list = []
    bold_text = ""
    text_list = []
    sample_str = ""
    
    # getting a list of the bold (headers) text and the content text
    for i, item in enumerate(relevant_section):
        if (item.get_text().upper() == item.get_text() or 'bold' in item.attrs['style'].lower()) \
        and 'priority' in item.get_text().lower():
            bold_list.append(item.get_text())
            text_list.append("BREAK")
            text_list.append("PRIORITY LINE")
            text_list.append("BREAK")
        elif "prioritized description of all the community needs" in item.get_text().lower():
            bold_list.append(item.get_text())
            text_list.append("BREAK")
            
        elif 'bold' in item.attrs['style'].lower() and item.get_text().upper() == item.get_text() and \
        item.get_text() != " " and item.get_text() != "\n" and item.get_text() != "" and item.get_text() != ".":
            bold_text += item.get_text()
            text_list.append("BREAK")
            
        elif 'bold' in item.attrs['style'].lower() and len(item.get_text()) > 1 \
            and item.get_text() != "\n" and len(item.get_text().lstrip()) == 1:
                continue
        elif 'bold' in item.attrs['style'].lower() and len(item.get_text()) > 1 \
            and item.get_text() != "\n":
            bold_text += item.get_text()
            text_list.append("BREAK")
    
        else:
            for a in item.childGenerator():
                if '12px' in item.attrs['style'] or '9px' in item.attrs['style'] or \
                '8px' in item.attrs['style'] or '13px' in item.attrs['style'] or \
                '10px' in item.attrs['style'] or '6px' in item.attrs['style']:
                    break
                elif 'bold' in item.attrs['style'].lower() and item.get_text() == "\n":
                    break
                elif '15px' in item.attrs['style'] and item.get_text().rstrip().isnumeric():
                    break
                elif "br" in str(a):
                    text_list.append(sample_str)
                    sample_str = ""
                    break
                sample_str += item.get_text()
    
            bold_list.append(bold_text)
            bold_text = ""
           
    text_list.append("BREAK")
    
    bold_list = [item for item in bold_list if item != "" and item != "\n" and item != " "]
    text_list = [l for l in text_list if l != "\n"]
    
    # editing the bold list so that special characters aren't on their own line
    # i.e. numbered items or parenthesis
    new_bold_list = []
    for i, text in enumerate(bold_list):
        new_bold_list.append(text.split("\n"))
    
    # removing sections with (TIE) in them
    new_bold_list = [t for text in new_bold_list for t in text if t!= '' and t.lower() != '(tie)']
    new_bold_list = [word.strip() for word in new_bold_list]
    
    # combining parts of the headers so that they're all on the correct lines
    a = False
    while not a:
        for i, text in enumerate(new_bold_list):
            if len(text) <= 1 and text != '.':
                new_bold_list[i] = new_bold_list[i] + new_bold_list[i+1]
                del new_bold_list[i+1]
                break
            elif len(text) <= 8 and text[0].isnumeric():
                new_bold_list[i] = new_bold_list[i] + " " + new_bold_list[i+1]
                del new_bold_list[i+1]
                break
            elif text[-1]=="&":
                new_bold_list[i] = new_bold_list[i] + " " + new_bold_list[i+1]
                del new_bold_list[i+1]
                break
            elif text == '.':
                del new_bold_list[i]
                break
            else:
                continue
        
        
        if i == len(new_bold_list)-1:
            a = True
    
    # keeping items that don't contain special characters
    bold_list = [item for item in new_bold_list if re.match("[A-Za-z0-9]+",item) is not None]

    section_text = ""
    section_text_list = []
    
    # creating a list with the consolidated text for each section
    for item in text_list:
        if 'BREAK' not in item:
            section_text += item
        else:
            section_text_list.append(section_text)
            section_text = ""
       
    section_text_list = [section.replace("\n","") for section in section_text_list]   
    section_text_list = [item for item in section_text_list if item != ""]
    if len(bold_list) -1 == len(section_text_list):
        section_text_list.insert(0,"<HEADER>")
    elif len([i for i in section_text_list if 'PRIORITY' not in i]) == len(bold_list):
        section_text_list = [i for i in section_text_list if 'PRIORITY' not in i] 
        
    # removing the colons in the beginning of the text and the end of the headers
    section_text_list = [section.strip() for section in section_text_list]
    new_section_text_list = []
    for section in section_text_list:
        if section[0] == ':':
            section = section[1:]
            new_section_text_list.append(section.strip())
        else:
            new_section_text_list.append(section)
            
    bold_list = [sentence[:-1] if sentence[-1] == ':' else sentence for sentence in bold_list]
    
    
    # creating a final dictionary with the headers as keys and corresponding text as
    # values
    header_dict = {}
    for i, section in enumerate(new_section_text_list):
        header_dict[bold_list[i]] = section    
        
    # exporting the information to a text file
    filename = os.path.basename(filepath)
    file = os.path.splitext(filename)[0]
    with open(file + '.txt','w') as f:
        for k,v in header_dict.items():
            f.write(str(k) + '\n' + '\t' + str(v) + '\n\n\n')
        
    return header_dict