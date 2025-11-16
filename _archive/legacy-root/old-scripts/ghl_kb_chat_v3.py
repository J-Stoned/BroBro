#!/usr/bin/env python3
"""
GHL WHIZ Knowledge Base Chat - Desktop App v3 (Elite Edition)
Features: Inline citations, smooth scrolling, Inter font, Bro Bro assistant
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
        self.conversation_history = []
        self.current_citations = {}  # Store citations for click events
        self.citation_windows = []  # Track open citation windows
        
        self.load_fonts()
        self.setup_styles()
        self.setup_ui()
        self.root.after(100, self.initialize_connection)
    
    def load_fonts(self):
        available_fonts = list(tkfont.families())
        if "Inter" in available_fonts:
            self.main_font = "Inter"
        elif "Segoe UI" in available_fonts:
            self.main_font = "Segoe UI"
        else:
            self.main_font = "Arial"
        self.mono_font = "Consolas" if "Consolas" in available_fonts else "Courier"
    
    def setup_styles(self):
        self.colors = {
            'bg': '#0f0f0f',
            'chat_bg': '#1a1a1a',
            'input_bg': '#1f2937',
            'input_border': '#374151',
            'text': '#e5e5e5',
            'user_name': '#60a5fa',
            'user_text': '#93c5fd',
            'assistant_name': '#4ade80',
            'system': '#fbbf24',
            'error': '#f87171',
            'citation': '#818cf8',
            'muted': '#6b7280',
            'button': '#3b82f6',
            'button_hover': '#2563eb',
        }
    
    def setup_ui(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=20, pady=15)
        header_frame.grid(row=0, column=0, sticky='ew')
        
        title_label = tk.Label(
            header_frame,
            text="GHL WHIZ Knowledge Base",
            font=(self.main_font, 20, 'bold'),
            bg=self.colors['bg'],
            fg='#ffffff'
        )
        title_label.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            header_frame,
            text="",
            font=(self.main_font, 11),
            bg=self.colors['bg'],
            fg=self.colors['muted']
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # Chat display with smooth scrolling
        chat_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=20)
        chat_frame.grid(row=1, column=0, sticky='nsew')
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)
        
        self.chat_display = tk.Text(
            chat_frame,
            wrap=tk.WORD,
            font=(self.main_font, 14),
            bg=self.colors['chat_bg'],
            fg=self.colors['text'],
            insertbackground='white',
            selectbackground='#404040',
            relief=tk.FLAT,
            padx=25,
            pady=20,
            spacing1=4,
            spacing2=2,
            spacing3=8,
            cursor='arrow',
            yscrollincrement=3  # Smooth scrolling
        )
        
        # Scrollbar
        scrollbar = tk.Scrollbar(chat_frame, command=self.chat_display.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.chat_display.configure(yscrollcommand=scrollbar.set)
        self.chat_display.grid(row=0, column=0, sticky='nsew')
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure text tags
        self.chat_display.tag_configure('user_name', foreground=self.colors['user_name'], font=(self.main_font, 14, 'bold'))
        self.chat_display.tag_configure('user_text', foreground=self.colors['user_text'], font=(self.main_font, 14), lmargin1=25, lmargin2=25)
        self.chat_display.tag_configure('assistant_name', foreground=self.colors['assistant_name'], font=(self.main_font, 14, 'bold'))
        self.chat_display.tag_configure('assistant_text', foreground=self.colors['text'], font=(self.main_font, 14), lmargin1=25, lmargin2=25, spacing1=6, spacing3=10)
        self.chat_display.tag_configure('system', foreground=self.colors['system'], font=(self.main_font, 12, 'italic'))
        self.chat_display.tag_configure('error', foreground=self.colors['error'], font=(self.main_font, 13))
        self.chat_display.tag_configure('citation', foreground=self.colors['citation'], font=(self.main_font, 12, 'bold'), underline=False)
        self.chat_display.tag_configure('timestamp', foreground=self.colors['muted'], font=(self.main_font, 10))
        
        # Bind citation clicks
        self.chat_display.tag_bind('citation', '<Button-1>', self.on_citation_click)
        self.chat_display.tag_bind('citation', '<Enter>', lambda e: self.chat_display.config(cursor='hand2'))
        self.chat_display.tag_bind('citation', '<Leave>', lambda e: self.chat_display.config(cursor='arrow'))
        
        # Input area
        input_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=20, pady=15)
        input_frame.grid(row=2, column=0, sticky='ew')
        
        input_container = tk.Frame(input_frame, bg=self.colors['input_border'], padx=2, pady=2)
        input_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        
        self.input_text = tk.Text(
            input_container,
            height=3,
            font=(self.main_font, 14),
            bg=self.colors['input_bg'],
            fg='#ffffff',
            insertbackground='white',
            relief=tk.FLAT,
            padx=18,
            pady=14
        )
        self.input_text.pack(fill=tk.X, expand=True)
        
        # Placeholder text
        self.placeholder_text = "Type message here..."
        self.input_text.insert("1.0", self.placeholder_text)
        self.input_text.config(fg=self.colors['muted'])
        self.placeholder_active = True
        
        self.input_text.bind('<FocusIn>', self.on_input_focus_in)
        self.input_text.bind('<FocusOut>', self.on_input_focus_out)
        self.input_text.bind('<Return>', self.handle_enter)
        self.input_text.bind('<Shift-Return>', lambda e: None)
        
        # Buttons
        button_frame = tk.Frame(input_frame, bg=self.colors['bg'])
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.send_button = tk.Button(
            button_frame,
            text="Send",
            command=self.send_message,
            font=(self.main_font, 13, 'bold'),
            bg=self.colors['button'],
            fg='white',
            activebackground=self.colors['button_hover'],
            activeforeground='white',
            relief=tk.FLAT,
            padx=25,
            pady=12,
            cursor='hand2'
        )
        self.send_button.pack(fill=tk.X, pady=(0, 8))
        
        self.clear_button = tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_chat,
            font=(self.main_font, 12),
            bg=self.colors['input_border'],
            fg='white',
            activebackground='#4b5563',
            activeforeground='white',
            relief=tk.FLAT,
            padx=25,
            pady=10,
            cursor='hand2'
        )
        self.clear_button.pack(fill=tk.X)
        
        # Quick queries
        quick_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=20, pady=12)
        quick_frame.grid(row=3, column=0, sticky='ew')
        
        quick_queries = [
            ("Email Deliverability", "How do I configure SPF, DKIM, and DMARC for optimal email deliverability in GHL?"),
            ("Workflow Triggers", "What are the best practices for setting up workflow triggers with conditional branching?"),
            ("Tissue Culture Media", "What are the optimal MS media formulations and growth regulator ratios for cannabis micropropagation?"),
            ("Offer Architecture", "How do I structure an irresistible offer using the value equation framework?"),
        ]
        
        for label, query in quick_queries:
            btn = tk.Button(
                quick_frame,
                text=label,
                command=lambda q=query: self.quick_query(q),
                font=(self.main_font, 11),
                bg=self.colors['input_bg'],
                fg='#d1d5db',
                activebackground=self.colors['input_border'],
                activeforeground='white',
                relief=tk.FLAT,
                padx=14,
                pady=8,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=4)
    
    def on_input_focus_in(self, event):
        if self.placeholder_active:
            self.input_text.delete("1.0", tk.END)
            self.input_text.config(fg='#ffffff')
            self.placeholder_active = False
    
    def on_input_focus_out(self, event):
        if not self.input_text.get("1.0", tk.END).strip():
            self.input_text.insert("1.0", self.placeholder_text)
            self.input_text.config(fg=self.colors['muted'])
            self.placeholder_active = True
    
    def handle_enter(self, event):
        if not event.state & 0x1:  # Not Shift+Enter
            self.send_message()
            return 'break'
        return None
    
    def on_citation_click(self, event):
        # Get the citation number from the clicked text
        index = self.chat_display.index(f"@{event.x},{event.y}")
        
        # Get all tags at this position
        tags = self.chat_display.tag_names(index)
        
        for tag in tags:
            if tag.startswith('cite_'):
                cite_num = tag.replace('cite_', '')
                if cite_num in self.current_citations:
                    self.show_citation_popup(event, cite_num, self.current_citations[cite_num])
                break
    
    def show_citation_popup(self, event, num, source):
        # Close any existing popups
        for win in self.citation_windows:
            try:
                win.destroy()
            except:
                pass
        self.citation_windows.clear()
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.configure(bg='#374151')
        
        # Position near click
        x = self.root.winfo_rootx() + event.x + 50
        y = self.root.winfo_rooty() + event.y + 100
        popup.geometry(f"+{x}+{y}")
        
        # Content frame
        frame = tk.Frame(popup, bg='#1f2937', padx=15, pady=12)
        frame.pack(padx=2, pady=2)
        
        header = tk.Label(
            frame,
            text=f"Source [{num}]",
            font=(self.main_font, 11, 'bold'),
            bg='#1f2937',
            fg=self.colors['citation']
        )
        header.pack(anchor='w')
        
        source_label = tk.Label(
            frame,
            text=source,
            font=(self.main_font, 12),
            bg='#1f2937',
            fg='#e5e5e5',
            wraplength=400,
            justify='left'
        )
        source_label.pack(anchor='w', pady=(5, 0))
        
        # Close on click outside
        def close_popup(e=None):
            popup.destroy()
            self.citation_windows.remove(popup)
        
        popup.bind('<Escape>', close_popup)
        self.root.bind('<Button-1>', lambda e: close_popup() if popup.winfo_exists() else None, add='+')
        
        self.citation_windows.append(popup)
        
        # Auto-close after 5 seconds
        popup.after(5000, close_popup)
    
    def initialize_connection(self):
        global genai, types
        
        # Show loading sequence
        self.update_status("Initializing...", '#fbbf24')
        self.root.update()
        
        api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
        if not api_key:
            self.update_status("❌ No API Key", '#f87171')
            self.add_error_message("No API key found. Set GOOGLE_API_KEY environment variable.")
            return
        
        self.update_status("Loading SDK...", '#fbbf24')
        self.root.update()
        
        try:
            from google import genai as g
            from google.genai import types as t
            genai = g
            types = t
            self.client = genai.Client()
        except ImportError:
            self.update_status("❌ Missing SDK", '#f87171')
            self.add_error_message("google-genai not installed. Run: pip install google-genai")
            return
        except Exception as e:
            self.update_status("❌ Init Failed", '#f87171')
            self.add_error_message(f"Failed to initialize: {e}")
            return
        
        self.update_status("Connecting to store...", '#fbbf24')
        self.root.update()
        
        store_file = r"C:\Users\justi\BroBro\GOOGLE_FILE_SEARCH_STORE.txt"
        if os.path.exists(store_file):
            with open(store_file, 'r') as f:
                for line in f:
                    if line.startswith('Store ID:'):
                        self.store_id = line.split(':', 1)[1].strip()
                        break
        
        if not self.store_id:
            self.update_status("❌ No Store ID", '#f87171')
            self.add_error_message(f"Store ID not found in {store_file}")
            return
        
        # Success - show briefly then fade
        self.update_status("✓ Connected", '#4ade80')
        self.root.update()
        
        # Fade out status after 2 seconds
        self.root.after(2000, lambda: self.update_status("", self.colors['muted']))
    
    def update_status(self, text, color):
        self.status_label.config(text=text, fg=color)
    
    def add_system_message(self, text):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{text}\n", 'system')
        self.chat_display.config(state=tk.DISABLED)
        self.smooth_scroll_to_end()
    
    def add_error_message(self, text):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"⚠ {text}\n\n", 'error')
        self.chat_display.config(state=tk.DISABLED)
        self.smooth_scroll_to_end()
    
    def add_user_message(self, text):
        self.chat_display.config(state=tk.NORMAL)
        
        # Get timestamp for hover
        timestamp = datetime.now().strftime("%H:%M")
        
        # Create unique tag for this message's timestamp
        msg_id = f"msg_{datetime.now().timestamp()}"
        
        self.chat_display.insert(tk.END, f"\nst0ne", 'user_name')
        
        # Add timestamp with hover behavior
        ts_tag = f"ts_{msg_id}"
        self.chat_display.tag_configure(ts_tag, foreground=self.colors['muted'], font=(self.main_font, 10))
        self.chat_display.insert(tk.END, f"  {timestamp}", ts_tag)
        
        # Initially hide timestamp
        self.chat_display.tag_configure(ts_tag, foreground=self.colors['chat_bg'])
        
        # Hover to show
        self.chat_display.tag_bind(ts_tag, '<Enter>', lambda e, t=ts_tag: self.chat_display.tag_configure(t, foreground=self.colors['muted']))
        self.chat_display.tag_bind(ts_tag, '<Leave>', lambda e, t=ts_tag: self.chat_display.tag_configure(t, foreground=self.colors['chat_bg']))
        
        self.chat_display.insert(tk.END, f"\n{text}\n", 'user_text')
        self.chat_display.config(state=tk.DISABLED)
        self.smooth_scroll_to_end()
    
    def add_assistant_message(self, text, citations=None):
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M")
        msg_id = f"msg_{datetime.now().timestamp()}"
        
        self.chat_display.insert(tk.END, f"\nBro Bro", 'assistant_name')
        
        # Timestamp with hover
        ts_tag = f"ts_{msg_id}"
        self.chat_display.tag_configure(ts_tag, foreground=self.colors['muted'], font=(self.main_font, 10))
        self.chat_display.insert(tk.END, f"  {timestamp}", ts_tag)
        self.chat_display.tag_configure(ts_tag, foreground=self.colors['chat_bg'])
        self.chat_display.tag_bind(ts_tag, '<Enter>', lambda e, t=ts_tag: self.chat_display.tag_configure(t, foreground=self.colors['muted']))
        self.chat_display.tag_bind(ts_tag, '<Leave>', lambda e, t=ts_tag: self.chat_display.tag_configure(t, foreground=self.colors['chat_bg']))
        
        self.chat_display.insert(tk.END, "\n")
        
        # Store citations for this response
        if citations:
            for i, cite in enumerate(citations, 1):
                self.current_citations[str(i)] = cite.get('source', 'Unknown source')
        
        # Format and insert response with clickable citations
        formatted_text = self.format_response(text)
        self.insert_text_with_citations(formatted_text)
        
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.config(state=tk.DISABLED)
        self.smooth_scroll_to_end()
    
    def insert_text_with_citations(self, text):
        # Find citation patterns like [1], [2], etc.
        pattern = r'\[(\d+)\]'
        last_end = 0
        
        for match in re.finditer(pattern, text):
            # Insert text before citation
            before_text = text[last_end:match.start()]
            self.chat_display.insert(tk.END, before_text, 'assistant_text')
            
            # Insert clickable citation
            cite_num = match.group(1)
            cite_tag = f"cite_{cite_num}"
            
            # Configure unique tag for this citation number
            self.chat_display.tag_configure(cite_tag, foreground=self.colors['citation'], font=(self.main_font, 12, 'bold'))
            self.chat_display.tag_bind(cite_tag, '<Button-1>', self.on_citation_click)
            self.chat_display.tag_bind(cite_tag, '<Enter>', lambda e: self.chat_display.config(cursor='hand2'))
            self.chat_display.tag_bind(cite_tag, '<Leave>', lambda e: self.chat_display.config(cursor='arrow'))
            
            self.chat_display.insert(tk.END, f"[{cite_num}]", cite_tag)
            
            last_end = match.end()
        
        # Insert remaining text
        if last_end < len(text):
            self.chat_display.insert(tk.END, text[last_end:], 'assistant_text')
    
    def format_response(self, text):
        # Clean up markdown formatting
        # Remove bold markers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        
        # Remove italic markers (but keep single * for lists)
        text = re.sub(r'(?<!\*)\*(?!\*)([^*]+)(?<!\*)\*(?!\*)', r'\1', text)
        
        # Remove header markers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Format paragraphs with indentation
        paragraphs = text.split('\n\n')
        formatted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para:
                # Check if it's a list item
                if para.startswith('- ') or para.startswith('* ') or re.match(r'^\d+\.', para):
                    # Keep list formatting but indent
                    lines = para.split('\n')
                    indented_lines = ['    ' + line for line in lines]
                    formatted_paragraphs.append('\n'.join(indented_lines))
                elif len(para) > 80:
                    # Wrap long paragraphs
                    wrapped = textwrap.fill(para, width=85, initial_indent='    ', subsequent_indent='    ')
                    formatted_paragraphs.append(wrapped)
                else:
                    # Short paragraphs
                    formatted_paragraphs.append('    ' + para)
        
        return '\n\n'.join(formatted_paragraphs)
    
    def smooth_scroll_to_end(self):
        self.chat_display.see(tk.END)
        self.chat_display.update_idletasks()
    
    def send_message(self):
        if not self.client or not self.store_id:
            messagebox.showerror("Not Connected", "Not connected to knowledge base.")
            return
        
        if self.placeholder_active:
            return
        
        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input:
            return
        
        self.input_text.delete("1.0", tk.END)
        self.placeholder_active = False
        self.add_user_message(user_input)
        
        # Clear previous citations
        self.current_citations.clear()
        
        self.send_button.config(state=tk.DISABLED, bg='#6b7280')
        self.update_status("Thinking...", '#fbbf24')
        
        thread = threading.Thread(target=self.query_knowledge_base, args=(user_input,))
        thread.daemon = True
        thread.start()
    
    def get_system_prompt(self):
        return """You are Bro Bro, a highly technical expert assistant. Your knowledge comes exclusively from the indexed documents you search.

