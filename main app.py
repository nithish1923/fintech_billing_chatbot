import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import CONVERSATION_PROMPT

st.set_page_config(page_title="Fintech Billing Extractor Chatbot")

# Initialize OpenAI Chat model
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
chat_model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.3)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
conversation = ConversationChain(
    llm=chat_model,
    memory=memory,
    prompt=CONVERSATION_PROMPT,
)

st.title("Fintech Billing Extractor Chatbot")

uploaded_files = st.file_uploader(
    "Upload multiple invoice PDFs", type=["pdf"], accept_multiple_files=True
)

# Placeholder for extracted data rows
extracted_rows = []

# Chatbot interaction to ask user for fields
st.header("Chat with Billing Assistant")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def user_message():
    return st.text_input("Ask which billing fields to extract or type 'start extraction'")

user_input = user_message()

if user_input:
    # Append user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Get response from chatbot
    response = conversation.predict(input=user_input)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.write("**Assistant:**", response)

# Function to extract text from PDFs
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Button to trigger extraction and Excel generation
if st.button("Extract Data and Generate Excel"):
    if not uploaded_files:
        st.error("Please upload PDF invoice files first.")
    else:
        # For demo: extract simple fields by searching for user requested fields in chat
        # Parse fields from last user input (naive approach)
        fields = []
        last_user_text = (
            st.session_state.chat_history[-2]["content"]
            if len(st.session_state.chat_history) >= 2
            else ""
        )
        # Simple keywords check
        keywords = ["invoice number", "vendor", "date", "total amount", "amount", "due date"]
        for kw in keywords:
            if kw in last_user_text.lower():
                fields.append(kw)

        if not fields:
            # Default fields if user did not specify
            fields = ["invoice number", "vendor", "date", "total amount"]

        for file in uploaded_files:
            text = extract_text_from_pdf(file)
            # Very naive extraction: search lines for each field keyword
            row = {}
            lines = text.split("\n")
            for field in fields:
                # Find line with field keyword and extract text after colon or keyword
                value = ""
                for line in lines:
                    if field in line.lower():
                        parts = line.split(":")
                        if len(parts) > 1:
                            value = parts[1].strip()
                        else:
                            value = line.replace(field, "").strip()
                        break
                row[field] = value
            row["filename"] = file.name
            extracted_rows.append(row)

        if extracted_rows:
            df = pd.DataFrame(extracted_rows)
            towrite = BytesIO()
            df.to_excel(towrite, index=False, engine="openpyxl")
            towrite.seek(0)
            st.success("Excel file generated!")
            st.download_button(
                label="Download Excel",
                data=towrite,
                file_name="extracted_billing_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.warning("No data extracted. Try specifying billing fields in chat first.")

# Show chat history
if st.session_state.chat_history:
    st.subheader("Chat History")
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f"**You:** {chat['content']}")
        else:
            st.markdown(f"**Assistant:** {chat['content']}")
