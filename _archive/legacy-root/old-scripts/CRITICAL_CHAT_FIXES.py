"""
GHL WHIZ KB Chat - CRITICAL FIXES
===================================

Apply these changes to ghl_kb_chat.py to fix the RAG pipeline:
"""

# ============================================================
# FIX #1: SYSTEM PROMPT (Replace get_system_prompt method)
# ============================================================
def get_system_prompt(self):
    """
    FIXED: Forces KB usage and proper citation
    """
    return """You are Bro Bro, an expert assistant powered by a comprehensive knowledge base about GoHighLevel, Cannabis Tissue Culture, and Business Strategy.

CRITICAL RULES:
1. ALWAYS search the knowledge base FIRST before answering
2. Base your responses ONLY on information retrieved from the knowledge base
3. If you find relevant information, cite the source by mentioning the document name
4. If no relevant information is found in the KB, clearly state: "I couldn't find specific information about this in my knowledge base. Here's general guidance based on my training..."
5. NEVER make up information that isn't in the retrieved documents

RESPONSE FORMAT:
- Start with a direct answer to the question
- Provide technical details with the WHY behind recommendations  
- Reference specific documents when available: "According to [document-name]..."
- Keep lists concise (max 5-7 items per list)
- Use natural paragraph flow, not excessive bullet points

At the end, ask 1 focused follow-up question (not 3) to clarify the user's specific situation."""


# ============================================================
# FIX #2: CONVERSATION HISTORY (Replace query_knowledge_base)
# ============================================================
def query_knowledge_base(self, question):
    try:
        system_instruction = self.get_system_prompt()
        
        # BUILD CONVERSATION CONTEXT
        # Include last 6 messages (3 exchanges) for context
        conversation_context = ""
        if self.conversation_history:
            recent_history = self.conversation_history[-6:]
            for msg in recent_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                conversation_context += f"{role.upper()}: {content}\n\n"
        
        # Create the full prompt with history
        if conversation_context:
            full_prompt = f"""CONVERSATION HISTORY:
{conversation_context}

CURRENT QUESTION:
{question}

Search the knowledge base and respond based on what you find."""
        else:
            full_prompt = question
        
        # QUERY WITH RETRIEVAL CONFIG
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=2000,  # Reduced to prevent over-long responses
                temperature=0.3,  # Lower = more factual, less creative
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[self.store_id],
                            # If the API supports these (check docs):
                            # dynamic_retrieval_config=types.DynamicRetrievalConfig(
                            #     mode='MODE_DYNAMIC',
                            #     dynamic_threshold=0.3
                            # )
                        )
                    )
                ]
            )
        )
        
        # Extract response
        if hasattr(response, 'text') and response.text:
            answer = response.text
        else:
            answer = self._extract_text_from_candidates(response)
        
        # Store in conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': question
        })
        self.conversation_history.append({
            'role': 'assistant', 
            'content': answer
        })
        
        # Extract citations
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
    return "I received your question but couldn't generate a response."


def _extract_citations(self, response):
    """Helper to extract grounding citations"""
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
                                    source_name = ctx.uri.split('/')[-1]
                                elif hasattr(ctx, 'title') and ctx.title:
                                    source_name = ctx.title
                            citations.append({'source': source_name})
    except Exception as e:
        print(f"Citation extraction error: {e}")
    return citations


# ============================================================
# FIX #3: CLEAR CHAT (Update clear_chat to reset history)
# ============================================================
def clear_chat(self):
    self.chat_display.config(state=tk.NORMAL)
    self.chat_display.delete("1.0", tk.END)
    self.chat_display.config(state=tk.DISABLED)
    self.conversation_history = []  # RESET HISTORY
    self.current_citations.clear()
    self.add_system_message("Chat cleared. History reset.")


# ============================================================
# FIX #4: FORMAT RESPONSE (Simpler, cleaner formatting)
# ============================================================
def format_response(self, text):
    """
    SIMPLIFIED: Less aggressive formatting, preserve natural flow
    """
    if text is None:
        return "No response received.\n"
    
    # Clean up markdown
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold
    text = re.sub(r'__([^_]+)__', r'\1', text)       # Remove underline
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)  # Remove headers
    
    # Add consistent indent
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted_lines.append('')
        elif re.match(r'^\d+\.', stripped):  # Numbered list
            formatted_lines.append('    ' + stripped)
        elif stripped.startswith(('- ', '* ', '• ')):  # Bullet
            formatted_lines.append('      ' + stripped)
        else:
            formatted_lines.append('    ' + stripped)
    
    result = '\n'.join(formatted_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)  # Clean up excess newlines
    
    return result


# ============================================================
# USAGE: 
# 1. Copy these functions into ghl_kb_chat.py
# 2. Replace the existing methods with these fixed versions
# 3. Make sure self.conversation_history is initialized in __init__
# ============================================================
