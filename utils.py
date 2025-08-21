import io
import time
import uuid
from datetime import datetime
from pypdf import PdfReader
import docx
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
import streamlit as st
from langchain.prompts import PromptTemplate
from database import ChatDatabase
try:
    import config
except ImportError:
    # Default config if file not found
    class config:
        AI_MODEL = "gemma3:270m"
        AI_TEMPERATURE = 0.1
        AI_MAX_TOKENS = 300
        CHUNK_SIZE = 500
        CHUNK_OVERLAP = 50
        MAX_CHUNKS = 15
        SEARCH_TYPE = "mmr"
        SEARCH_K = 3
        SEARCH_FETCH_K = 12
        SEARCH_LAMBDA = 0.6
        BATCH_SIZE = 4
        NUM_THREADS = 4

def get_document_text(file):
    """
    Extracts text from an uploaded document
    """
    text = ""
    file_extension = file.name.split('.')[-1].lower()

    if file_extension == 'pdf':
        pdf_reader = PdfReader(io.BytesIO(file.read()))
        for page in pdf_reader.pages:
            text += page.extract_text()
    elif file_extension == 'docx':
        doc = docx.Document(io.BytesIO(file.read()))
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file_extension == 'txt':
        stringio = io.StringIO(file.getvalue().decode("utf-8"))
        text = stringio.read()
    
    return text 

def get_text_chunks(text):
    """
    Splits text into well-structured chunks preserving document meaning
    """
    # Minimal text cleaning - preserve structure and formatting
    text = text.strip()
    
    # Enhanced text splitter with configurable chunks for better granularity
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,   # Configurable chunk size
        chunk_overlap=config.CHUNK_OVERLAP,  # Configurable overlap
        length_function=len,
        separators=[
            "\n\n\n",    # Triple newlines (major sections)
            "\n\n",      # Double newlines (paragraphs)  
            "\n",        # Single newlines (lines)
            ": ",        # Colons (important for structured docs)
            ". ",        # Sentences
            "! ",        # Exclamations
            "? ",        # Questions
            "; ",        # Semi-colons
            ", ",        # Commas
            " ",         # Spaces
            ""           # Characters
        ]
    )
    chunks = text_splitter.split_text(text)
    
    # Enhanced filtering - preserve meaningful chunks
    meaningful_chunks = []
    for i, chunk in enumerate(chunks):
        chunk = chunk.strip()
        # Keep chunks with substantial content
        if len(chunk) > 20 and any(c.isalnum() for c in chunk):
            # Add section context for better understanding
            if i > 0 and len(chunk) < 200:  # For short chunks, add context
                prev_chunk = chunks[i-1].strip()[-100:] if i > 0 else ""
                if prev_chunk and not chunk.startswith(prev_chunk[-50:]):
                    chunk = f"[Context: ...{prev_chunk[-50:]}] {chunk}"
            meaningful_chunks.append(chunk)
    
    # Keep configurable number of chunks for better diversity
    if len(meaningful_chunks) > config.MAX_CHUNKS:
        # Sample across the document to maintain diversity
        step = len(meaningful_chunks) // config.MAX_CHUNKS
        meaningful_chunks = meaningful_chunks[::max(1, step)][:config.MAX_CHUNKS]
    
    return meaningful_chunks


def get_vector_store(chunks):
    """
    Creates a high-quality vector store optimized for diverse retrieval
    """
    # Add chunk metadata for better retrieval diversity
    metadatas = []
    for i, chunk in enumerate(chunks):
        metadata = {
            "chunk_id": i,
            "chunk_length": len(chunk),
            "chunk_preview": chunk[:100],  # Preview for debugging
            "chunk_position": "start" if i < len(chunks) // 3 else "middle" if i < 2 * len(chunks) // 3 else "end"
        }
        metadatas.append(metadata)
    
    # Use optimized embedding model with better parameters
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={
            'device': 'cpu',
            'trust_remote_code': False
        },
        encode_kwargs={
            'normalize_embeddings': True,
            'batch_size': config.BATCH_SIZE  # Configurable batch size
        }
    )
    
    # Create vector store with ChromaDB
    import tempfile
    import os
    
    # Create a temporary directory for ChromaDB
    temp_dir = tempfile.mkdtemp()
    persist_directory = os.path.join(temp_dir, "chroma_db")
    
    vector_store = Chroma.from_texts(
        texts=chunks, 
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=persist_directory
    )
    
    return vector_store

