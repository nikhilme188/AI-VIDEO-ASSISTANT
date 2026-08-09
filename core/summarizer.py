from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable,RunnablePassthrough,RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from core.transcriber import speech_to_text
from core.llm import get_llm
from utils.audio_process import prepare_audio_chunks

def split_transcript_chunk(transcript:str)->list:
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200)
    return splitter.split_text(transcript)

def summarizer(transcript:str)->str:
    print("Inside summarizer")
    llm=get_llm()
    summary_prompt=ChatPromptTemplate.from_messages(
        [
        ("system", "Summarize this portion of a meeting transcript concisely."),
        ("human", "{text}"),
        ]
    )
    map_chain=  summary_prompt | llm |  StrOutputParser()
    chunks=split_transcript_chunk(transcript)
    print(f"Number of chunks: {len(chunks)}")
    summary_chunk=[map_chain.invoke({"text":chunk}) for chunk in chunks]
    combined="\n\n".join(summary_chunk)
    combined_summary_prompt=ChatPromptTemplate.from_messages(
        [
        ("system",   
         "You are an expert meeting summarizer. Combine these partial summaries into one final professional meeting summary in bullet points."),
        ("human", "{text}")
        ]
    )

    combined_summary_chain=  combined_summary_prompt | llm |  StrOutputParser()

    return combined_summary_chain.invoke({"text":combined})






# if __name__ == "__main__":
#     url = "https://youtu.be/UabBYexBD4k?si=SP6wKNyaCQ97JObo"

#     chunk_paths = prepare_audio_chunks(url)

#     transcript = speech_to_text(chunk_paths)


#     print(transcript)
#     print("len of transcript",len(transcript))

#     summary = summarizer(transcript)

#     print(summary)

