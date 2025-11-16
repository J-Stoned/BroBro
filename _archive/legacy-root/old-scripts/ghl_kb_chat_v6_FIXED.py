#!/usr/bin/env python3
"""
GHL WHIZ Knowledge Base Chat - Desktop App v6 (FIXED RAG)
CRITICAL FIXES:
1. Conversation history maintained across messages
2. System prompt ENFORCES knowledge base usage
3. Citations properly displayed with sources
4. Temperature lowered for factual responses
5. Better response formatting without excessive bullets
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, font as tkfont
import threading
import os
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
        self.conversation_history = []  # CRITICAL: Now actually used
        self.current_citations = {}
        self.citation_windows = []
        self.typing_indicator_id = None
        self.typing_dots = 0
        self.thinking_line_start = None
        
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
            'thinking': '#ff9500',
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
        
        # Chat display
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
            cursor='arrow'
        )
        
        scrollbar = tk.Scrollbar(chat_frame, command=self.chat_display.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.chat_display.configure(yscrollcommand=scrollbar.set)
        self.chat_display.grid(row=0, column=0, sticky='nsew')
        self.chat_display.config(state=tk.DISABLED)
        
        # Text tags
        self.chat_display.tag_configure('user_name', foreground=self.colors['user_name'], 
                                         font=(self.main_font, 14, 'bold'))
        self.chat_display.tag_configure('user_text', foreground=self.colors['user_text'], 
                                         font=(self.main_font, 14), lmargin1=25, lmargin2=25)
        self.chat_display.tag_configure('assistant_name', foreground=self.colors['assistant_name'], 
                                         font=(self.main_font, 14, 'bold'))
        self.chat_display.tag_configure('assistant_text', foreground=self.colors['text'], 
                                         font=(self.main_font, 14), lmargin1=25, lmargin2=25, 
                                         spacing1=6, spacing3=10)
        self.chat_display.tag_configure('system', foreground=self.colors['system'], 
                                         font=(self.main_font, 12, 'italic'))
        self.chat_display.tag_configure('error', foreground=self.colors['error'], 
                                         font=(self.main_font, 13))
        self.chat_display.tag_configure('citation', foreground=self.colors['citation'], 
                                         font=(self.main_font, 12, 'bold'), underline=False)
        self.chat_display.tag_configure('timestamp', foreground=self.colors['muted'], 
                                         font=(self.main_font, 10))
        self.chat_display.tag_configure('thinking', foreground=self.colors['thinking'], 
                                         font=(self.main_font, 14, 'italic'))
        self.chat_display.tag_configure('source_info', foreground='#a78bfa', 
                                         font=(self.main_font, 11, 'italic'))
        
        self.chat_display.tag_bind('citation', '<Button-1>', self.on_citation_click)
        self.chat_display.tag_bind('citation', '<Enter>', lambda e: self.chat_display.config(cursor='hand2'))
        self.chat_display.tag_bind('citation', '<Leave>', lambda e: self.chat_display.config(cursor='arrow'))
        
        # Input frame
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
        
        self.placeholder_text = "Type message here..."
        self.input_text.insert("1.0", self.placeholder_text)
        self.input_text.config(fg=self.colors['muted'])
        self.placeholder_active = True
        
        self.input_text.bind('<FocusIn>', self.on_input_focus_in)
        self.input_text.bind('<FocusOut>', self.on_input_focus_out)
        self.input_text.bind('<Return>', self.handle_enter)
        self.input_text.bind('<Shift-Return>', lambda e: None)
        
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
            ("Email Setup", "What are the exact steps to configure SPF, DKIM, and DMARC in GoHighLevel?"),
            ("Workflow Help", "How do I create a workflow with conditional branching in GHL?"),
            ("Tissue Culture", "What is the optimal MS media formulation for cannabis micropropagation?"),
            ("Value Equation", "Explain the value equation framework from $100M Offers"),
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
        if not event.state & 0x1:
            self.send_message()
            return 'break'
        return None
    
    def on_citation_click(self, event):
        index = self.chat_display.index(f"@{event.x},{event.y}")
        tags = self.chat_display.tag_names(index)
        for tag in tags:
            if tag.startswith('cite_'):
                cite_num = tag.replace('cite_', '')
                if cite_num in self.current_citations:
                    self.show_citation_popup(event, cite_num, self.current_citations[cite_num])
                break
    
    def show_citation_popup(self, event, num, source):
        for win in self.citation_windows:
            try:
                win.destroy()
            except:
                pass
        self.citation_windows.clear()
        
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.configure(bg='#374151')
        
        x = self.root.winfo_rootx() + event.x + 50
        y = self.root.winfo_rooty() + event.y + 100
        popup.geometry(f"+{x}+{y}")
        
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
        
        def close_popup(e=None):
            try:
                popup.destroy()
                if popup in self.citation_windows:
                    self.citation_windows.remove(popup)
            except:
                pass
        
        popup.bind('<Escape>', close_popup)
        self.root.bind('<Button-1>', lambda e: close_popup() if popup.winfo_exists() else None, add='+')
        self.citation_windows.append(popup)
        popup.after(5000, close_popup)
    
    def initialize_connection(self):
        global genai, types
        
        self.update_status("Initializing...", '#fbbf24')
        self.root.update()
        
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
        
        self.update_status("✓ Connected", '#4ade80')
        self.add_system_message(f"Connected to knowledge base with {self.get_doc_count()} documents.")
        self.root.update()
    
    def get_doc_count(self):
        """Get approximate document count from store info"""
        store_file = r"C:\Users\justi\BroBro\GOOGLE_FILE_SEARCH_STORE.txt"
        if os.path.exists(store_file):
            with open(store_file, 'r') as f:
                for line in f:
                    if 'Total Documents Uploaded:' in line:
                        try:
                            return int(line.split(':')[1].strip())
                        except:
                            pass
        return 858  # Default from your upload
    
    def update_status(self, text, color):
        self.status_label.config(text=text, fg=color)
    
    def add_system_message(self, text):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"⚙ {text}\n", 'system')
        self.chat_display.config(state=tk.DISABLED)
        self.smooth_scroll_to_end()
    
    def add_error_message(self, text):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"⚠ {text}\n\n", 'error')
        self.chat_display.config(state=tk.DISABLED)
        self.smooth_scroll_to_end()
    
    def add_user_message(self, text):
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")
        msg_id = f"msg_{datetime.now().timestamp()}"
        
        self.chat_display.insert(tk.END, f"\nst0ne", 'user_name')
        
        ts_tag = f"ts_{msg_id}"
        self.chat_display.tag_configure(ts_tag, foreground=self.colors['muted'], font=(self.main_font, 10))
        self.chat_display.insert(tk.END, f"  {timestamp}", ts_tag)
        self.chat_display.tag_configure(ts_tag, foreground=self.colors['chat_bg'])
        self.chat_display.tag_bind(ts_tag, '<Enter>', 
                                   lambda e, t=ts_tag: self.chat_display.tag_configure(t, foreground=self.colors['muted']))
        self.chat_display.tag_bind(ts_tag, '<Leave>', 
                                   lambda e, t=ts_tag: self.chat_display.tag_configure(t, foreground=self.colors['chat_bg']))
        
        self.chat_display.insert(tk.END, f"\n{text}\n", 'user_text')
        self.chat_display.config(state=tk.DISABLED)
        self.smooth_scroll_to_end()

    def get_system_prompt(self):
        """
        CRITICAL FIX: System prompt that ENFORCES knowledge base usage
        """
        return """You are Bro Bro, a technical expert powered by a comprehensive knowledge base containing GoHighLevel documentation, business strategy books (Alex Hormozi, Russell Brunson), cannabis tissue culture research, and YouTube tutorials.