EXPERTISE DOMAINS:
- GoHighLevel (GHL): Workflow configuration, automation sequences, website/funnel builder, email deliverability (SPF/DKIM/DMARC), API integrations, webhooks, custom fields, pipeline logic
- Cannabis Tissue Culture: Micropropagation protocols, media formulations (MS/WPM/DKW), sterilization procedures, growth regulators (BAP/IBA/NAA), environmental controls, acclimatization
- Business Strategy: Offer architecture, funnel mechanics, persuasion frameworks, revenue modeling, lead nurturing, conversion psychology

RESPONSE BEHAVIOR:
- Base ALL answers on the retrieved document information
- If no relevant information is retrieved, clearly state: "I don't have information on this in the current knowledge base"
- Never fabricate or extrapolate beyond what the documents provide
- When multiple documents are retrieved, synthesize them into a cohesive answer
- Reference source documents naturally within context when relevant (e.g., "According to the GHL workflow documentation..." or "The tissue culture protocol specifies...")

SOURCE ATTRIBUTION:
- Use inline citation numbers [1], [2], [3] immediately after the relevant information
- Place the citation number directly after the fact or statement it supports
- Reuse the same number when referencing the same source multiple times
- Keep citations unobtrusive - they should support credibility without disrupting flow

RESPONSE FORMAT:
- Provide precise, technical explanations with specific parameters and values
- Write in clear prose paragraphs with natural flow
- Use bullet points or numbered lists ONLY when presenting:
  - Step-by-step procedures
  - Configuration parameters
  - Lists of specific values or settings
  - Comparison data
