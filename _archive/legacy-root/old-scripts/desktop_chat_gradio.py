"""
GHL WHIZ - Desktop Chat Interface (Gradio)
Modern chat UI that queries your ChromaDB backend
"""

import gradio as gr
import requests
from typing import List, Tuple

class GHLWizChat:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.chat_history = []
    
    def query_chromadb(self, message: str, history: List[Tuple[str, str]]) -> str:
        """Query the GHL WHIZ ChromaDB backend"""
        try:
            # Call your FastAPI backend
            response = requests.post(
                f"{self.api_url}/query",  # Adjust endpoint as needed
                json={
                    "query": message,
                    "n_results": 5  # Number of results to retrieve
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Format response with sources
                answer = self._format_response(data)
                return answer
            else:
                return f"❌ Error querying database: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to GHL WHIZ backend. Make sure FastAPI server is running on http://localhost:8000"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _format_response(self, data: dict) -> str:
        """Format the response with retrieved context"""
        # Adjust this based on your actual API response structure
        if "results" in data:
            results = data["results"]
            
            response = "📚 **Retrieved Information:**\n\n"
            
            for i, result in enumerate(results[:3], 1):
                doc = result.get("document", "")
                metadata = result.get("metadata", {})
                source = metadata.get("source", "Unknown")
                
                response += f"**Source {i}:** {source}\n"
                response += f"{doc[:300]}...\n\n"
            
            return response
        else:
            return "No results found."

def create_interface():
    """Create the Gradio chat interface"""
    chat = GHLWizChat()
    
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        font-family: 'Inter', sans-serif;
    }
    #chatbot {
        height: 600px;
    }
    """
    
    with gr.Blocks(css=custom_css, title="GHL WHIZ Chat", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 🚀 GHL WHIZ - Desktop Chat
            ### Query your 1,235+ indexed GoHighLevel knowledge base
            """
        )
        
        chatbot = gr.Chatbot(
            elem_id="chatbot",
            height=600,
            bubble_full_width=False,
            avatar_images=(None, "🤖")
        )
        
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Ask anything about GoHighLevel...",
                container=False,
                scale=7
            )
            submit = gr.Button("Send", scale=1, variant="primary")
            clear = gr.Button("Clear", scale=1)
        
        gr.Markdown(
            """
            ### 💡 Example Questions:
            - How do I set up email authentication in GHL?
            - What are best practices for workflow automation?
            - Show me information about conversation AI
            """
        )
        
        def respond(message, history):
            bot_response = chat.query_chromadb(message, history)
            history.append((message, bot_response))
            return "", history
        
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        submit.click(respond, [msg, chatbot], [msg, chatbot])
        clear.click(lambda: None, None, chatbot, queue=False)
    
    return demo

if __name__ == "__main__":
    print("🚀 Starting GHL WHIZ Desktop Chat...")
    print("📍 Make sure your FastAPI backend is running!")
    print("🌐 Opening interface at http://localhost:7860")
    
    demo = create_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False  # Set to True if you want a public link
    )
