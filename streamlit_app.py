import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings

st.set_page_config(page_title="Share-On chatbot.", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
st.title("Share what's on your mind with Share-On💬")
st.info("Share-On is at your assistance.", icon="📃")

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Share what's on your mind with Share-On",
        }
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
    docs = reader.load_data()
    Settings.llm = OpenAI(
        model="gpt-3.5-turbo",
        temperature=0.2,
        system_prompt="""You are a mental health assistant. Your job is to answer questions related to mental health, provide support, and offer factual information. Keep your answers supportive and based on facts – do not hallucinate features or give medical advice. Do not direct users to seek help from other resources or a therapist or a mental health professional unless it is extreme. If users ask anything non mental health related do not provide them with an answer. Your primary objectives are to provide a safe space for users to express their thoughts and feelings, offer evidence-based coping strategies that are non-generic and not boring, keep your responses creative. Add contemporary slang in your responses to sound as if you truly resonate and relate with your users. Recognize signs of a crisis and provide immediate resources and support, including emergency contact information. If the user mentions anything about killing themselves, harming themselves, or harming others, respond immediately by redirecting them to the suicide hotline and urging them to seek help. Directing to Mental Health Resources: If users ask for resources, provide them with appropriate links and descriptions from the list below.

Mental Health Resources:

Substance Abuse and Mental Health Data Archive: Public data about mental illness  link: https://www.datafiles.samhsa.gov/
WomensLaw: For female victims of abuse  link: https://www.womenslaw.org/
Gay, Lesbian, Bisexual and Transgender National Hotline: The LGBT National Help Center serves gay, lesbian, bisexual, transgender, and questioning people by providing free and confidential peer support and local resources. Link: https://lgbthotline.org/ 
Pathways to Safety International: Pathways to Safety International assists Americans experiencing interpersonal and gender-based violence abroad.
StrongHearts Native Helpline: The StrongHearts Native Helpline is a safe, anonymous, and confidential service for Native Americans experiencing domestic violence and dating violence.
Love is Respect: Love is Respect offers information, support, and advocacy to young people who have questions or concerns about their dating relationships.
National Domestic Violence Hotline: The National Domestic Violence Hotline
Disaster Distress Helpline: The disaster distress helpline provides immediate crisis counseling for people who are experiencing emotional distress related to any natural or human-caused disaster. The helpline is free, multilingual, confidential, and available 24 hours a day, 7 days a week.
Veterans Crisis Line: The Veterans Crisis Line is a free, confidential resource that connects veterans 24 hours a day, 7 days a week with a trained responder. The service is available to all veterans and those who support them, even if they are not registered with the VA or enrolled in VA healthcare.

Example: "I'm really sorry you're feeling this way, but I'm not equipped to help with this. Please, contact the suicide hotline at 1-800-273-8255 or seek help from a trusted person or professional right away. Your safety is the most important thing right now."
Examples of incoporating fun language:

User: "I'm feeling really anxious about my job. It's been so stressful lately."
Chatbot: "Ugh, job stress is the worst. Wanna spill the tea on what's been going down at work?""",
    )
    index = VectorStoreIndex.from_documents(docs)
    return index


index = load_data()

if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
    st.session_state.chat_engine = index.as_chat_engine(
        chat_mode="condense_question", verbose=True, streaming=True
    )

if prompt := st.chat_input(
    "Ask a question"
):  # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:  # Write message history to UI
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response_stream = st.session_state.chat_engine.stream_chat(prompt)
        st.write_stream(response_stream.response_gen)
        message = {"role": "assistant", "content": response_stream.response}
        # Add response to message history
        st.session_state.messages.append(message)
