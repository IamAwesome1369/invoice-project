import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import re
import pandas as pd

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def parse_invoice(text):
    print("Extracted text:", text)  # Debugging statement
    invoice_data = {}

    # Extract invoice number
    invoice_number_match = re.search(r"(Invoice|Invoice #|Invoice Number|Inv #|Inv No)\s*[:#-]?\s*(\S+)", text, re.IGNORECASE)
    if invoice_number_match:
        invoice_data['invoice_number'] = invoice_number_match.group(2)
    else:
        invoice_data['invoice_number'] = "Not Found"
    print("Invoice Number:", invoice_data['invoice_number'])  # Debugging statement

    # Extract date
    date_match = re.search(r"(Date|Invoice Date|Inv Date)\s*[:#-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})", text, re.IGNORECASE)
    if date_match:
        invoice_data['date'] = date_match.group(2)
    else:
        date_match_alt = re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", text)
        invoice_data['date'] = date_match_alt.group(0) if date_match_alt else "Not Found"
    print("Date:", invoice_data['date'])  # Debugging statement

    # Extract total amount
    total_amount_match = re.search(r"(Total|Total Amount|Grand Total)\s*[:#-]?\s*\$?([\d,]+\.\d{2})", text, re.IGNORECASE)
    if total_amount_match:
        invoice_data['total_amount'] = total_amount_match.group(2)
    else:
        invoice_data['total_amount'] = "Not Found"
    print("Total Amount:", invoice_data['total_amount'])  # Debugging statement
    
    # Example of extracting line items
    line_items = []
    line_item_pattern = re.compile(r"(Item|Description)\s*(Quantity|Qty)\s*(Price|Amount)", re.IGNORECASE)
    line_items_start = line_item_pattern.search(text)
    if line_items_start:
        items_text = text[line_items_start.end():]
        item_matches = re.finditer(r"(\w+.*)\s+(\d+)\s+\$([\d,]+\.\d{2})", items_text)
        for match in item_matches:
            item = {
                'description': match.group(1).strip(),
                'quantity': match.group(2).strip(),
                'price': match.group(3).strip()
            }
            line_items.append(item)
    invoice_data['line_items'] = line_items
    
    print("Line Items:", invoice_data['line_items'])  # Debugging statement
    return invoice_data

def convert_to_dataframe(invoice_data):
    if not invoice_data['line_items']:  # Check if line_items is empty
        return pd.DataFrame(columns=['description', 'quantity', 'price', 'invoice_number', 'date', 'total_amount'])

    df = pd.DataFrame(invoice_data['line_items'])
    df['invoice_number'] = invoice_data['invoice_number']
    df['date'] = invoice_data['date']
    df['total_amount'] = invoice_data['total_amount']
    return df

# Example usage:
def main():
    pdf_text = extract_text_from_pdf('C:\\Visual Studio\\invoice project\\exampleInvoices\\5929168515995319483.pdf')
    print("Extracted text from PDF:", pdf_text)  # Debugging statement
    invoice_data = parse_invoice(pdf_text)
    df = convert_to_dataframe(invoice_data)
    print("DataFrame:\n", df)  # Debugging statement
    df.to_csv('output.csv', index=False)
    print("CSV file has been saved.")  # Debugging statement

if __name__ == "__main__":
    main()
