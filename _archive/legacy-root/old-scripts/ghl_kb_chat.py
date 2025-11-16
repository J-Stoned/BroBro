#!/usr/bin/env python3
"""
GHL WHIZ Knowledge Base Chat - Desktop App v2 (Fixed Layout)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font as tkfont
import threading
import os
import textwrap
from datetime import datetime

genai = None
types = None


class KnowledgeBaseChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GHL WHIZ Knowledge Base Chat")
        self.root.geometry("1000x800")
        self.root.configure(bg='#0f0f0f')
        self.root.minsize(800, 600)
        
        self.client = None
        self.store_id = None
        self.conversation_history = []
        
        self.load_fonts()
        self.setup_ui()
        self.root.after(100, self.initialize_connection)
    
    def load_fonts(self):
        available_fonts = list(tkfont.families())
        if "Open Sans" in available_fonts:
            self.agent_font = "Open Sans"
        elif "Segoe UI" in available_fonts:
            self.agent_font = "Segoe UI"
        else:
            self.agent_font = "Arial"
        self.mono_font = "Consolas" if "Consolas" in available_fonts else "Courier"
    
    def setup_ui(self):
        # Main container - use grid for better control
        self.root.grid_rowconfigure(1, weight=1)  # Chat area expands
        self.root.grid_columnconfigure(0, weight=1)
        
        # Header (row 0)
        header_frame = tk.Frame(self.root, bg='#0f0f0f', padx=15, pady=10)
        header_frame.grid(row=0, column=0, sticky='ew')
        
        title_label = tk.Label(
            header_frame,
            text="🧠 GHL WHIZ Knowledge Base Chat",
            font=(self.agent_font, 18, 'bold'),
            bg='#0f0f0f',
            fg='#ffffff'
        )
        title_label.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            header_frame,
            text="⏳ Connecting...",
            font=(self.agent_font, 10),
            bg='#0f0f0f',
            fg='#9ca3af'
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # Chat display (row 1) - this one expands
        chat_frame = tk.Frame(self.root, bg='#0f0f0f', padx=15)
        chat_frame.grid(row=1, column=0, sticky='nsew')
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=(self.agent_font, 13),
            bg='#1a1a1a',
            fg='#e5e5e5',
            insertbackground='white',
            selectbackground='#404040',
            relief=tk.FLAT,
            padx=20,
            pady=15,
            spacing1=5,
            spacing2=3,
            spacing3=10
        )
        self.chat_display.grid(row=0, column=0, sticky='nsew')
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure text tags
        self.chat_display.tag_configure('user_label', foreground='#60a5fa', font=(self.agent_font, 13, 'bold'))
        self.chat_display.tag_configure('user_text', foreground='#93c5fd', font=(self.agent_font, 13), lmargin1=20, lmargin2=20)
        self.chat_display.tag_configure('assistant_label', foreground='#4ade80', font=(self.agent_font, 13, 'bold'))
        self.chat_display.tag_configure('assistant_text', foreground='#e5e5e5', font=(self.agent_font, 13), lmargin1=30, lmargin2=30, spacing1=8, spacing3=12)
        self.chat_display.tag_configure('system', foreground='#fbbf24', font=(self.agent_font, 11, 'italic'))
        self.chat_display.tag_configure('error', foreground='#f87171', font=(self.agent_font, 12))
        self.chat_display.tag_configure('citation_header', foreground='#a78bfa', font=(self.agent_font, 12, 'bold'), spacing1=15)
        self.chat_display.tag_configure('citation_text', foreground='#9ca3af', font=(self.agent_font, 11), lmargin1=25, lmargin2=25)
        
        # Input area (row 2) - fixed at bottom
        input_frame = tk.Frame(self.root, bg='#0f0f0f', padx=15, pady=10)
        input_frame.grid(row=2, column=0, sticky='ew')
        
        # Input container with border
        input_container = tk.Frame(input_frame, bg='#374151', padx=2, pady=2)
        input_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.input_text = tk.Text(
            input_container,
            height=3,
            font=(self.agent_font, 13),
            bg='#1f2937',
            fg='#ffffff',
            insertbackground='white',
            relief=tk.FLAT,
            padx=15,
            pady=12
        )
        self.input_text.pack(fill=tk.X, expand=True)
        self.input_text.bind('<Return>', self.handle_enter)
        self.input_text.bind('<Shift-Return>', lambda e: None)
        
        # Buttons
        button_frame = tk.Frame(input_frame, bg='#0f0f0f')
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.send_button = tk.Button(
            button_frame,
            text="Send",
            command=self.send_message,
            font=(self.agent_font, 12, 'bold'),
            bg='#3b82f6',
            fg='white',
            activebackground='#2563eb',
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.send_button.pack(fill=tk.X, pady=(0, 8))
        
        self.clear_button = tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_chat,
            font=(self.agent_font, 11),
            bg='#374151',
            fg='white',
            activebackground='#4b5563',
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        )
        self.clear_button.pack(fill=tk.X)
        
        # Quick queries (row 3) - at very bottom
        quick_frame = tk.Frame(self.root, bg='#0f0f0f', padx=15, pady=10)
        quick_frame.grid(row=3, column=0, sticky='ew')
        
        quick_label = tk.Label(
            quick_frame,
            text="Quick queries:",
            font=(self.agent_font, 11),
            bg='#0f0f0f',
            fg='#9ca3af'
        )
        quick_label.pack(side=tk.LEFT, padx=(0, 10))
        
        quick_queries = [
            ("📧 Email Setup", "How do I set up email deliverability with DKIM and SPF in GHL?"),
            ("🔄 Lead Nurturing", "What's the best workflow for automated lead nurturing?"),
            ("🤖 AI Chatbot", "How do I configure an AI chatbot for lead qualification?"),
            ("🌱 Tissue Culture", "What are the sterilization protocols for cannabis tissue culture?"),
            ("💰 $100M Offers", "How does Alex Hormozi recommend structuring irresistible offers?"),
        ]
        
        for label, query in quick_queries:
            btn = tk.Button(
                quick_frame,
                text=label,
                command=lambda q=query: self.quick_query(q),
                font=(self.agent_font, 10),
                bg='#1f2937',
                fg='#d1d5db',
                activebackground='#374151',
                activeforeground='white',
                relief=tk.FLAT,
                padx=12,
                pady=6,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=3)
    
    def handle_enter(self, event):
        if not event.state & 0x1:
            self.send_message()
            return 'break'
        return None
    
    def initialize_connection(self):
        global genai, types
        
        self.add_system_message("Initializing connection to Google File Search...")
        
        api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
        if not api_key:
            self.add_error_message("❌ No API key found! Set GOOGLE_API_KEY environment variable.")
            self.status_label.config(text="❌ No API Key")
            return
        
        try:
            from google import genai as g
            from google.genai import types as t
            genai = g
            types = t
            self.client = genai.Client()
        except ImportError:
            self.add_error_message("❌ google-genai not installed. Run: pip install google-genai")
            self.status_label.config(text="❌ Missing SDK")
            return
        except Exception as e:
            self.add_error_message(f"❌ Failed to initialize client: {e}")
            self.status_label.config(text="❌ Init Failed")
            return
        
        store_file = r"C:\Users\justi\BroBro\GOOGLE_FILE_SEARCH_STORE.txt"
        if os.path.exists(store_file):
            with open(store_file, 'r') as f:
                for line in f:
                    if line.startswith('Store ID:'):
                        self.store_id = line.split(':', 1)[1].strip()
                        break
        
        if not self.store_id:
            self.add_error_message(f"❌ Store ID not found in {store_file}")
            self.status_label.config(text="❌ No Store ID")
            return
        
        self.status_label.config(text="✅ Connected", fg='#4ade80')
        self.add_system_message("✅ Connected to knowledge base!")
        self.add_system_message(f"Store: {self.store_id}")
        self.add_system_message("Ready to answer questions about GHL, business strategy, tissue culture, and more!")
        self.add_system_message("─" * 60)
    
    def add_system_message(self, text):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{text}\n", 'system')
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def add_error_message(self, text):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{text}\n", 'error')
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def add_user_message(self, text):
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.insert(tk.END, f"\n[{timestamp}] You:\n", 'user_label')
        self.chat_display.insert(tk.END, f"{text}\n", 'user_text')
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def add_assistant_message(self, text, citations=None):
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.insert(tk.END, f"\n[{timestamp}] Assistant:\n", 'assistant_label')
        
        formatted_text = self.format_response(text)
        self.chat_display.insert(tk.END, f"{formatted_text}\n", 'assistant_text')
        
        if citations and len(citations) > 0:
            self.chat_display.insert(tk.END, f"\n📚 Sources Referenced:\n", 'citation_header')
            for i, cite in enumerate(citations[:5], 1):
                source = cite.get('source', 'Unknown source')
                self.chat_display.insert(tk.END, f"  {i}. {source}\n", 'citation_text')
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def format_response(self, text):
        paragraphs = text.split('\n\n')
        formatted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para:
                if len(para) > 100 and not para.startswith('*') and not para.startswith('-'):
                    wrapped = textwrap.fill(para, width=90, initial_indent='    ', subsequent_indent='    ')
                    formatted_paragraphs.append(wrapped)
                else:
                    lines = para.split('\n')
                    indented_lines = ['    ' + line for line in lines]
                    formatted_paragraphs.append('\n'.join(indented_lines))
        
        return '\n\n'.join(formatted_paragraphs)
    
    def send_message(self):
        if not self.client or not self.store_id:
            messagebox.showerror("Not Connected", "Not connected to knowledge base.")
            return
        
        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input:
            return
        
        self.input_text.delete("1.0", tk.END)
        self.add_user_message(user_input)
        
        self.send_button.config(state=tk.DISABLED, bg='#6b7280')
        self.status_label.config(text="🔄 Thinking...", fg='#fbbf24')
        
        thread = threading.Thread(target=self.query_knowledge_base, args=(user_input,))
        thread.daemon = True
        thread.start()
    
    def query_knowledge_base(self, question):
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=question,
                config=types.GenerateContentConfig(
                    max_output_tokens=2048,
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[self.store_id]
                            )
                        )
                    ]
                )
            )
            
            answer = response.text if hasattr(response, 'text') else str(response)
            
            # Debug: Print response structure to console
            print("\n=== DEBUG: Response Structure ===")
            if hasattr(response, 'candidates') and response.candidates:
                for i, candidate in enumerate(response.candidates):
                    print(f"Candidate {i}: {type(candidate)}")
                    if hasattr(candidate, 'grounding_metadata'):
                        gm = candidate.grounding_metadata
                        print(f"  grounding_metadata: {type(gm)}")
                        if gm:
                            for attr in dir(gm):
                                if not attr.startswith('_'):
                                    val = getattr(gm, attr)
                                    if val and not callable(val):
                                        print(f"    {attr}: {type(val)} = {str(val)[:200]}")
            print("=== END DEBUG ===\n")
            
            citations = []
            try:
                if hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                            metadata = candidate.grounding_metadata
                            
                            # Try grounding_chunks first
                            if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
                                for chunk in metadata.grounding_chunks:
                                    source_name = 'Unknown'
                                    # Try different attributes for source name
                                    if hasattr(chunk, 'retrieved_context'):
                                        ctx = chunk.retrieved_context
                                        if hasattr(ctx, 'uri'):
                                            source_name = ctx.uri.split('/')[-1]
                                        elif hasattr(ctx, 'title'):
                                            source_name = ctx.title
                                    elif hasattr(chunk, 'web'):
                                        if hasattr(chunk.web, 'uri'):
                                            source_name = chunk.web.uri.split('/')[-1]
                                        elif hasattr(chunk.web, 'title'):
                                            source_name = chunk.web.title
                                    elif hasattr(chunk, 'source'):
                                        source_name = str(chunk.source)
                                    
                                    citations.append({
                                        'source': source_name,
                                        'content': getattr(chunk, 'content', '')[:100] if hasattr(chunk, 'content') else ''
                                    })
                            
                            # Also try grounding_supports for additional source info
                            if hasattr(metadata, 'grounding_supports') and metadata.grounding_supports:
                                for support in metadata.grounding_supports:
                                    if hasattr(support, 'grounding_chunk_indices'):
                                        pass  # Already captured in grounding_chunks
                            
                            # Try retrieval_metadata
                            if hasattr(metadata, 'retrieval_metadata') and metadata.retrieval_metadata:
                                ret_meta = metadata.retrieval_metadata
                                if hasattr(ret_meta, 'google_search_dynamic_retrieval_score'):
                                    pass  # This is just a score, not useful for citations
            except Exception as e:
                # Log the error but don't crash
                print(f"Citation extraction error: {e}")
                pass
            
            self.root.after(0, lambda: self.display_response(answer, citations))
            
        except Exception as e:
            self.root.after(0, lambda: self.add_error_message(f"❌ Error: {str(e)}"))
            self.root.after(0, self.reset_ui_state)
    
    def display_response(self, answer, citations):
        self.add_assistant_message(answer, citations)
        self.reset_ui_state()
    
    def reset_ui_state(self):
        self.status_label.config(text="✅ Connected", fg='#4ade80')
        self.send_button.config(state=tk.NORMAL, bg='#3b82f6')
    
    def quick_query(self, query):
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", query)
        self.send_message()
    
    def clear_chat(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.conversation_history = []
        self.add_system_message("Chat cleared. Ready for new questions!")


def main():
    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        env_file = r"C:\Users\justi\BroBro\.env"
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('GOOGLE_API_KEY='):
                        key = line.split('=', 1)[1].strip()
                        os.environ['GOOGLE_API_KEY'] = key
                        break
    
    root = tk.Tk()
    app = KnowledgeBaseChatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
