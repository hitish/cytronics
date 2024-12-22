import streamlit as st
#import PyPDF2
import pandas as pd
import io,os
import pdfplumber
import requests
#from dotenv import load_dotenv
from model.xomad_gliner import XomadGliner
#load_dotenv()
from pydantic import BaseModel
from typing import List

class GeneDetails(BaseModel):
    gene:str = ""
    transcript:str = " "
    variant_nomenclature:str = ""
    variant_total_depth:str = ""
    zygosity:str = ""



# def create_model_from_header(header: List[str]):
#     fields = {field: (str, ...) for field in header}  # Define fields with type str
#     return type("DynamicModel", (BaseModel,), fields)


def check_password():
    def password_entered():
        #pwd = os.getenv("PASSWORD")
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

def extract_info_from_pdf(pdf_file):
    pdf_reader = pdfplumber.open(pdf_file)
    
    
    All_genes = []
    results = []
    items_to_extract = ["clinical_history"]
    pages = [1,2,3]
    #api_key = os.getenv("API_KEY")
    api_key = st.secrets["API_KEY"]
    #api_url = os.getenv("API_URL")
    api_url = st.secrets["API_URL"]
    # if page_number > len(pdf_reader.pages) or page_number < 1:
    #     st.error(f"Invalid page number. The PDF has {len(pdf_reader.pages)} pages.")
    #     return None
   
    pages = [1,2,3]
    for page_num in pages:
        tables = []
        page = pdf_reader.pages[page_num - 1]
        extracted_text = page.extract_text()
        
        model_input = {"text": extracted_text, "labels": items_to_extract}

        resp = requests.post(
            api_url,
            headers={"Authorization": f"Api-Key {api_key}"},
            json=model_input,
        )
        entity_list = resp.json()
        print(f"\n\nEntities for page no {page_num} \n")
        print(entity_list)
        print("\n\n")
        for entity in entity_list:
            results.append([entity["label"],entity["text"]])

        
        
        tables.extend(page.extract_tables())
        print(f"\n\ntables for page no {page_num} \n")
        print(tables)
        
        print("\n")
        for table in tables:
            # print("\n\n")
            # print(table)
            # print("\n\n")
            header = table[0]
            if header[0].replace("\n"," ").strip() == "Gene and Transcript":

                rows = table[1:]
                for row in rows:
                    # print("print row")
                    # print(row)
                    gene = GeneDetails()
                    try:
                        print(row[0].replace("\n"," ").strip())
                        
                        temp = row[0].replace("\n"," ").strip().split("(")
                        
                        gene.gene = temp[0].strip()
                        gene.transcript = temp[1].strip(")") 
                        
                        temp =row[2].replace("\n"," ").strip().split("[")
                        
                        gene.variant_nomenclature = temp[0].strip()
                        gene.variant_total_depth = temp[1].strip("]") 

                        gene.zygosity = row[3].replace("\n"," ").strip()
                        All_genes.append(gene)
                        results.append(["Gene Details",gene.model_dump_json()])
                    except Exception as e:
                        print(f"Error in extraction: {e}")
                        





    # df = pd.DataFrame(tables)
    # table_str = df.to_string(index=False)
          
    # print("\n\n")
    # table_str = table_str.replace("\n", " ")
    # print(table_str)

    # model_input = {"text": table_str, "labels": items_to_extract}
    # resp = requests.post(
    #     api_url,
    #     headers={"Authorization": f"Api-Key {api_key}"},
    #     json=model_input,
    # )
    # entity_list = resp.json()
    # print(entity_list)
    # for entity in entity_list:
    #     results.append([entity["label"],entity["text"],entity["score"]])


    print(All_genes)
    print(results)
    return results 

def main():
    st.title("PDF Information Extractor")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    # items_input = st.text_input("Enter items to extract (comma-separated)")
    # page_number = st.number_input("Enter page number to extract from", min_value=1, value=1)

    #if uploaded_file is not None and items_input and page_number:
    if uploaded_file is not None:
        #items_to_extract = [item.strip() for item in items_input.split(',')]

        if st.button("Extract Information"):
            pdf_file = io.BytesIO(uploaded_file.getvalue())
            #results = extract_info_from_pdf(pdf_file, items_to_extract, page_number)
            results = extract_info_from_pdf(pdf_file)
            
            #print(results)
            if results:
                df = pd.DataFrame(results, columns=['Item', 'Value'])
                st.subheader("Extracted Information")
                st.table(df)
            else:
                st.error("Failed to extract information. Please check your inputs and try again.")

if __name__ == "__main__":
    if check_password():
        main()