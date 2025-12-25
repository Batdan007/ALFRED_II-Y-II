# Fabric AI Patterns - Usage Guide

Alfred Ultimate now includes **243 expert AI patterns** from the Fabric AI framework!

## What's Included

- **227 Fabric Patterns** from danielmiessler/fabric
- **16 Custom Alfred Patterns** for security, business, and automation
- **Total: 243 patterns** covering every use case

## Pattern Categories

The patterns are organized by tags:

- **SECURITY** - Security analysis, threat modeling, vulnerability scanning
- **DEVELOPMENT** - Code review, debugging, testing, documentation
- **BUSINESS** - Market analysis, strategy, competitive intelligence
- **WRITING** - Content improvement, essays, documentation
- **ANALYSIS** - Data analysis, research, claims verification
- **LEARNING** - Study guides, tutorials, explanations
- **SUMMARIZE** - Content summarization, key points extraction
- **EXTRACT** - Information extraction, pattern recognition
- **And many more!**

## Quick Start

### 1. Test the Pattern System

```bash
python fabric_patterns.py
```

This will show you all 243 loaded patterns organized by category.

### 2. Use with Alfred Enhanced

```python
from alfred_enhanced import AlfredEnhanced

# Initialize Alfred
alfred = AlfredEnhanced()

# Apply a pattern
prompt = alfred.apply_fabric_pattern('extract_wisdom', """
Your input text here...
This could be an article, book excerpt, video transcript, etc.
""")

print(prompt)  # This gives you the formatted prompt ready for AI
```

## Common Use Cases

### Extract Wisdom from Content

```python
text = """
[Paste article, video transcript, or any content here]
"""

prompt = alfred.apply_fabric_pattern('extract_wisdom', text)
# Use this prompt with Claude, GPT, or any AI model
```

### Code Review

```python
code = """
def my_function():
    # Your code here
    pass
"""

prompt = alfred.apply_fabric_pattern('code_review', code)
# Or use custom Alfred pattern:
prompt = alfred.apply_fabric_pattern('review_code', code)
```

### Security Analysis

```python
code_to_scan = """
user_input = request.GET['username']
query = "SELECT * FROM users WHERE username = '" + user_input + "'"
"""

prompt = alfred.apply_fabric_pattern('security_audit', code_to_scan)
```

### Create Summary

```python
article = """
[Long article text...]
"""

prompt = alfred.apply_fabric_pattern('create_summary', article)
```

### Improve Writing

```python
draft = """
Your draft text that needs improvement...
"""

prompt = alfred.apply_fabric_pattern('improve_writing', draft)
```

## Discovering Patterns

### List All Patterns

```python
# List all patterns
all_patterns = alfred.list_fabric_patterns()
print(f"Total patterns: {len(all_patterns)}")

# Filter by tag
security_patterns = alfred.list_fabric_patterns(tag='SECURITY')
print("Security patterns:", security_patterns)

development_patterns = alfred.list_fabric_patterns(tag='DEVELOPMENT')
print("Development patterns:", development_patterns)
```

### Search Patterns

```python
# Search for patterns related to 'code'
code_patterns = alfred.search_fabric_patterns('code')
print("Code-related patterns:", code_patterns)

# Search for patterns related to 'security'
security_patterns = alfred.search_fabric_patterns('security')
print("Security patterns:", security_patterns)
```

### Get Pattern Info

```python
# Get detailed information about a specific pattern
info = alfred.get_fabric_pattern_info('extract_wisdom')
print(info)
```

## Popular Patterns

### Content Analysis
- `extract_wisdom` - Extract insights and wisdom from content
- `analyze_claims` - Fact-check and verify claims
- `rate_content` - Rate content quality
- `create_summary` - Generate comprehensive summaries
- `extract_article_wisdom` - Extract wisdom from articles

### Writing & Communication
- `improve_writing` - Enhance writing quality
- `write_essay` - Generate structured essays
- `create_keynote` - Create presentation outlines
- `create_tweet` - Generate engaging tweets
- `create_linkedin_post` - Professional LinkedIn posts

### Security & Development
- `security_audit` - Comprehensive security analysis
- `code_review` - Professional code review
- `analyze_malware` - Malware behavior analysis
- `create_stride_threat_model` - STRIDE threat modeling
- `write_hackerone_report` - Bug bounty reports

### Business & Strategy
- `market_analysis` - Market opportunity analysis
- `competitive_analysis` - Competition analysis
- `swot_analysis` - SWOT analysis
- `create_business_plan` - Business plan generation
- `create_pitch_deck` - Pitch deck outlines

### Learning & Education
- `create_quiz` - Generate quiz questions
- `study_guide` - Create study guides
- `explain_like_im_5` - Simplify complex topics
- `create_flashcards` - Generate flashcards

### Research & Analysis
- `analyze_paper` - Research paper analysis
- `literature_review` - Create literature reviews
- `extract_predictions` - Extract and analyze predictions
- `find_logical_fallacies` - Identify logical fallacies

## Advanced Usage

### Direct Pattern Access

```python
from fabric_patterns import FabricPatterns

fabric = FabricPatterns()

# Get a specific pattern
pattern = fabric.get_pattern('extract_wisdom')
print(pattern['name'])
print(pattern['description'])
print(pattern['tags'])

# Apply the pattern
prompt = fabric.apply_pattern('extract_wisdom', 'your text')
```

### Filter by Multiple Tags

```python
# Get all security patterns
security_patterns = fabric.get_patterns_by_tag('SECURITY')

for name, pattern in security_patterns.items():
    print(f"{name}: {pattern['description']}")
```

### Get All Available Tags

```python
tags = fabric.get_all_tags()
print("All available tags:", tags)
```

## Pattern Source

The patterns are loaded from:
1. **Primary Source**: `C:/BAT_UBX/Fabric-main/scripts/pattern_descriptions/pattern_descriptions.json`
2. **Fallback**: Embedded popular patterns if JSON not found

All 227 Fabric patterns are sourced from the official [danielmiessler/fabric](https://github.com/danielmiessler/fabric) repository.

## Integration with AI Models

These patterns generate prompts that work with:
- **Claude** (Anthropic)
- **GPT-4** (OpenAI)
- **Groq** (Fast inference)
- **Ollama** (Local models)
- Any other LLM

The patterns are LLM-agnostic - they generate structured prompts that guide any AI to produce high-quality results.

## Example Workflow

```python
# 1. Search for relevant patterns
patterns = alfred.search_fabric_patterns('security')

# 2. Get info about a specific pattern
info = alfred.get_fabric_pattern_info('security_audit')
print(info)

# 3. Apply the pattern to your code
code = open('my_app.py').read()
prompt = alfred.apply_fabric_pattern('security_audit', code)

# 4. Send the prompt to your AI model
# (Integration with Claude/GPT/Groq would go here)
print(prompt)
```

## Benefits

1. **Expert-Crafted Prompts** - Each pattern is designed by experts
2. **Consistency** - Get consistent, high-quality results
3. **Time-Saving** - No need to craft prompts from scratch
4. **Comprehensive** - 243 patterns cover virtually every use case
5. **Flexible** - Works with any LLM or AI model

## Next Steps

1. Run `python fabric_patterns.py` to see all patterns
2. Try applying patterns to your content
3. Integrate with your AI workflows
4. Explore different pattern categories
5. Create custom patterns for your specific needs

---

**Total Patterns: 243**
- Fabric Framework: 227
- Custom Alfred: 16

For more information about the Fabric framework, visit:
https://github.com/danielmiessler/fabric
