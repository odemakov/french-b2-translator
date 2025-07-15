#!/usr/bin/env python3
"""
French B2 Translation Assistant MCP Server
Provides a simple translation tool that internally uses AI with optimized prompts
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
logger = logging.getLogger("french-b2-translator")

# Add after your existing imports
try:
    import spacy
    nlp = spacy.load("fr_core_news_sm")
    HAS_SPACY = True
except (ImportError, OSError):
    # uv pip install fr_core_news_sm@https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.8.0/fr_core_news_sm-3.8.0-py3-none-any.whl
    logger.warning("spaCy not available")
    HAS_SPACY = False
    nlp = None


def load_b2_vocabulary(vocab_file: str = "words.txt") -> tuple[set, set]:
    """Load the B2 vocabulary list from txt file"""
    try:
        with open(vocab_file, "r", encoding="utf-8") as f:
            original_vocab = {line.strip().lower() for line in f if line.strip()}

            # Create normalized version if spaCy is available
            if HAS_SPACY and nlp:
                normalized_vocab = set()
                for word in original_vocab:
                    doc = nlp(word)
                    if doc:
                        normalized_vocab.add(doc[0].lemma_.lower())
                return original_vocab, normalized_vocab
            return original_vocab, original_vocab
    except FileNotFoundError:
        logger.warning(f"Vocabulary file {vocab_file} not found.")
        return set(), set()


class FrenchB2Translator:
    """French B2 Translation Assistant"""

    def __init__(self):
        self.original_vocab, self.normalized_vocab = load_b2_vocabulary()

    def normalize_french_words(self, text: str) -> set:
        """Extract normalized French words from text"""
        if not HAS_SPACY or not nlp:
            # Fallback to simple tokenization
            words = re.findall(r'\b[a-zA-ZàâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]+\b', text.lower())
            return set(words)

        doc = nlp(text)
        normalized_words = set()

        for token in doc:
            if token.is_alpha and not token.is_stop:
                # Use lemma (base form) of the word
                lemma = token.lemma_.lower()
                normalized_words.add(lemma)

        return normalized_words

    def validate_vocabulary(self, french_text: str) -> dict:
        """Check if translation uses only B2 vocabulary"""
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
2. Use the translation tool to get a B2-compliant version
3. Check if any violations are proper nouns that can be kept as-is
"""
        else:
            report += """## All Clear!
All words in this text are within the B2 vocabulary constraints.
"""

        return report

    def create_translation_prompt(self, text: str) -> str:
        """Create optimized prompt for B2 translation with markdown output"""

        # Use original vocabulary for display (more readable than lemmatized forms)
        vocab_sample = list(self.original_vocab) if self.original_vocab else []
        vocab_info = (
            f"Available B2 vocabulary includes words: {', '.join(vocab_sample[:50])}..."
            if vocab_sample
            else ""
        )

        prompt = f"""You are an experienced French teacher helping students translate texts to French B2 level.

**Text to translate:**
{text}

**Your task:** Translate this to French B2 level and output a markdown file with B2 grammar highlighting.

**Vocabulary Constraints:**
- Use ONLY words from the 5000 most common French words (B2 level)
- If you need a complex concept, use simpler synonyms or explanatory phrases
- Prioritize everyday, concrete vocabulary over specialized terms
{vocab_info}

**Grammar Requirements (B2 Level):**
- Essential tenses: présent, passé composé, imparfait, futur simple, conditionnel
- Use subjunctive only after clear trigger expressions (emotion, doubt, necessity)
- Complex relative pronouns (dont, où, lequel) but keep structure clear
- Varied sentence connectors: parce que, bien que, pour que, afin que

**CRITICAL OUTPUT FORMAT - You must output EXACTLY this markdown structure:**

```markdown
# French B2 Translation

## Translation

[Your French B2 translation here, with B2 grammar elements marked in bold like **[passé composé]**, **[imparfait]**, **[subjonctif]**, **[relative pronoun]**, **[conditionnel]**, etc.]

---

## Simplifications Made

- **Original:** [complex word/phrase] → **B2 Version:** [simpler alternative]
  **Reason:** [why the change was necessary for B2 level]

## Grammar Clarifications

### Passé Composé
[Explain any passé composé usage in the translation, if present]

### Imparfait
[Explain any imparfait usage in the translation, if present]

### Subjonctif
[Explain any subjunctive usage in the translation, if present]

### Relative Pronouns
[Explain any complex relative pronouns (dont, où, lequel) usage, if present]

### Conditionnel
[Explain any conditional usage in the translation, if present]

### Other B2 Grammar
[Any other B2-level grammar points used in the translation]

## Vocabulary Notes

- **[word]:** [simple definition in French] - [usage context]
- **[word]:** [simple definition in French] - [usage context]

## Learning Tips

[Brief tips about the B2 grammar structures used in this translation]
```

**IMPORTANT RULES:**
1. In the translation section, mark ALL B2 grammar with bold brackets
2. Only include clarification sections for grammar actually used in the translation
3. Never ask clarifying questions - always translate/simplify as requested
4. If text is already French: simplify it to B2 level
5. If text is another language: translate it to French B2 level
6. Output the complete markdown file ready to save as .md artifact
7. STRICTLY use only B2 vocabulary - this is MANDATORY
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
        ),
        types.Tool(
            name="validate_b2_vocabulary",
            description="Check if French text uses only B2 vocabulary words and get detailed report",
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

        # Return the prompt that will generate the markdown artifact
        response = f"""Here's the optimized prompt for French B2 translation with markdown output:

{prompt}

---

**This prompt will generate a complete markdown file (.md) with:**
- French B2 translation with **bold grammar highlighting**
- Detailed explanations of B2 grammar used
- Vocabulary notes for difficult words
- Learning tips for B2 students

**The output will be a ready-to-save .md artifact with proper formatting.**

**Vocabulary Status:**
- Loaded {len(translator.original_vocab)} B2 vocabulary words
- Normalization: {'spaCy enabled' if HAS_SPACY else 'Basic tokenization fallback'}"""

        return [types.TextContent(type="text", text=response)]

    elif name == "validate_b2_vocabulary":
        french_text = arguments.get("french_text", "")

        if not french_text.strip():
            return [
                types.TextContent(type="text", text="Please provide French text to validate.")
            ]

        # Generate validation report
        report = translator.create_validation_report(french_text)

        return [types.TextContent(type="text", text=report)]

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
