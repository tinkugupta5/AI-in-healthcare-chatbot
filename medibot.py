import streamlit as st

def main():
    st.title("Medical Chatbot")
    st.write("Welcome to the Medical Chatbot! Ask your medical questions below.")

    user_input = st.text_input("Enter your question:")
    
    if st.button("Submit"):
        if user_input:
            # Here you would typically call your LLM or retrieval function
            response = get_response_from_llm(user_input)
            st.write("Response:", response)
        else:
            st.write("Please enter a question.")

if __name__ == "__main__":
    main()