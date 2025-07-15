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

    def create_b2_compliant_text(self, text: str) -> str:
        """Create instructions for B2-compliant text with vocabulary enforcement"""

        return f"""SIMPLIFY this French text to B2 level:

Text: "{text}"

Instructions:
1. Simplify to B2 level French (use only common vocabulary and grammar)
2. Keep the meaning but use simpler words and structures
3. Use only words from the 5000 most common French words
4. Provide ONLY the simplified French text as output"""

    def simplify_to_b2(self, text: str) -> str:
        """
        Main function to simplify text to B2 level with vocabulary enforcement
        """
        # Create initial simplification instruction
        instruction = self.create_b2_compliant_text(text)

        return f"""{instruction}

IMPORTANT: After providing your simplification, I will check it against the B2 vocabulary list and suggest replacements for any non-B2 words.

B2 vocabulary includes {len(self.original_vocab)} common French words."""


# Initialize the sSimplifier
simplifier = FrenchB2Simplifier()

# Create the MCP server
server = Server("french-b2-simplifier")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="simplify_to_french_b2_instructions",
            description="Simplify French text to French B2 level using only 5000 most used french words",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to simplify",
                    }
                },
                "required": ["text"],
            },
        ),
        types.Tool(
            name="validate_b2_vocabulary",
            description="Check if French text uses only B2 vocabulary and get replacement suggestions for non-B2 words",
            inputSchema={
                "type": "object",
                "properties": {
                    "french_text": {
                        "type": "string",
                        "description": "French text to validate against B2 vocabulary",
                    }
                },
                "required": ["french_text"],
            },
        ),
        types.Tool(
            name="fix_b2_vocabulary",
            description="Replace non-B2 words in French text with B2 alternatives",
            inputSchema={
                "type": "object",
                "properties": {
                    "french_text": {
                        "type": "string",
                        "description": "French text with potential non-B2 vocabulary to fix",
                    }
                },
                "required": ["french_text"],
            },
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""

    if name == "simplify_to_french_b2_instructions":
        text = arguments.get("text", "")

        if not text.strip():
            return [
                types.TextContent(type="text", text="Please provide text to simplify.")
            ]

        # Generate B2 simplification instruction
        response = simplifier.simplify_to_b2(text)

        return [types.TextContent(type="text", text=response)]

    elif name == "validate_b2_vocabulary":
        french_text = arguments.get("french_text", "")

        if not french_text.strip():
            return [
                types.TextContent(type="text", text="Please provide French text to validate.")
            ]

        # Generate validation report with suggestions
        validation = simplifier.validate_vocabulary(french_text)
        report = simplifier.create_validation_report(french_text)

        if validation['violations']:
            suggestions = simplifier.get_b2_replacement_suggestions(validation['violations'])
            report += f"\n## Suggested B2 Replacements\n\n"
            for word, replacement in suggestions.items():
                report += f"- **{word}** -> **{replacement}**\n"

        return [types.TextContent(type="text", text=report)]

    elif name == "fix_b2_vocabulary":
        french_text = arguments.get("french_text", "")

        if not french_text.strip():
            return [
                types.TextContent(type="text", text="Please provide French text to fix.")
            ]

        # Find non-B2 words and suggest replacements
        validation = simplifier.validate_vocabulary(french_text)

        if not validation['violations']:
            return [types.TextContent(type="text", text=f"PASSED: Text is already B2-compliant!\n\n**Text:** {french_text}")]

        suggestions = simplifier.get_b2_replacement_suggestions(validation['violations'])

        response = f"""**B2 Vocabulary Fixes Needed**

**Original text:** {french_text}

**Non-B2 words found:** {len(validation['violations'])} words

**Suggested replacements:**
"""
        for word, replacement in suggestions.items():
            response += f"\n- **{word}** -> **{replacement}**"

        response += f"""

**Instructions:** Please rewrite the text using these B2 replacements to make it fully B2-compliant."""

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
