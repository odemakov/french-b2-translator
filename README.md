# French B2 Vocabulary Enforcer MCP Server

A Model Context Protocol (MCP) server that simplifies French text to French B2 level. It enforces strict B2 vocabulary compliance by checking against a 5000-word vocabulary list and providing replacement suggestions for non-B2 words.

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
    "french-b2-simplifier": {
      "command": "/Users/pupkin/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/pupkin/src/french-b2-simplifier",
        "run",
        "french_b2_mcp.py"
      ],
      "env": {}
    }
  }
}
```

## Available Tools

### `simplify_to_french_b2_instructions`
Generates instructions for simplifying French text to B2 level using only vocabulary from the B2 word list.

**Parameters:**
- `text` (required): French text to simplify

**Output:**
Clear instructions for B2-compliant simplification that ensures only B2 vocabulary is used.

### `validate_b2_vocabulary`
Checks if French text uses only B2 vocabulary and provides replacement suggestions for non-B2 words.

**Parameters:**
- `french_text` (required): French text to validate

**Output:**
- Detailed validation report
- List of non-B2 words found
- Suggested B2 replacements

### `fix_b2_vocabulary`
Identifies non-B2 words and provides specific B2 alternatives for replacement.

**Parameters:**
- `french_text` (required): French text with potential non-B2 vocabulary

**Output:**
- List of non-B2 words with suggested B2 replacements
- Instructions for creating B2-compliant text

## Usage Examples

### Simplifying French Text
```
User input: "Dans cet apaisement du soleil absent, toutes les senteurs de la terre se répandaient."

Tool: simplify_to_french_b2_instructions
Output: Instructions to simplify using only B2 vocabulary

Then use: validate_b2_vocabulary
Output: Identifies "apaisement" and "senteurs" as non-B2 words

Then use: fix_b2_vocabulary
Output:
- apaisement -> [find B2 equivalent for 'apaisement']
- senteurs -> [find B2 equivalent for 'senteurs']
```

### Vocabulary Enforcement Workflow
1. Use `simplify_to_french_b2_instructions` to get B2 simplification instructions
2. Apply the simplification to create B2-level text
3. Use `validate_b2_vocabulary` to check compliance
4. Use `fix_b2_vocabulary` to get specific replacements for non-B2 words
5. Revise text using suggested B2 alternatives

## Features

- **Vocabulary Enforcement**: Strict checking against 5000-word B2 vocabulary list
- **Non-B2 Word Detection**: Identifies words not in the B2 vocabulary
- **Practical Workflow**: Three-step process for guaranteed B2 compliance
- **Real Validation**: Uses actual word list checking, not just guidelines
- **Generic Replacement Instructions**: Provides clear guidance for finding B2 alternatives
- **spaCy Integration**: Optional advanced text processing with French language model

## B2 Vocabulary Compliance

The tool ensures:
- **Only B2 words**: Every word checked against the 5000-word vocabulary list
- **Automatic detection**: Identifies non-B2 words requiring replacement
- **Clear instructions**: Provides guidance for finding appropriate B2 alternatives
- **Practical output**: Text that B2 learners can actually understand

## Algorithm
1. **Input**: French text to simplify
2. **Simplify**: Generate B2-level French using clear instructions
3. **Validate**: Check each word against `words.txt` vocabulary list
4. **Replace**: Suggest B2 alternatives for any non-compliant words
5. **Output**: Text using only B2 vocabulary

## Optional spaCy Integration

For enhanced text processing, you can install spaCy with French language model:

```bash
pip install spacy
python -m spacy download fr_core_news_sm
```

This enables more accurate word normalization and lemmatization.

## Troubleshooting

- Ensure Python path is correct in configuration
- Check that `words.txt` exists and is readable
- Verify MCP server is properly registered in AI tool
- Restart AI tool after configuration changes
- For spaCy issues, ensure French model is properly installed