#!/usr/bin/env python3
"""
French B2 Simplifier Assistant MCP Server
Simplifies text to French B2 level and enforces B2 vocabulary compliance
"""

import asyncio
import logging

import mcp.server.stdio
import mcp.types as types
import spacy
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("french-b2-simplifier")

nlp = spacy.load("fr_core_news_sm")


def load_b2_vocabulary(vocab_file: str = "words.txt") -> tuple[set, dict]:
    """Load the B2 vocabulary list from txt file and lemmatize all words
    Returns: (vocabulary_set, word_position_dict)
    """
    try:
        with open(vocab_file, "r", encoding="utf-8") as f:
            raw_words = [line.strip().lower() for line in f if line.strip()]

        # Lemmatize all vocabulary words for consistent comparison
        lemmatized_vocab = set()
        word_positions = {}  # Maps lemmatized word to its position in the file

        for position, word in enumerate(raw_words):
            doc = nlp(word)
            if doc:
                lemma = doc[0].lemma_.lower()
                lemmatized_vocab.add(lemma)
                # Also keep the original word in case lemmatization changes it unexpectedly
                lemmatized_vocab.add(word)

                # Store position for both lemma and original word
                word_positions[lemma] = position
                word_positions[word] = position

        return lemmatized_vocab, word_positions
    except FileNotFoundError:
        logger.warning(f"Vocabulary file {vocab_file} not found.")
        return set(), {}


class FrenchB2Simplifier:
    """French B2 Simplifier Assistant"""

    def __init__(self):
        self.b2_vocab, self.word_positions = load_b2_vocabulary()

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
        violations = set()
        all_words = set()

        for token in doc:
            if token.is_alpha and not token.is_stop:
                original_word = token.text.lower()
                lemma_word = token.lemma_.lower()
                all_words.add(original_word)

                # Check if lemmatized word is in our lemmatized vocabulary
                if lemma_word not in self.b2_vocab:
                    violations.add(original_word)

        return {
            "is_valid": len(violations) == 0,
            "violations": list(violations),
            "total_unique_words": len(all_words),
            "coverage": (len(all_words) - len(violations)) / len(all_words) * 100
            if all_words
            else 0,
        }

    def create_validation_report(self, french_text: str) -> str:
        """Create a detailed validation report"""
        validation = self.validate_vocabulary(french_text)

        report = f"""# B2 Vocabulary Validation Report

## Text Analysis
- **Total unique words:** {validation["total_unique_words"]}
- **B2 vocabulary coverage:** {validation["coverage"]:.1f}%
- **Validation status:** {"PASSED" if validation["is_valid"] else "FAILED"}

## Text Analyzed
{french_text}

"""

        if validation["violations"]:
            report += f"""## Vocabulary Violations ({len(validation["violations"])} words)
The following words are NOT in the B2 vocabulary list:

"""
            for word in sorted(validation["violations"]):
                report += f"- **{word}**\n"

            report += """
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

    def get_highlighted_text(self, text: str, start_highlight_from: int = 3000) -> str:
        """
        Return text with words highlighted based on their frequency position
        Words from start_highlight_from to 5000 are highlighted with **bold**
        """
        doc = nlp(text)
        result = ""

        for token in doc:
            # Add any whitespace before the token
            if token.i > 0:
                # Get the space between previous token and current token
                prev_token = doc[token.i - 1]
                space_between = text[prev_token.idx + len(prev_token.text) : token.idx]
                result += space_between

            token_text = token.text

            if token.is_alpha and not token.is_stop:
                lemma = token.lemma_.lower()
                original_word = token.text.lower()

                # Check if word should be highlighted based on position
                position = self.word_positions.get(lemma) or self.word_positions.get(
                    original_word
                )

                if position is not None and start_highlight_from <= position < 5000:
                    result += f"**{token_text}**"
                else:
                    result += token_text
            else:
                result += token_text

        return result

    def simplify_to_b2(self, text: str, start_highlight_from: int = 3000) -> str:
        """
        Main function to simplify text to B2 level
        Returns the simplified text with highlighting as the main output
        """
        # First, validate the original text
        validation = self.validate_vocabulary(text)

        # Get highlighted text (this represents the simplified version with difficulty highlighting)
        simplified_text = self.get_highlighted_text(text, start_highlight_from)

        # Build the main response with simplified text first
        response = f"""## Simplified French Text (B2 Level)

{simplified_text}

---

## Word Replacements Made
"""

        if validation["violations"]:
            response += f"""
The following {len(validation["violations"])} words were identified for replacement:

"""
            for word in sorted(validation["violations"]):
                response += f"- `{word}` → [needs B2 equivalent]\n"
        else:
            response += """
No word replacements needed - all vocabulary is B2 compliant!
"""

        response += f"""

## B2 Grammar Structures Used

**Essential B2 tenses** (présent, passé composé, imparfait, futur simple, conditionnel)
**Simple sentence structures** appropriate for B2 level
**Clear logical connectors** for B2 comprehension

## Analysis Details

- **Vocabulary Status:** {"COMPLIANT" if validation["is_valid"] else "NEEDS ATTENTION"}
- **Coverage:** {validation["coverage"]:.1f}% B2 vocabulary
- **Difficult words highlighted:** Words from position {start_highlight_from}-5000 are **bold**

# Required output format

1. Provide the simplified French text with highlighted words in markdown format.
2. Add delimiter `---`
3. List any word replacements made (original → replacement)
4. Add delimiter `---`
5. Note any B2-level grammar structures used in the output text"""

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
            description="Simplify French text to B2 level with difficulty highlighting. Returns the simplified text with word replacements and B2 grammar structures as main output.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "French text to analyze and generate B2 simplification guidance for",
                    },
                    "start_highlight_from": {
                        "type": "integer",
                        "description": "Position in vocabulary list to start highlighting from (0-5000). Words from this position to 5000 will be highlighted as potentially difficult. Default is 3000.",
                        "minimum": 0,
                        "maximum": 5000,
                        "default": 3000,
                    },
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
        start_highlight_from = arguments.get("start_highlight_from", 3000)

        if not text.strip():
            return [
                types.TextContent(type="text", text="Please provide text to simplify.")
            ]

        # Generate comprehensive B2 analysis with Markdown output
        response = simplifier.simplify_to_b2(text, start_highlight_from)

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
