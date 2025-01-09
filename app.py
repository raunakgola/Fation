import streamlit as st
import logging
from langchain_ollama import OllamaLLM

# Set up logging to save logs to a file
logging.basicConfig(
    filename='app.log',  # Save logs in app.log
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Available LLMs
LLM_OPTIONS = {
    "Mistral": "mistral",
    "PHI-3": "phi3",
    "LLaMa-3": "llama3",
}

# Initialize the default LLM
if "selected_llm" not in st.session_state:
    st.session_state.selected_llm = "Mistral"

def initialize_llm(model_name):
    try:
        return OllamaLLM(model=model_name)
    except Exception as e:
        logger.error("Error initializing LLM: %s", e)
        return None

llm = initialize_llm(LLM_OPTIONS[st.session_state.selected_llm])

# Define the system prompt
SYSTEM_PROMPT = """You are an expert outfit recommender. 
Based on the user's prompt, provide two outfit suggestions from the following list: 
[kudta, sherwani, tuxedo, shirt, t-shirt, jeans, shorts, indo-western, jacket, blazer, pants, saree, kurti, lehenga, gown, dress, top, skirt, long skirt, suit]. 
Each recommendation should be detailed and tailored to the context provided in the prompt. 
Your response should be between 200-300 words. 
"""

# Function to get the bot's response
def generate_text(question):
    try:
        response = llm.invoke(
            SYSTEM_PROMPT + f" Here is the user's prompt: {question}",
            stop=['<|eot_id|>']
        )
        return response
    except Exception as e:
        logger.error("Error generating response: %s", e)
        return "Sorry, I encountered an issue generating a response. Please try again."

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []

# Function to start a new chat
def start_new_chat():
    chat_name = f"Chat {len(st.session_state.chat_history) + 1}"
    st.session_state.chat_history[chat_name] = []
    st.session_state.current_chat = chat_name

# Sidebar for model selection and chat management
st.set_page_config(page_title="Fashion Station", page_icon="👗", layout="wide")
with st.sidebar:

    # Start a new chat
    if st.button("Start New Chat 💬"):
        start_new_chat()

    # Select LLM
    st.title("Options")
    st.session_state.selected_llm = st.selectbox("Select LLM", options=list(LLM_OPTIONS.keys()))
    llm = initialize_llm(LLM_OPTIONS[st.session_state.selected_llm])
    # Add space between "Select LLM" and "Start New Chat"
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)

    # Display existing chats
    st.write("### Saved Chats")
    for chat_name in st.session_state.chat_history:
        if st.button(chat_name):
            st.session_state.current_chat = chat_name

# Streamlit app setup
st.title("Fashion Station")
st.subheader("Chat with different LLM's Models 🤖 and have recommendations on clothing 👕👗 and wardrobe 🛍️.")

# Ensure a chat is initialized
if not st.session_state.current_chat:
    start_new_chat()

current_chat = st.session_state.current_chat
chat_history = st.session_state.chat_history[current_chat]

# Display chat history
for message in chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Prompt for user input and save to chat history
if user_input := st.chat_input("Ask for outfit recommendations!"):  # Using chat_input instead of text_input
    # Immediately display the user's query
    with st.chat_message("user"):
        st.markdown(user_input)
    chat_history.append({"role": "user", "content": user_input})

    # Generate the bot's response with error handling
    response = generate_text(user_input)
    with st.chat_message("assistant"):
        st.markdown(response)
    chat_history.append({"role": "assistant", "content": response})

    # Save chat history to a file
    try:
        with open("responses.txt", "w", encoding="utf-8") as file:
            for chat_name, messages in st.session_state.chat_history.items():
                file.write(f"{chat_name}:\n")
                for message in messages:
                    file.write(f"  {message}\n")
    except Exception as e:
        logger.error("Error saving chat history: %s", e)
