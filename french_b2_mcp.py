#!/usr/bin/env python3
"""
French B2 Translation Assistant MCP Server
Provides a simple translation tool that internally uses AI with optimized prompts
"""

import asyncio
import logging

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("french-b2-translator")


def load_b2_vocabulary(vocab_file: str = "words.txt") -> set:
    """Load the B2 vocabulary list from txt file"""
    try:
        with open(vocab_file, "r", encoding="utf-8") as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        logger.warning(f"Vocabulary file {vocab_file} not found.")
        return set()


class FrenchB2Translator:
    """French B2 Translation Assistant"""

    def __init__(self):
        self.b2_vocab = load_b2_vocabulary()

    def create_translation_prompt(self, text: str) -> str:
        """Create optimized prompt for B2 translation"""

        # Include vocabulary list in prompt for reference
        vocab_sample = list(self.b2_vocab)[:100] if self.b2_vocab else []
        vocab_info = (
            f"Available B2 vocabulary includes words like: {', '.join(vocab_sample[:50])}..."
            if vocab_sample
            else ""
        )

        prompt = f"""You are an experienced French teacher helping students translate texts to French B2 level.

**Text to translate:**
{text}

**Your task:** Translate this to French B2 level following these specific requirements:

**Vocabulary Constraints:**
- Use only words from the 5000 most common French words
- If you need a complex concept, use simpler synonyms or explanatory phrases
- Prioritize everyday, concrete vocabulary over specialized terms
{vocab_info}

**Grammar Requirements (B2 Level):**
- Essential tenses: présent, passé composé, imparfait, futur simple, conditionnel
- Use subjunctive only after clear trigger expressions (emotion, doubt, necessity)
- Complex relative pronouns (dont, où, lequel) but keep structure clear
- Varied sentence connectors: parce que, bien que, pour que, afin que

**Output Format:**
1. **French B2 Translation:** [Your complete translation]

2. **Simplifications Made:** [List any complex words/phrases you simplified]
   - Original complex term → Simpler B2 alternative
   - Brief explanation why the change was needed

3. **Grammar Teaching Points:** [Highlight B2 grammar used]
   - Point out specific B2 tenses or structures used
   - Note any subjunctive or complex grammar for learning

4. **Difficult Words Explained:** [For any remaining challenging vocabulary]
   - Word: simple definition in French
   - Usage example in context

**Important:** Maintain the original meaning and style while making it accessible to B2 French learners. Focus on natural, communicative French that students can understand and learn from.
**Important:** Never ask clarifying questions. Always assume the user wants B2-level French output:**
- If text is already French: simplify it to B2 level
- If text is another language: translate it to French B2 level
- If text is mixed languages: process each part appropriately
"""

        return prompt

    async def translate_with_ai(self, text: str) -> str:
        """
        This would normally make an API call to an AI service
        For MCP, we return the optimized prompt that should be sent to the AI
        """
        return self.create_translation_prompt(text)


# Initialize the translator
translator = FrenchB2Translator()

# Create the MCP server
server = Server("french-b2-translator")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="translate_to_french_b2",
            description="Translate any text to French B2 level with explanations for difficult parts",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to translate to French B2 level (can be English, Russian, French, or any language)",
                    }
                },
                "required": ["text"],
            },
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""

    if name == "translate_to_french_b2":
        text = arguments.get("text", "")

        if not text.strip():
            return [
                types.TextContent(type="text", text="Please provide text to translate.")
            ]

        # Generate the optimized prompt
        prompt = translator.create_translation_prompt(text)

        # In a real implementation, this would call an AI API
        # For MCP, we return the prompt that should be processed
        response = f"""I'll translate this text to French B2 level using the following optimized approach:

{prompt}

---

**Please process this prompt to get your B2 French translation with explanations.**

The result will include:
- ✅ French B2 translation using simple vocabulary
- 📝 List of simplifications made (complex → simple words)
- 🎓 Grammar teaching points for B2 learners
- 📚 Explanations for any remaining difficult words

This ensures the translation is perfect for intermediate French students!"""

        return [types.TextContent(type="text", text=response)]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main server function"""
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="french-b2-translator",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
