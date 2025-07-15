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


def load_b2_vocabulary(vocab_file: str = "words.txt") -> set:
    """Load the B2 vocabulary list from txt file and lemmatize all words"""
    try:
        with open(vocab_file, "r", encoding="utf-8") as f:
            raw_words = {line.strip().lower() for line in f if line.strip()}

        # Lemmatize all vocabulary words for consistent comparison
        lemmatized_vocab = set()
        for word in raw_words:
            doc = nlp(word)
            if doc:
                lemma = doc[0].lemma_.lower()
                lemmatized_vocab.add(lemma)
                # Also keep the original word in case lemmatization changes it unexpectedly
                lemmatized_vocab.add(word)

        return lemmatized_vocab
    except FileNotFoundError:
        logger.warning(f"Vocabulary file {vocab_file} not found.")
        return set()


class FrenchB2Simplifier:
    """French B2 Simplifier Assistant"""

    def __init__(self):
        self.b2_vocab = load_b2_vocabulary()

    def get_lemmatized_words(self, text: str) -> set:
        """Extract lemmatized words from text, excluding stop words"""
        doc = nlp(text)
        lemmatized_words = set()

        for token in doc:
            if token.is_alpha and not token.is_stop:
                # Use lemma (base form) of the word
                lemma = token.lemma_.lower()
                lemmatized_words.add(lemma)

        return lemmatized_words

    def validate_vocabulary(self, french_text: str) -> dict:
        """Check if text uses only B2 vocabulary by comparing lemmas"""
        doc = nlp(french_text)
        violations = []
        all_words = set()

        for token in doc:
            if token.is_alpha and not token.is_stop:
                original_word = token.text.lower()
                lemma_word = token.lemma_.lower()
                all_words.add(original_word)

                # Check if lemmatized word is in our lemmatized vocabulary
                if lemma_word not in self.b2_vocab:
                    violations.append(original_word)

        return {
            'is_valid': len(violations) == 0,
            'violations': violations,
            'total_unique_words': len(all_words),
            'coverage': (len(all_words) - len(violations)) / len(all_words) * 100 if all_words else 0
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

    def get_b2_grammar_requirements(self) -> str:
        """Return B2 Level Grammar Requirements"""
        return """### B2 Level Grammar Requirements

Students at B2 level should master:

#### Essential Tenses (Must Use Confidently)

- Passé composé (compound past) - primary past tense
- Imparfait (imperfect) - for descriptions and habits
- Présent (present)
- Futur simple (simple future)
- Conditionnel présent (conditional)

#### Advanced Grammar (Introduce/Practice)

- Subjonctif présent (present subjunctive) after expressions of emotion, doubt, necessity
- Subjonctif passé (past subjunctive) for past actions in subjunctive context
- Plus-que-parfait (pluperfect) for actions before other past actions
- Complex relative pronouns (dont, où, lequel)

#### Passive voice

Gérondif (gerund) for simultaneous actions"""

    def simplify_to_b2(self, text: str) -> str:
        """
        Main function to simplify text to B2 level with comprehensive analysis
        Returns properly formatted Markdown output with word replacements and grammar requirements
        """
        # First, validate the original text
        validation = self.validate_vocabulary(text)

        # Build comprehensive Markdown response
        response = f"""# French B2 Text Simplification Report

## Original Text
```
{text}
```

## Analysis Summary
- **B2 Vocabulary Status:** {'COMPLIANT' if validation['is_valid'] else 'NEEDS SIMPLIFICATION'}
- **Total unique words:** {validation['total_unique_words']}
- **B2 vocabulary coverage:** {validation['coverage']:.1f}%
- **Words requiring replacement:** {len(validation['violations']) if validation['violations'] else 0}

## Vocabulary Compliance Check

### Approved B2 Words
All analyzed words are checked against a vocabulary of {len(self.b2_vocab)} approved B2 French words.

### Words Requiring Replacement"""

        if validation['violations']:
            response += f"""

The following **{len(validation['violations'])} words** need to be replaced with B2 alternatives:

"""
            for word in sorted(validation['violations']):
                response += f"- `{word}` → [find B2 equivalent]\n"
        else:
            response += """

**No words need replacement** - all vocabulary is B2 compliant!

"""

        # Add B2 Grammar Requirements
        response += f"""

## B2 Grammar Compliance

{self.get_b2_grammar_requirements()}

## Simplification Guidelines

### Vocabulary Requirements
1. **Use only B2-level vocabulary** (5000 most common French words)
2. **Replace complex words** with simpler B2 alternatives
3. **Maintain natural French flow** and readability

### Grammar Requirements
1. **Prioritize essential tenses** (présent, passé composé, imparfait, futur simple, conditionnel)
2. **Simplify complex structures** while preserving meaning
3. **Use appropriate B2-level grammar** patterns

### Text Processing Instructions

**Original text to simplify:**
```
{text}
```

**Required output format:**
1. Provide the simplified French text in Markdown format
2. Highlight words that were replaced with B2 alternatives
3. Add delimiter `---`
5. List any word replacements made (original → replacement)
6. Note any B2-level grammar structures in the output text

---

*This analysis uses lemmatization for accurate vocabulary checking and includes comprehensive B2 compliance guidelines.*"""

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
            description="Analyze and provide B2 simplification guidance for French text. Returns Markdown-formatted report with vocabulary compliance check, word replacement suggestions, and B2 grammar requirements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "French text to analyze and generate B2 simplification guidance for",
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

        # Generate comprehensive B2 analysis with Markdown output
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