MANDATORY RULES - YOU MUST FOLLOW THESE:
1. ALWAYS search and use information from your knowledge base FIRST
2. Base your responses PRIMARILY on the retrieved documents
3. When you find relevant information, mention the source naturally: "Based on the documentation..." or "According to the training materials..."
4. If the knowledge base doesn't have specific information on a topic, clearly state: "I don't have specific documentation on this in my knowledge base, but here's general guidance..."
5. NEVER invent specific procedures, settings, or configurations that aren't in the retrieved documents

RESPONSE STYLE:
- Be direct and technical - get to the answer immediately
- Explain the WHY behind each recommendation
- Use numbered steps ONLY for sequential procedures
- Keep responses focused - aim for 200-400 words unless complexity requires more
- Write in natural paragraphs, not excessive bullet points
- Reference specific sources when applicable

CONVERSATION AWARENESS:
- Remember what was discussed earlier in this conversation
- When asked to "elaborate" or "explain more", refer back to the previous context
- Build on previous answers rather than repeating everything

At the end of your response, ask ONE focused follow-up question to clarify the user's specific situation or next step."""
    
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
        self.current_citations.clear()
        
        self.send_button.config(state=tk.DISABLED, bg='#6b7280')
        
        self.start_typing_indicator()
        
        thread = threading.Thread(target=self.query_knowledge_base, args=(user_input,))
        thread.daemon = True
        thread.start()
    
    def query_knowledge_base(self, question):
        """
        CRITICAL FIX: Includes conversation history for context retention
        """
        try:
            system_instruction = self.get_system_prompt()
            
            # BUILD CONVERSATION CONTEXT (last 6 messages = 3 exchanges)
            conversation_context = ""
            if self.conversation_history:
                recent_history = self.conversation_history[-6:]
                for msg in recent_history:
                    role = msg.get('role', 'user').upper()
                    content = msg.get('content', '')
                    # Truncate long messages in history to save tokens
                    if len(content) > 500:
                        content = content[:500] + "..."
                    conversation_context += f"{role}: {content}\n\n"
            
            # Create full prompt with history
            if conversation_context:
                full_prompt = f"""PREVIOUS CONVERSATION:
{conversation_context}
---
CURRENT QUESTION: {question}

Search your knowledge base and provide a response based on what you find. Remember the conversation context above."""
            else:
                full_prompt = question
            
            # QUERY WITH FILE SEARCH
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=2000,  # Reduced to prevent over-long responses
                    temperature=0.2,  # Lower = more factual, less creative hallucination
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[self.store_id]
                            )
                        )
                    ]
                )
            )
            
            # Extract response text
            if hasattr(response, 'text') and response.text:
                answer = response.text
            else:
                answer = self._extract_text_from_candidates(response)
            
            # STORE IN CONVERSATION HISTORY
            self.conversation_history.append({
                'role': 'user',
                'content': question
            })
            self.conversation_history.append({
                'role': 'assistant', 
                'content': answer
            })
            
            # Trim history if too long (keep last 10 exchanges)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            # Extract citations from grounding metadata
            citations = self._extract_citations(response)
            
            self.root.after(0, lambda: self.display_response(answer, citations))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.add_error_message(f"Error: {error_msg}"))
            self.root.after(0, self.reset_ui_state)
    
    def _extract_text_from_candidates(self, response):
        """Helper to extract text from response candidates"""
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                return part.text
        return "I received your question but couldn't generate a response. The File Search may not have found relevant documents."
    
    def _extract_citations(self, response):
        """Extract grounding citations from response metadata"""
        citations = []
        try:
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                        metadata = candidate.grounding_metadata
                        if hasattr(metadata, 'grounding_chunks') and metadata.grounding_chunks:
                            for chunk in metadata.grounding_chunks:
                                source_name = 'Unknown source'
                                if hasattr(chunk, 'retrieved_context'):
                                    ctx = chunk.retrieved_context
                                    if hasattr(ctx, 'uri') and ctx.uri:
                                        # Extract filename from URI
                                        source_name = ctx.uri.split('/')[-1]
                                        # Clean up the name
                                        source_name = source_name.replace('%20', ' ').replace('_', ' ')
                                    elif hasattr(ctx, 'title') and ctx.title:
                                        source_name = ctx.title
                                elif hasattr(chunk, 'web'):
                                    if hasattr(chunk.web, 'uri') and chunk.web.uri:
                                        source_name = chunk.web.uri.split('/')[-1]
                                    elif hasattr(chunk.web, 'title') and chunk.web.title:
                                        source_name = chunk.web.title
                                elif hasattr(chunk, 'source') and chunk.source:
                                    source_name = str(chunk.source)
                                citations.append({'source': source_name})
        except Exception as e:
            print(f"Citation extraction error: {e}")
        return citations

    def add_assistant_message(self, text, citations=None):
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")
        msg_id = f"msg_{datetime.now().timestamp()}"
        
        self.chat_display.insert(tk.END, f"\nBro Bro", 'assistant_name')
        
        ts_tag = f"ts_{msg_id}"
        self.chat_display.tag_configure(ts_tag, foreground=self.colors['muted'], font=(self.main_font, 10))
        self.chat_display.insert(tk.END, f"  {timestamp}", ts_tag)
        self.chat_display.tag_configure(ts_tag, foreground=self.colors['chat_bg'])
        self.chat_display.tag_bind(ts_tag, '<Enter>', 
                                   lambda e, t=ts_tag: self.chat_display.tag_configure(t, foreground=self.colors['muted']))
        self.chat_display.tag_bind(ts_tag, '<Leave>', 
                                   lambda e, t=ts_tag: self.chat_display.tag_configure(t, foreground=self.colors['chat_bg']))
        
        self.chat_display.insert(tk.END, "\n")
        
        # Store citations for click access
        if citations:
            for i, cite in enumerate(citations, 1):
                self.current_citations[str(i)] = cite.get('source', 'Unknown source')
        
        # Format and display the response
        formatted_text = self.format_response(text)
        self.insert_text_with_citations(formatted_text)
        
        # Show sources used (if any)
        if citations and len(citations) > 0:
            unique_sources = list(set([c.get('source', '') for c in citations]))[:3]
            if unique_sources:
                sources_text = f"\n    📚 Sources: {', '.join(unique_sources)}"
                self.chat_display.insert(tk.END, sources_text, 'source_info')
        
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.config(state=tk.DISABLED)
        self.smooth_scroll_to_end()
    
    def insert_text_with_citations(self, text):
        """Insert text with clickable citation markers"""
        pattern = r'\[(\d+)\]'
        last_end = 0
        
        for match in re.finditer(pattern, text):
            before_text = text[last_end:match.start()]
            self.chat_display.insert(tk.END, before_text, 'assistant_text')
            
            cite_num = match.group(1)
            cite_tag = f"cite_{cite_num}"
            
            self.chat_display.tag_configure(cite_tag, foreground=self.colors['citation'], 
                                           font=(self.main_font, 12, 'bold'))
            self.chat_display.tag_bind(cite_tag, '<Button-1>', self.on_citation_click)
            self.chat_display.tag_bind(cite_tag, '<Enter>', lambda e: self.chat_display.config(cursor='hand2'))
            self.chat_display.tag_bind(cite_tag, '<Leave>', lambda e: self.chat_display.config(cursor='arrow'))
            
            self.chat_display.insert(tk.END, f"[{cite_num}]", cite_tag)
            last_end = match.end()
        
        if last_end < len(text):
            self.chat_display.insert(tk.END, text[last_end:], 'assistant_text')
    
    def format_response(self, text):
        """
        IMPROVED: Cleaner formatting that preserves structure without excess
        """
        if text is None:
            return "    No response received from the knowledge base.\n"
        
        # Remove markdown bold/italic
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'(?<!\*)\*(?!\*)([^*]+)(?<!\*)\*(?!\*)', r'\1', text)
        
        # Remove markdown headers but keep text
        text = re.sub(r'^#{1,6}\s+(.+)$', r'\1', text, flags=re.MULTILINE)
        
        # Process line by line
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                formatted_lines.append('')
            elif re.match(r'^\d+\.\s+', stripped):
                # Numbered list - proper indent
                formatted_lines.append('    ' + stripped)
            elif stripped.startswith(('- ', '* ', '• ')):
                # Bullet point - slightly more indent
                formatted_lines.append('      ' + stripped)
            elif stripped.upper().startswith('WHY:') or 'WHY:' in stripped[:10]:
                # WHY explanation - clean it up
                clean_why = stripped.replace('**', '')
                formatted_lines.append('        ' + clean_why)
            else:
                # Regular text
                formatted_lines.append('    ' + stripped)
        
        # Join and clean excessive blank lines
        result = '\n'.join(formatted_lines)
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result
    
    def smooth_scroll_to_end(self):
        """Scroll to end of chat - FIXED for smoother behavior"""
        self.chat_display.see(tk.END)
        self.chat_display.update_idletasks()
        # Small delay to ensure rendering is complete
        self.root.after(10, lambda: self.chat_display.see(tk.END))
    
    def start_typing_indicator(self):
        self.chat_display.config(state=tk.NORMAL)
        self.thinking_line_start = self.chat_display.index("end-1c linestart")
        self.chat_display.insert(tk.END, "\n    Thinking.", 'thinking')
        self.chat_display.config(state=tk.DISABLED)
        self.typing_dots = 0
        self.animate_typing()
    
    def animate_typing(self):
        if self.thinking_line_start is None:
            return
        
        dots = "." * ((self.typing_dots % 3) + 1)
        spaces = " " * (3 - len(dots))
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(self.thinking_line_start, tk.END)
        self.chat_display.insert(tk.END, f"\n    Thinking{dots}{spaces}", 'thinking')
        self.chat_display.config(state=tk.DISABLED)
        
        self.update_status(f"Searching KB{dots}{spaces}", self.colors['thinking'])
        
        self.smooth_scroll_to_end()
        
        self.typing_dots += 1
        self.typing_indicator_id = self.root.after(400, self.animate_typing)
    
    def stop_typing_indicator(self):
        if self.typing_indicator_id:
            self.root.after_cancel(self.typing_indicator_id)
            self.typing_indicator_id = None
        
        if self.thinking_line_start is not None:
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(self.thinking_line_start, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.thinking_line_start = None
    
    def display_response(self, answer, citations):
        self.stop_typing_indicator()
        self.add_assistant_message(answer, citations)
        self.reset_ui_state()
    
    def reset_ui_state(self):
        self.update_status("✓ Connected", '#4ade80')
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
        self.conversation_history = []  # CRITICAL: Clear history too
        self.current_citations.clear()
        self.add_system_message("Chat cleared. Conversation history reset.")


def main():
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
