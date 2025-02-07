import openai
import streamlit as st
from openai import OpenAI

get_all_items = st.session_state.functions['get_all_items']

st.set_page_config(
    page_title="Chat Assistant 🤖",
    layout="wide",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None,
    }
)

st.title("💬 Chatbot")
st.write("Welcome to the Chat Assistant page! Ask questions about the items in our store.")


def check_openai_api_key(api_key):
    client_exists = OpenAI(api_key=api_key)
    try:
        client_exists.models.list()
    except openai.AuthenticationError:
        return False
    else:
        return True


with st.sidebar:
    if "openai_api_key" not in st.session_state or not st.session_state.openai_api_key:
        st.session_state.openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
        if st.session_state.openai_api_key:
            st.success("API key saved!")
    else:
        st.text("Using saved OpenAI API Key")
        st.write("✔️ Your API key is already set.")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

    if st.button("Reset API Key"):
        del st.session_state["openai_api_key"]


if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello! How can I help you?"}]
if "prompt_count" not in st.session_state:
    st.session_state["prompt_count"] = 0

items = get_all_items()

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if st.session_state["prompt_count"] < 5 and (prompt := st.chat_input()):
    if "openai_api_key" not in st.session_state or not st.session_state.openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    st.session_state["prompt_count"] += 1
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    store_context = (
            "You are a store assistant chatbot. You can answer questions about stock and prices "  
            "using the provided product data. If a user wants to purchase an item, you should "
            "guide them to the Home page to add it to their cart if it's available in stock. "
            "Here is the store's product data:\n" +
            "\n".join([f"{item['name']} has {item['item_stock']} in stock, priced at {item['price']}."
                       for item in items])
    )

    context_messages = st.session_state.messages + [{"role": "system", "content": store_context}]

    client = OpenAI(api_key=st.session_state.openai_api_key)
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=context_messages)

    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

if st.session_state["prompt_count"] >= 5:
    st.warning("You have reached the maximum of 5 prompts for this session. Please refresh the page to restart.")
