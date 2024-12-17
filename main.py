import streamlit as st
#import PyPDF2
import pandas as pd
import io
import pdfplumber
from model.xomad_gliner import XomadGliner


# Simple authentication
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
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

def extract_info_from_pdf(pdf_file, items_to_extract, page_number):
    pdf_reader = pdfplumber.open(pdf_file)
    
    tables = []
    if page_number > len(pdf_reader.pages) or page_number < 1:
        st.error(f"Invalid page number. The PDF has {len(pdf_reader.pages)} pages.")
        return None
   
    page = pdf_reader.pages[page_number - 1]
    tables.extend(page.extract_tables())
    
    df = pd.DataFrame(tables)
    table_str = df.to_string(index=False)
    print(table_str)
    print(items_to_extract)
    #labels = items_to_extract.split(",")
    results = []
    model = XomadGliner()
    entity_list = model.detect(table_str,items_to_extract)
    print(entity_list)
    for entity in entity_list:
        results.append([entity["label"],entity["text"]])
    return results 

def main():
    st.title("PDF Information Extractor")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    items_input = st.text_input("Enter items to extract (comma-separated)")
    page_number = st.number_input("Enter page number to extract from", min_value=1, value=1)

    if uploaded_file is not None and items_input and page_number:
        items_to_extract = [item.strip() for item in items_input.split(',')]

        if st.button("Extract Information"):
            pdf_file = io.BytesIO(uploaded_file.getvalue())
            results = extract_info_from_pdf(pdf_file, items_to_extract, page_number)

            if results:
                df = pd.DataFrame(results, columns=['Item', 'Value'])
                st.subheader("Extracted Information")
                st.table(df)
            else:
                st.error("Failed to extract information. Please check your inputs and try again.")

if __name__ == "__main__":
    if check_password():
        main()