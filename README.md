# French B2 Simplifier MCP Server

A Model Context Protocol (MCP) server that analyzes French text for B2 level compliance and provides comprehensive simplification guidance. It enforces strict B2 vocabulary compliance by checking against a 5000-word vocabulary list, identifies words requiring replacement, and includes B2 grammar requirements in a well-formatted Markdown report.

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

### `simplify_to_french_b2`
Analyzes French text for B2 compliance and provides comprehensive simplification guidance in Markdown format.

**Parameters:**
- `text` (required): French text to analyze for B2 compliance

**Output:**
- **Markdown-formatted report** with proper structure and formatting
- **Vocabulary compliance analysis** with coverage statistics
- **List of words requiring replacement** (original → [find B2 equivalent])
- **B2 Level Grammar Requirements** including essential tenses and advanced grammar
- **Comprehensive simplification guidelines** for vocabulary and grammar
- **Clear instructions** for creating B2-compliant text

**Key Features:**
- Proper `.md` format output
- Shows specific words that need replacement
- Includes complete B2 grammar requirements
- No hardcoded replacements - dynamic analysis only
- Detailed compliance statistics and coverage analysis

## Usage Examples

### Example 1: Text Requiring Simplification
**Input:** "Dans cet apaisement du soleil absent, toutes les senteurs de la terre se répandaient."

**Tool:** `simplify_to_french_b2`

**Output:** Complete Markdown report including:
- NEEDS SIMPLIFICATION status
- 66.7% B2 vocabulary coverage
- 2 words requiring replacement: `apaisement` → [find B2 equivalent], `senteurs` → [find B2 equivalent]
- Full B2 Grammar Requirements section
- Comprehensive simplification guidelines

### Example 2: B2-Compliant Text
**Input:** "Je vais au marché pour acheter du pain et des fruits."

**Tool:** `simplify_to_french_b2`

**Output:** Complete Markdown report showing:
- COMPLIANT status
- 100.0% B2 vocabulary coverage
- No words need replacement
- B2 Grammar Requirements for reference
- Guidelines for maintaining B2 compliance

### Workflow
1. Run `simplify_to_french_b2` with your French text
2. Review the Markdown-formatted analysis report
3. Follow the specific word replacement suggestions
4. Apply B2 grammar requirements as needed
5. Verify compliance with the comprehensive guidelines provided

## Features

- **Markdown Output**: All reports formatted as proper `.md` with clear structure
- **Word Replacement Tracking**: Shows exactly which words need B2 alternatives
- **B2 Grammar Requirements**: Includes complete grammar guidelines in every report
- **Detailed Analytics**: Coverage statistics, compliance status, and word counts
- **Dynamic Analysis**: No hardcoded replacements - analyzes each text individually
- **Vocabulary Enforcement**: Strict checking against 5000-word B2 vocabulary list
- **Precise Detection**: Identifies specific words not in B2 vocabulary using lemmatization
- **spaCy Integration**: Advanced French text processing for accurate analysis
- **Comprehensive Guidelines**: Complete simplification instructions for vocabulary and grammar

## Enhanced B2 Compliance Features

The tool provides:
- **Markdown Reports**: Structured, readable output in `.md` format
- **Word Replacement Lists**: Specific words needing B2 alternatives (e.g., `apaisement` → [find B2 equivalent])
- **Grammar Requirements**: Complete B2 grammar guidelines included in every report
- **Compliance Analytics**: Coverage percentages, word counts, and status indicators
- **Zero Hardcoded Replacements**: Dynamic analysis based on actual vocabulary checking
- **Comprehensive Validation**: Every word checked against 5000-word B2 vocabulary
- **Lemmatization Support**: Accurate word form recognition using spaCy
- **Educational Content**: B2 grammar requirements for learning reference

## Enhanced Algorithm
1. **Input**: French text for B2 analysis
2. **Vocabulary Analysis**: Check each word against 5000-word B2 vocabulary using lemmatization
3. **Compliance Report**: Generate detailed Markdown report with:
   - Original text display
   - Coverage statistics and compliance status
   - Specific words requiring replacement (no hardcoded suggestions)
   - Complete B2 Grammar Requirements section
   - Comprehensive simplification guidelines
4. **Output**: Well-structured `.md` report with actionable guidance
5. **Result**: Clear roadmap for achieving B2 compliance with specific word targets

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
