#!/usr/bin/env python3
"""
French B2 Simplifier Assistant MCP Server
Simplifies text to French B2 level and enforces B2 vocabulary compliance
"""

import asyncio
import logging
import re

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("french-b2-simplifier")

import spacy
nlp = spacy.load("fr_core_news_sm")


def load_b2_vocabulary(vocab_file: str = "words.txt") -> tuple[set, set]:
    """Load the B2 vocabulary list from txt file"""
    try:
        with open(vocab_file, "r", encoding="utf-8") as f:
            original_vocab = {line.strip().lower() for line in f if line.strip()}

            # Create normalized version if spaCy is available
            normalized_vocab = set()
            for word in original_vocab:
                doc = nlp(word)
                if doc:
                    normalized_vocab.add(doc[0].lemma_.lower())
            return original_vocab, normalized_vocab
    except FileNotFoundError:
        logger.warning(f"Vocabulary file {vocab_file} not found.")
        return set(), set()


class FrenchB2Simplifier:
    """French B2 Simplifier Assistant"""

    def __init__(self):
        self.original_vocab, self.normalized_vocab = load_b2_vocabulary()

    def normalize_french_words(self, text: str) -> set:
        """Extract normalized French words from text"""
        doc = nlp(text)
        normalized_words = set()

        for token in doc:
            if token.is_alpha and not token.is_stop:
                # Use lemma (base form) of the word
                lemma = token.lemma_.lower()
                normalized_words.add(lemma)

        return normalized_words

    def validate_vocabulary(self, french_text: str) -> dict:
        """Check if text uses only B2 vocabulary"""
        normalized_words = self.normalize_french_words(french_text)

        violations = []
        for word in normalized_words:
            if word not in self.normalized_vocab:
                violations.append(word)

        return {
            'is_valid': len(violations) == 0,
            'violations': violations,
            'total_unique_words': len(normalized_words),
            'coverage': (len(normalized_words) - len(violations)) / len(normalized_words) * 100 if normalized_words else 0
        }

    def create_validation_report(self, french_text: str) -> str:
        """Create a detailed validation report"""
        validation = self.validate_vocabulary(french_text)

        report = f"""# B2 Vocabulary Validation Report

## Text Analysis
- **Total unique words:** {validation['total_unique_words']}
- **B2 vocabulary coverage:** {validation['coverage']:.1f}%
- **Validation status:** {'PASSED' if validation['is_valid'] else 'FAILED'}

## Text Analyzed
{french_text}

"""

        if validation['violations']:
            report += f"""## Vocabulary Violations ({len(validation['violations'])} words)
The following words are NOT in the B2 vocabulary list:

"""
            for word in sorted(validation['violations']):
                report += f"- **{word}**\n"

            report += f"""
## Recommendations
1. Replace the violated words with simpler B2 alternatives
2. Use the simplifier tool to get a B2-compliant version
3. Check if any violations are proper nouns that can be kept as-is
"""
        else:
            report += """## All Clear!
All words in this text are within the B2 vocabulary constraints.
"""

        return report

    def get_b2_replacement_suggestions(self, non_b2_words: list) -> dict:
        """Get suggestions for replacing non-B2 words with B2 alternatives"""
        suggestions = {}

        for word in non_b2_words:
            # Generic instruction for all non-B2 words
            suggestions[word] = f"[find B2 equivalent for '{word}']"

        return suggestions

    def simplify_to_b2(self, text: str) -> str:
        """
        Main function to simplify text to B2 level with comprehensive analysis
        """
        # First, validate the original text
        validation = self.validate_vocabulary(text)

        # Build comprehensive response
        response = f"""# French B2 Text Simplification

## Original Text Analysis
**Text:** {text}

**B2 Vocabulary Status:** {'COMPLIANT' if validation['is_valid'] else 'NEEDS SIMPLIFICATION'}
- **Unique words:** {validation['total_unique_words']}
- **B2 coverage:** {validation['coverage']:.1f}%"""

        if validation['violations']:
            response += f"""
- **Non-B2 words:** {len(validation['violations'])} words need replacement

### Words to Replace:
"""
            for word in sorted(validation['violations']):
                response += f"- **{word}** (find B2 alternative)\n"

        response += f"""

## Simplification Instructions

Please SIMPLIFY this French text to B2 level:

**Text to simplify:** "{text}"

**Requirements:**
1. Use only B2-level vocabulary (5000 most common French words)
2. Simplify grammar structures while keeping the original meaning
3. Replace complex words with simpler alternatives
4. Ensure the text flows naturally in French"""

        if validation['violations']:
            response += f"""
5. **Priority replacements needed for:** {', '.join(sorted(validation['violations']))}"""

        response += f"""

**B2 Vocabulary Reference:** This server validates against {len(self.original_vocab)} approved B2 French words.

**Output:** Provide ONLY the simplified French text."""

        return response


# Initialize the sSimplifier
simplifier = FrenchB2Simplifier()

# Create the MCP server
server = Server("french-b2-simplifier")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="simplify_to_french_b2",
            description="Simplify French text to B2 level with automatic vocabulary validation and comprehensive guidance",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "French text to simplify to B2 level",
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

    if name == "simplify_to_french_b2":
        text = arguments.get("text", "")

        if not text.strip():
            return [
                types.TextContent(type="text", text="Please provide text to simplify.")
            ]

        # Generate comprehensive B2 simplification with internal validation
        response = simplifier.simplify_to_b2(text)

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
                server_name="french-b2-simplifier",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
