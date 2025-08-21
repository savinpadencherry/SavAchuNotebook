# 🤖 NoteBook AI - Your Intelligent Document Companion

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-000000?style=for-the-badge&logo=chainlink&logoColor=white)](https://langchain.com/)
[![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge)](https://ollama.ai/)

A beautiful, modern document chat application that lets you have intelligent conversations with your documents. Built with Streamlit, LangChain, and Ollama for completely local AI processing.

## ✨ Features

### 🎯 **Core Capabilities**
- **Multi-format Document Support**: PDF, Word (DOCX), and text files
- **Intelligent Chunking**: Smart text splitting preserving document structure
- **Advanced AI Responses**: Powered by Gemma 2B model via Ollama
- **Semantic Search**: Find relevant information using vector similarity
- **Persistent Storage**: SQLite database for chat history and documents

### 🎨 **Beautiful UI**
- **Cosmic Theme**: Animated starfield background with modern glassmorphism
- **Responsive Design**: Optimized for all screen sizes
- **Thinking Process**: Visual AI thinking indicators
- **Chat Management**: Create, manage, and delete conversations
- **Context Display**: See relevant document chunks for each response

### 🔒 **Privacy & Performance**
- **100% Local**: All processing happens on your machine
- **No API Keys**: No external API calls required
- **Optimized Performance**: Resource-efficient with minimal battery drain
- **Data Persistence**: Resume conversations without re-uploading documents

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- [Ollama](https://ollama.ai) installed and running

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "NoteBook AI"
   ```

2. **Run the setup script**
   ```bash
   ./start.sh
   ```

3. **Or install manually**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install Ollama and download model
   ollama pull gemma2:2b
   
   # Start the application
   streamlit run app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501`

## 📖 How to Use

### 1. **Create a New Chat**
- Click "✨ New Chat" in the sidebar
- Enter a descriptive title for your chat
- Click "Create Chat"

### 2. **Upload a Document**
- In the document upload panel, choose your file (PDF, DOCX, or TXT)
- Click "🚀 Process Document"
- Wait for the AI to process and create searchable chunks

### 3. **Start Chatting**
- Type your question in the chat input
- Watch the AI thinking process
- Get intelligent responses based on your document content

### 4. **Manage Conversations**
- View all your chats in the sidebar
- Click on any chat to resume the conversation
- Delete unwanted chats with the 🗑️ button

## 🏗️ Architecture

### **Components**
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    app.py       │  │    utils.py     │  │  database.py    │
│  (UI Layer)     │  │ (Processing)    │  │  (Storage)      │
│                 │  │                 │  │                 │
│ • Streamlit UI  │  │ • Text Extract  │  │ • SQLite DB     │
│ • Chat Interface│  │ • Chunking      │  │ • Chat Storage  │
│ • File Upload   │  │ • Vector Store  │  │ • Vector Store  │
│ • Chat Mgmt     │  │ • AI Chain      │  │ • Messages      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### **AI Pipeline**
1. **Document Processing**: Extract text from uploaded files
2. **Smart Chunking**: Split text preserving context and meaning
3. **Vectorization**: Convert chunks to numerical embeddings
4. **Storage**: Save in FAISS vector database
5. **Retrieval**: Find relevant chunks using similarity search
6. **Generation**: Generate responses using local Ollama model

## 🎨 Customization

### **Changing the AI Model**
Edit `utils.py` in the `get_conversation_chain` function:
```python
llm = Ollama(
    model='llama2',  # Change to your preferred model
    temperature=0.1,
    # ... other parameters
)
```

### **Adjusting Chunk Size**
Modify `get_text_chunks` function in `utils.py`:
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Increase for larger chunks
    chunk_overlap=100,  # Adjust overlap
    # ... other parameters
)
```

### **UI Themes**
Customize the CSS in `app.py` to change colors, animations, and styling.

## 🔧 Technical Details

### **Dependencies**
- **Streamlit**: Web application framework
- **LangChain**: AI application framework
- **FAISS**: Vector similarity search
- **Sentence Transformers**: Text embeddings
- **Ollama**: Local AI model runner
- **SQLite**: Local database storage

### **Performance Optimizations**
- **Efficient Chunking**: Preserves context while maintaining performance
- **Caching**: Database connections and embeddings cached
- **Batch Processing**: Optimized embedding generation
- **Memory Management**: Careful resource cleanup

### **File Support**
- **PDF**: Using `pypdf` for text extraction
- **Word**: Using `python-docx` for DOCX files
- **Text**: Native Python string handling

## 🛠️ Development

### **Project Structure**
```
NoteBook AI/
├── app.py              # Main Streamlit application
├── utils.py            # Document processing and AI utilities
├── database.py         # SQLite database operations
├── requirements.txt    # Python dependencies
├── start.sh           # Quick start script
├── README.md          # This file
└── notebook_ai.db     # SQLite database (created automatically)
```

### **Adding New Features**
1. **New Document Types**: Add processors in `utils.py`
2. **Different AI Models**: Modify the LLM configuration
3. **Enhanced UI**: Update the Streamlit interface in `app.py`
4. **Database Schema**: Extend `database.py` for new data types

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Troubleshooting

### **Common Issues**

**Ollama not found**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull gemma2:2b
```

**Model download fails**
```bash
# Try a different model
ollama pull llama2:7b
# Update utils.py to use the new model
```

**Database errors**
```bash
# Delete the database to reset
rm notebook_ai.db
# Restart the application
```

**Performance issues**
- Reduce chunk size in `utils.py`
- Use a smaller AI model
- Increase system RAM allocation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama** for local AI model serving
- **LangChain** for the AI application framework
- **Streamlit** for the beautiful web interface
- **Hugging Face** for the embedding models
- **FAISS** for efficient vector search

---

<div align="center">
  <p><strong>Built with ❤️ for intelligent document interaction</strong></p>
  <p>🌟 Star this repo if you find it helpful! 🌟</p>
</div>
