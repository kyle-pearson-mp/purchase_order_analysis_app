import streamlit as st
import pandas as pd
import pdfplumber
import os
import re
import zipfile
import tempfile
#%%

st.title('Xcel Invoice Extraction')

df = pd.DataFrame()
folder_path = r"C:\Users\KylePearson\Downloads\Fw_ XCL515 Invoicing Review - May"
def add_row(df, po_num, description, wbs, pm_order, total_price):
    new_row = {'PO Number': po_num,
               'Description': description,
               'WBS': wbs,
               'PM Order': pm_order,
               'Total Price': total_price}
    new_row = pd.DataFrame([new_row])
    df = pd.concat([new_row, df])
    return df

def extract_invoice_data(pdf, df):
    print(pdf)
    with pdfplumber.open(pdf) as pdf:
        i = 0
        for page in pdf.pages:
            if i > 1:
                continue
            text = page.extract_text()
            if text:
                match = re.search(r'\b\d{1,2}/\d{1,2}/\d{4}\s+(\d{5})\b', text)
                if match:
                    po_num = match.group(1)
                    #st.write("Invoice Number:", invoice_number)
                
                match = re.search(r'\bTOTAL\b\s*\$\s*([\d\s,]+\.\d{2})', text)
                if match and i == 0:
                    description = match.group(1)

                match = re.search(r'Expenses? (?:TOTAL|Subtotal)[^\d]*\$([\d,]+\.\d{2})', text, re.IGNORECASE)
                if match:
                    wbs = match.group(1)
                
                match = re.search(r'PO\s*No\.\s*(\d+)', text, re.IGNORECASE)
                if match:
                    pm_order = match.group(1).strip()
                match = re.search(r'\b\d{1,2}/\d{1,2}/\d{4}\s+(\d{10})\b', text)
                if match:
                    total_price = match.group(1).strip()
                i += 1
    try:
        df = add_row(df, po_num, description, wbs, pm_order, total_price)
    except:
        st.write(text)
        df = add_row(df, po_num, description, wbs, pm_order, total_price)
    return df

st.title("Upload a ZIP of Invoice PDFs")
uploaded_zips = st.file_uploader("Upload ZIP file", type="zip", accept_multiple_files=True)

if uploaded_zips:
    for uploaded_zip in uploaded_zips:
        st.subheader(f"Processing: {uploaded_zip.name}")

        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "uploaded.zip")
            
            # Save uploaded zip to temp directory
            with open(zip_path, "wb") as f:
                f.write(uploaded_zip.read())
    
            # Extract zip contents
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)
                st.success("ZIP file extracted!")      
                pdf_files = []
                for root, dirs, files in os.walk(tmpdir):
                    for file in files:
                        if file.lower().endswith(".pdf"):
                            pdf_files.append(os.path.join(root, file))
                # List PDF files
                #pdf_files = [f for f in os.listdir(tmpdir) if f.lower().endswith(".pdf")]
                #st.write("Found PDF files:")
                for pdf_path in pdf_files:
                    #pdf_path = os.path.join(tmpdir, pdf)
                    df = extract_invoice_data(pdf_path, df)
                st.success("Invoice Data extracted!")
                
st.subheader('Invoice data')
st.write(df)