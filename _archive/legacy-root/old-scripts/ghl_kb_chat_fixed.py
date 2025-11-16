#!/usr/bin/env python3
"""
GHL WHIZ Knowledge Base Chat - FIXED VERSION
Major Fixes:
1. Conversation history maintained
2. System prompt enforces KB usage
3. Citations actually used
4. Better retrieval config
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, font as tkfont
import threading
import os
import textwrap
import re
from datetime import datetime

genai = None
types = None


class KnowledgeBaseChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GHL WHIZ Knowledge Base")
        self.root.geometry("1100x850")
        self.root.configure(bg='#0f0f0f')
        self.root.minsize(900, 700)
        
        self.client = None
        self.store_id = None
        self.conversation_history = []  # NOW ACTUALLY USED
        self.current_citations = {}
        self.citation_windows = []
        self.typing_indicator_id = None
        self.typing_dots = 0
        self.thinking_line_start = None
        
        self.load_fonts()
        self.setup_styles()
        self.setup_ui()
        self.root.after(100, self.initialize_connection)
