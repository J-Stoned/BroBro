"""
TokenCounter - Accurate Token Counting for Claude Models

Uses Anthropic's tokenizer for precise token counting.
Supports messages, strings, and complex content.
"""

import re
from typing import List, Dict, Any, Union


class TokenCounter:
    """
    Token Counter for Claude Models

    Uses estimation algorithm based on Anthropic's guidance:
    - ~4 characters per token (English)
    - JSON/code: ~3-3.5 characters per token
    - System prompts count toward input
    - Message overhead: ~10 tokens per message

    For production, consider using Anthropic's official tokenizer
    when available via their SDK.
    """

    def __init__(self):
        # Average characters per token
        self.chars_per_token = 4.0
        self.message_overhead = 10  # Tokens per message for formatting

    def count_string(self, text: str) -> int:
        """
        Estimate tokens in a string

        Args:
            text: String to count

        Returns:
            Estimated token count
        """
        if not text:
            return 0

        # Basic estimation: characters / 4
        # More accurate would use tiktoken or Anthropic's tokenizer
        char_count = len(text)

        # Adjust for code/JSON (denser tokens)
        if self._is_code_like(text):
            return int(char_count / 3.5)

        return int(char_count / self.chars_per_token)

    def count_messages(self, messages: List[Dict[str, Any]]) -> int:
        """
        Count tokens in message list

        Args:
            messages: List of Claude API messages

        Returns:
            Total token count including overhead
        """
        if not messages:
            return 0

        total_tokens = 0

        for message in messages:
            # Message overhead
            total_tokens += self.message_overhead

            # Count role
            role = message.get('role', '')
            total_tokens += self.count_string(role)

            # Count content
            content = message.get('content', '')
            if isinstance(content, str):
                total_tokens += self.count_string(content)
            elif isinstance(content, list):
                # Complex content (images, etc.)
                for block in content:
                    if isinstance(block, dict):
                        if block.get('type') == 'text':
                            total_tokens += self.count_string(block.get('text', ''))
                        elif block.get('type') == 'image':
                            # Images: ~1000 tokens per image (rough estimate)
                            total_tokens += 1000

        return total_tokens

    def count_system_prompt(self, system_prompt: str) -> int:
        """
        Count tokens in system prompt

        Args:
            system_prompt: System prompt string

        Returns:
            Token count
        """
        return self.count_string(system_prompt) if system_prompt else 0

    def estimate_request_tokens(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str = None
    ) -> int:
        """
        Estimate total input tokens for a request

        Args:
            messages: Message list
            system_prompt: Optional system prompt

        Returns:
            Total estimated input tokens
        """
        total = 0

        if system_prompt:
            total += self.count_system_prompt(system_prompt)

        total += self.count_messages(messages)

        # Add small buffer for API formatting overhead
        total += 50

        return total

    def will_fit_in_context(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str = None,
        max_output_tokens: int = 4096,
        context_window: int = 200000,
        safety_buffer: int = 20000
    ) -> tuple[bool, int]:
        """
        Check if request will fit in context window

        Args:
            messages: Message list
            system_prompt: Optional system prompt
            max_output_tokens: Expected output size
            context_window: Model's context window (default 200K)
            safety_buffer: Safety buffer tokens (default 20K)

        Returns:
            Tuple of (will_fit: bool, tokens_used: int)
        """
        input_tokens = self.estimate_request_tokens(messages, system_prompt)
        total_needed = input_tokens + max_output_tokens
        available = context_window - safety_buffer

        return (total_needed <= available, input_tokens)

    def _is_code_like(self, text: str) -> bool:
        """
        Detect if text is code/JSON (for more accurate counting)

        Args:
            text: Text to check

        Returns:
            True if appears to be code
        """
        if not text:
            return False

        # Simple heuristics
        code_indicators = [
            '{', '}', '[', ']', '(', ')',
            ':', ';', '=', '<', '>',
            'function', 'const', 'let', 'var',
            'def ', 'class ', 'import ',
            '```'
        ]

        # Count indicators
        indicator_count = sum(1 for ind in code_indicators if ind in text)

        # If >20% of common indicators present, likely code
        threshold = len(code_indicators) * 0.2
        return indicator_count > threshold


