"""
Backward compatibility layer for existing app.py
This file maintains compatibility with the old app.py while using the new modular architecture.
"""

# Import and run the new modular application
from main import main

if __name__ == "__main__":
    main()