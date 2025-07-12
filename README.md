# French B2 Prompt Generator MCP Server

A Model Context Protocol (MCP) server that generates optimized prompts for AI translation to French B2 level. Instead of doing translation itself, it creates detailed prompts that help AI systems produce better B2-level French translations.

## Installation

### 1. Install Dependencies

```bash
pip install mcp
```

### 2. Save the Server Code

Save the Python code as `french_b2_mcp.py` and make it executable:

```bash
chmod +x french_b2_mcp.py
```

### 3. Add Vocabulary File

Ensure you have `words.txt` in the same directory (the 5000 most common French words).

### 4. Configure Claude Desktop

Add to your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "french-b2-translator": {
      "command": "/Users/pupkin/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/pupkin/src/french-b2-translator",
        "run",
        "french_b2_mcp.py"
      ],
      "env": {}
    }
  }
}
```

## Available Tools

### `translate_to_french_b2`
Simple tool that translates any text to French B2 level with explanations.

**Parameters:**
- `text` (required): Text to translate (any language)

**Output:**
- French B2 translation
- Simplifications made (complex → simple words)
- Grammar teaching points for B2 learners
- Explanations for difficult vocabulary

## Usage Examples

### Simple Translation
```
User input: "Dans cet apaisement du soleil absent, toutes les senteurs de la terre se répandaient."

Tool: translate_to_french_b2
Output:
- French B2 Translation: "Dans le calme du soir sans soleil, toutes les odeurs de la terre se répandaient."
- Simplifications: apaisement → calme, senteurs → odeurs
- Grammar Points: imparfait used for ongoing description
- Difficult Words: répandaient - to spread out, scatter
```

### From Any Language
```
User input: "The stars were shining brightly in the clear night sky."

Tool: translate_to_french_b2
Output:
- French B2 Translation: "Les étoiles brillaient fort dans le ciel clair de la nuit."
- Grammar Points: imparfait for ongoing past action
- Vocabulary: All words within B2 level
```

## Features

- **Prompt Generation**: Creates optimized prompts for AI translation tasks
- **B2 Guidelines**: Provides comprehensive French B2 level constraints
- **Multiple Prompt Types**: Translation, vocabulary analysis, simplification
- **Educational Focus**: Designed for B2 language learning
- **Context Awareness**: Incorporates specific translation contexts

## B2 Level Focus

The translator ensures:
- Essential tenses: présent, passé composé, imparfait, futur simple
- Intermediate grammar: subjunctive, relative pronouns, passive voice
- Clear sentence structure with appropriate connectors
- Natural but accessible French expression

## Troubleshooting

- Ensure Python path is correct in configuration
- Check that `words.txt` exists and is readable
- Verify MCP server is properly registered in AI tool
- Restart AI tool after configuration changes