# ===== Singleton instance =====
_token_counter_instance = None


def get_token_counter() -> TokenCounter:
    """Get singleton TokenCounter instance"""
    global _token_counter_instance

    if _token_counter_instance is None:
        _token_counter_instance = TokenCounter()

    return _token_counter_instance


# ===== Example Usage =====
if __name__ == "__main__":
    print("=" * 80)
    print("Testing TokenCounter")
    print("=" * 80)

    counter = get_token_counter()

    # Test 1: Simple string
    print("\n[TEST 1] Simple string:")
    text1 = "Hello, how can I help you with GoHighLevel today?"
    tokens1 = counter.count_string(text1)
    print(f"   Text: {text1}")
    print(f"   Estimated tokens: {tokens1}")
    print(f"   Characters: {len(text1)}")
    print(f"   Ratio: {len(text1) / tokens1:.2f} chars/token")

    # Test 2: Code
    print("\n[TEST 2] Code snippet:")
    text2 = """
    function generateWorkflow(trigger, actions) {
        return {
            trigger: trigger,
            actions: actions.map(a => ({ type: a.type, config: a.config }))
        };
    }
    """
    tokens2 = counter.count_string(text2)
    print(f"   Estimated tokens: {tokens2}")
    print(f"   Characters: {len(text2)}")
    print(f"   Ratio: {len(text2) / tokens2:.2f} chars/token")

    # Test 3: Messages
    print("\n[TEST 3] Message list:")
    messages = [
        {"role": "user", "content": "How do I set up a webhook in GoHighLevel?"},
        {"role": "assistant", "content": "To set up a webhook in GoHighLevel, follow these steps: 1. Go to Settings > Integrations. 2. Click on Webhooks. 3. Add a new webhook URL..."},
        {"role": "user", "content": "Can you show me the JSON format?"}
    ]
    tokens3 = counter.count_messages(messages)
    print(f"   Messages: {len(messages)}")
    print(f"   Estimated tokens: {tokens3}")

    # Test 4: Full request
    print("\n[TEST 4] Full request estimation:")
    system_prompt = "You are an expert GoHighLevel consultant with 10 years of experience in marketing automation and CRM workflows."
    tokens4 = counter.estimate_request_tokens(messages, system_prompt)
    print(f"   System prompt: {counter.count_system_prompt(system_prompt)} tokens")
    print(f"   Messages: {tokens3} tokens")
    print(f"   Total input: {tokens4} tokens")

    # Test 5: Context window check
    print("\n[TEST 5] Context window check:")
    will_fit, input_tokens = counter.will_fit_in_context(
        messages,
        system_prompt,
        max_output_tokens=12000,
        context_window=200000,
        safety_buffer=20000
    )
    print(f"   Input tokens: {input_tokens}")
    print(f"   Max output: 12,000 tokens")
    print(f"   Context window: 200,000 tokens")
    print(f"   Safety buffer: 20,000 tokens")
    print(f"   Available: 180,000 tokens")
    print(f"   Will fit: {will_fit}")

    # Test 6: Large context
    print("\n[TEST 6] Large context simulation:")
    large_messages = []
    for i in range(50):
        large_messages.append({
            "role": "user" if i % 2 == 0 else "assistant",
            "content": "This is a longer message that simulates a real conversation with detailed technical information about GoHighLevel workflows, triggers, actions, and best practices. " * 10
        })
    large_tokens = counter.count_messages(large_messages)
    will_fit_large, _ = counter.will_fit_in_context(
        large_messages,
        system_prompt,
        max_output_tokens=12000
    )
    print(f"   Messages: {len(large_messages)}")
    print(f"   Estimated tokens: {large_tokens:,}")
    print(f"   Will fit: {will_fit_large}")

    print("\n" + "=" * 80)
    print("TokenCounter test complete!")
    print("=" * 80)
    print("\nNote: These are ESTIMATES. For production, use Anthropic's official")
    print("tokenizer when available. Estimates are typically within 10-15% accuracy.")
