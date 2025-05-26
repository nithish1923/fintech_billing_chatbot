# fintech_billing_chatbot

This is a simple Streamlit app that allows fintech users to upload multiple PDF invoices, chat with an AI assistant to select which billing fields to extract, and generate an Excel file with extracted data.

## Features
- Upload multiple PDF invoice files
- Chat with AI agent to specify fields like invoice number, vendor name, date, total amount, etc.
- Extracts text using pdfplumber
- Uses OpenAI GPT via LangChain as chatbot agent backend
- Generates downloadable Excel with extracted billing info


