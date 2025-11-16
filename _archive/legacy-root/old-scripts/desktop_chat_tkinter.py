"""
GHL WHIZ - Desktop Chat Interface (CustomTkinter)
Uses Google File Search API with 858+ indexed documents
"""

import customtkinter as ctk
import requests
import json
import re
import threading
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GHLWizDesktopChat(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("GHL WHIZ - Desktop Chat")
        self.geometry("1100x800")
        self.configure(fg_color="#1a1a2e")
        
        # Google File Search Configuration
        self.api_key = self.load_api_key()
        self.store_id = "ghlwizcompletekb-9dultbq96h00"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        # Chat history
        self.chat_history = []
        
        self.setup_ui()
        
    def load_api_key(self):
        """Load API key from config file"""
        try:
            with open("C:/Users/justi/BroBro/google_file_search_config.json", "r") as f:
                config = json.load(f)
                return config.get("api_key", "")
        except:
            return ""
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main container with gradient-like background
        main_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Header section
        header_frame = ctk.CTkFrame(main_frame, fg_color="#0f3460", height=100)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header_frame,
            text="🚀 GHL WHIZ Knowledge Base",
            font=("Segoe UI", 28, "bold"),
            text_color="#e94560"
        )
        title.pack(pady=(20, 5))
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="858 Documents | GoHighLevel • Business Strategy • Tissue Culture Research",
            font=("Segoe UI", 14),
            text_color="#a0a0a0"
        )
        subtitle.pack(pady=(0, 10))
        
        # Chat display area with better styling
        chat_container = ctk.CTkFrame(main_frame, fg_color="#1a1a2e")
        chat_container.pack(pady=15, padx=25, fill="both", expand=True)
        
        self.chat_frame = ctk.CTkScrollableFrame(
            chat_container,
            fg_color="#0d1b2a",
            corner_radius=15,
            scrollbar_button_color="#e94560",
            scrollbar_button_hover_color="#ff6b8a"
        )
        self.chat_frame.pack(fill="both", expand=True)
        
        # Quick query buttons
        quick_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        quick_frame.pack(pady=10, padx=25, fill="x")
        
        quick_label = ctk.CTkLabel(
            quick_frame,
            text="Quick Queries:",
            font=("Segoe UI", 12, "bold"),
            text_color="#e94560"
        )
        quick_label.pack(side="left", padx=(0, 15))
        
        quick_queries = [
            ("Email Deliverability", "Best practices for email deliverability in GoHighLevel"),
            ("Workflow Triggers", "How to set up workflow triggers and automation"),
            ("Tissue Culture", "Cannabis tissue culture protocols and contamination control")
        ]
        
        for label, query in quick_queries:
            btn = ctk.CTkButton(
                quick_frame,
                text=label,
                command=lambda q=query: self.quick_query(q),
                font=("Segoe UI", 11, "bold"),
                fg_color="#533483",
                hover_color="#7952b3",
                corner_radius=20,
                height=32
            )
            btn.pack(side="left", padx=5)
        
        # Input frame with modern styling
        input_container = ctk.CTkFrame(main_frame, fg_color="#0f3460", corner_radius=15)
        input_container.pack(pady=15, padx=25, fill="x")
        
        input_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        input_frame.pack(pady=15, padx=15, fill="x")
        
        # Message input - larger font
        self.message_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ask anything about your knowledge base...",
            height=50,
            font=("Segoe UI", 16),
            corner_radius=25,
            fg_color="#1a1a2e",
            border_color="#e94560",
            border_width=2
        )
        self.message_input.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.message_input.bind("<Return>", lambda e: self.send_message())