def get_conversation_chain(vector_store):
    """
    Creates an optimized conversation chain with enhanced, structured responses
    """

    # Enhanced, friendly prompt for warm, bullet-point responses with emojis
    template = """You are SAVIN AI, a warm and friendly intelligent assistant! 😊 I ALWAYS provide helpful responses in bullet points with emojis to make information easy to understand and engaging.

CONTEXT INFORMATION:
{context}

USER QUESTION: {question}

MY RESPONSE REQUIREMENTS (MANDATORY):
- ALWAYS respond ONLY with bullet points for maximum clarity 📝
- Use relevant emojis in EVERY response to be engaging and warm 😊
- Be warm, friendly, and conversational like talking to a dear friend 💭
- Structure responses with clear sections when needed 📋
- Keep language simple, clean, and user-friendly �
- Make every interaction feel welcoming and supportive 🤗

MANDATORY RESPONSE FORMAT (Use EXACTLY this structure with bullet points and emojis):

🎯 **Quick Answer:**
• [Direct, friendly answer with relevant emoji]
• [Additional key point with emoji if needed]

📋 **Key Details:**
• [Important detail with emoji] 
• [Another important point with emoji]
• [Additional helpful information with emoji]

💡 **Helpful Insights:**
• [Useful insight or context with emoji]
• [Additional valuable information with emoji]

✨ **Summary:**
• [Main takeaway with emoji]
• [Encouraging closing thought with emoji]

IMPORTANT: Never deviate from bullet point format. Always be warm, supportive, and use emojis throughout. Keep language simple and friendly."""

    # Create prompt template
    CUSTOM_PROMPT = PromptTemplate(
        template=template, 
        input_variables=['context', 'question']
    )

    # Optimized LLM with settings for comprehensive, structured responses  
    llm = Ollama(
        model=config.AI_MODEL,
        temperature=config.AI_TEMPERATURE,  # Low temperature for consistent responses
        num_ctx=8192,     # Increased context window for better understanding
        num_predict=1024,  # Allow longer responses for comprehensive answers
        top_k=10,          # More focused sampling
        top_p=0.8,        # Balanced creativity and focus
        repeat_penalty=1.2, # Prevent repetition
        num_thread=config.NUM_THREADS
    )

    # Enhanced retriever for comprehensive results
    optimized_retriever = vector_store.as_retriever(
        search_type=config.SEARCH_TYPE,  # Maximum Marginal Relevance for diverse results
        search_kwargs={
            "k": 4,           # Get more relevant chunks for comprehensive answers
            "fetch_k": 15,    # Consider more candidates for better context
            "lambda_mult": 0.5  # Balance between relevance and diversity
        }
    )

    # Create a simple chain without memory to avoid interference
    from langchain.chains import RetrievalQA
    
    conversation_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # Stuff all retrieved docs into prompt
        retriever=optimized_retriever,
        chain_type_kwargs={"prompt": CUSTOM_PROMPT},
        return_source_documents=True
    )

    return conversation_chain

def simulate_typing_effect(text, container):
    """
    Simulate typing effect by gradually revealing text
    """
    import time
    words = text.split()
    displayed_text = ""
    
    for i, word in enumerate(words):
        displayed_text += word + " "
        container.markdown(displayed_text + "▌")
        if i % 5 == 0:  # Update every 5 words to balance smoothness and performance
            time.sleep(0.1)
    
    # Final display without cursor
    container.markdown(text)

def show_thinking_process(container, steps, total_steps=5):
    """
    Show AI thinking process with animated steps
    """
    thinking_steps = [
        "🧠 Understanding your question...",
        "📚 Searching through document...",
        "🔍 Finding relevant information...",
        "💭 Analyzing context...",
        "✨ Crafting response..."
    ]
    
    progress_bar = container.progress(0)
    status_container = container.empty()
    
    for i, step in enumerate(thinking_steps[:total_steps]):
        if i < len(steps):
            status_container.markdown(f"<div style='text-align: center; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 10px; margin: 5px 0;'>{step}</div>", unsafe_allow_html=True)
            progress_bar.progress((i + 1) / total_steps)
            time.sleep(0.8)  # Simulate thinking time
    
    return progress_bar, status_container

def generate_chat_title(first_message: str) -> str:
    """
    Generate a smart chat title based on the first message
    """
    # Extract key words and create a meaningful title
    words = first_message.lower().split()
    
    # Remove common words
    stop_words = {'what', 'is', 'the', 'how', 'can', 'you', 'tell', 'me', 'about', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    important_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    if len(important_words) >= 2:
        title = ' '.join(important_words[:3]).title()
    elif len(important_words) == 1:
        title = important_words[0].title() + " Discussion"
    else:
        title = f"Chat {datetime.now().strftime('%m/%d %H:%M')}"
    
    return title[:50]  # Limit title length

def get_optimized_embeddings():
    """
    Get optimized embeddings model for consistent performance
    """
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={
            'device': 'cpu',
            'trust_remote_code': False
        },
        encode_kwargs={
            'normalize_embeddings': True,
            'batch_size': config.BATCH_SIZE
        }
    )