- Use tables for specifications, ratios, or comparative data when helpful
- NO excessive markdown styling (avoid bold for emphasis, avoid headers for every section)
- Keep formatting functional and readable, not decorative
- Deliver technical depth while maintaining clarity. Explain the WHY behind configurations, not just the WHAT. Complex concepts should be thorough AND understandable.

ENGAGEMENT:
- End EVERY response with a strategic follow-up question
- The question should push toward optimization, edge cases, or advanced implementation
- Frame naturally: "Have you considered..." or "What's your contingency if..." or "How does this integrate with..."

Deliver expert-level technical guidance. Precision matters."""
    
    def query_knowledge_base(self, question):
        try:
            # Build the request with system instruction
            system_instruction = self.get_system_prompt()
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=question,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=3000,
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
            
            # Extract citations from grounding metadata
            citations = []
            try:
                if hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                            metadata = candidate.grounding_metadata
                            
                            # Try grounding_chunks
                            if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
                                for chunk in metadata.grounding_chunks:
                                    source_name = 'Unknown source'
                                    
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
                                    
                                    citations.append({'source': source_name})
            except Exception as e:
                print(f"Citation extraction error: {e}")
            
            self.root.after(0, lambda: self.display_response(answer, citations))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.add_error_message(f"Error: {error_msg}"))
            self.root.after(0, self.reset_ui_state)
    
    def display_response(self, answer, citations):
        self.add_assistant_message(answer, citations)
        self.reset_ui_state()
    
    def reset_ui_state(self):
        self.update_status("", self.colors['muted'])
        self.send_button.config(state=tk.NORMAL, bg=self.colors['button'])
    
    def quick_query(self, query):
        if self.placeholder_active:
            self.input_text.delete("1.0", tk.END)
            self.placeholder_active = False
            self.input_text.config(fg='#ffffff')
        else:
            self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", query)
        self.send_message()
    
    def clear_chat(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.conversation_history = []
        self.current_citations.clear()


def main():
    # Load API key from .env if not in environment
    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        env_file = r"C:\Users\justi\BroBro\.env"
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('GOOGLE_API_KEY='):
                        key = line.split('=', 1)[1].strip()
                        os.environ['GOOGLE_API_KEY'] = key
                        break
                    elif line.startswith('GEMINI_API_KEY='):
                        key = line.split('=', 1)[1].strip()
                        os.environ['GEMINI_API_KEY'] = key
                        break
    
    root = tk.Tk()
    app = KnowledgeBaseChatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
