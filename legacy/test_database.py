#!/usr/bin/env python3
"""
Test script for NoteBook AI database functionality
"""

import sys
import os
from database import ChatDatabase

def test_database():
    """Test basic database operations"""
    print("🧪 Testing NoteBook AI Database...")
    
    # Initialize database
    db = ChatDatabase("test_db.db")
    print("✅ Database initialized")
    
    # Test creating a chat
    chat_id = db.create_chat("Test Chat", "test.pdf", "pdf", 1024)
    print(f"✅ Created chat with ID: {chat_id}")
    
    # Test getting chat info
    chat_info = db.get_chat_info(chat_id)
    print(f"✅ Retrieved chat info: {chat_info['title']}")
    
    # Test adding messages
    db.add_message(chat_id, "user", "Hello, this is a test message")
    db.add_message(chat_id, "assistant", "Hello! I'm ready to help with your document.")
    print("✅ Added test messages")
    
    # Test retrieving messages
    messages = db.get_chat_messages(chat_id)
    print(f"✅ Retrieved {len(messages)} messages")
    
    # Test getting all chats
    all_chats = db.get_all_chats()
    print(f"✅ Retrieved {len(all_chats)} chats")
    
    # Clean up test database
    os.remove("test_db.db")
    print("✅ Cleanup completed")
    
    print("\n🎉 All database tests passed!")

if __name__ == "__main__":
    try:
        test_database()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
