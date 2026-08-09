import streamlit as st

from main import run_pipeline
from core.rag_engine import ask_question


# --------------------------------------------------
# Streamlit configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AI Meeting Assistant",
    page_icon="🎙️",
    layout="wide"
)


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "result" not in st.session_state:
    st.session_state.result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# --------------------------------------------------
# UI
# --------------------------------------------------

st.title("🎙️ AI Meeting Assistant")

st.write(
    "Upload a meeting file or provide a YouTube URL "
    "to analyze and chat with your meeting."
)


# --------------------------------------------------
# Input
# --------------------------------------------------

import tempfile
import os

source = st.text_input(
    "YouTube URL",
    placeholder="Enter YouTube URL..."
)

uploaded_file = st.file_uploader("Or upload an audio file", type=["mp3", "wav", "m4a", "mp4", "webm"])

process = st.button(
    "Process Meeting",
    type="primary"
)

# --------------------------------------------------
# Run your existing pipeline
# --------------------------------------------------

if process:
    if not source and not uploaded_file:
        st.warning("Please enter a YouTube URL or upload a file.")
    else:
        with st.spinner("Processing meeting..."):
            try:
                # If file is uploaded, save it to a temporary file
                if uploaded_file is not None:
                    # Create a temporary file
                    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") 
                    tfile.write(uploaded_file.read())
                    # The source for the pipeline is now the path to this temp file
                    target_source = tfile.name
                else:
                    # Otherwise, use the YouTube URL
                    target_source = source
                
                result = run_pipeline(target_source)
                
                # Clean up the temp file if one was created
                if uploaded_file is not None:
                    os.remove(target_source)

                st.session_state.result = result
                st.session_state.chat_history = []

                st.success("Meeting processed successfully!")

            except Exception as e:
                error_msg = str(e)
                if "Sign in to confirm you’re not a bot" in error_msg:
                    st.error("YouTube blocked the download from this cloud server (bot protection). Please download the audio locally and upload the file instead.")
                else:
                    st.error("Something went wrong.")
                    st.exception(e)


# --------------------------------------------------
# Display results
# --------------------------------------------------

result = st.session_state.result


if result is not None:

    st.divider()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Summary",
            "Action Items",
            "Decisions",
            "Open Questions",
            "Transcript",
            "Chat"
        ]
    )


    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    with tab1:

        st.header("📋 Summary")

        st.write(
            result["summary"]
        )


    # --------------------------------------------------
    # Action Items
    # --------------------------------------------------

    with tab2:

        st.header("Action Items")

        st.write(
            result["action_items"]
        )


    # --------------------------------------------------
    # Decisions
    # --------------------------------------------------

    with tab3:

        st.header("Key Decisions")

        st.write(
            result["key_decisions"]
        )


    # --------------------------------------------------
    # Questions
    # --------------------------------------------------

    with tab4:

        st.header("Open Questions")

        st.write(
            result["open_questions"]
        )


    # --------------------------------------------------
    # Transcript
    # --------------------------------------------------

    with tab5:

        st.header("Transcript")

        st.text_area(
            "Transcript",
            result["transcript"],
            height=500
        )


    # --------------------------------------------------
    # Chat
    # --------------------------------------------------

    with tab6:

        st.header("Chat with your meeting")

        # Display previous messages
        for message in st.session_state.chat_history:

            with st.chat_message(
                message["role"]
            ):

                st.write(
                    message["content"]
                )


        question = st.chat_input(
            "Ask something about the meeting..."
        )


        if question:

            # Display user question

            with st.chat_message("user"):

                st.write(question)


            st.session_state.chat_history.append(
                {
                    "role": "user",
                    "content": question
                }
            )


            # Use YOUR existing function

            with st.chat_message("assistant"):

                with st.spinner("Thinking..."):

                    try:

                        answer = ask_question(
                            result["rag_chain"],
                            question
                        )

                        st.write(answer)

                        st.session_state.chat_history.append(
                            {
                                "role": "assistant",
                                "content": answer
                            }
                        )

                    except Exception as e:

                        st.error(
                            "Unable to answer the question."
                        )

                        st.exception(e)

