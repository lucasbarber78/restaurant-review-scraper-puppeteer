# Claude Memory System

This directory contains the Claude-iterated memory system for the Restaurant Review Scraper project.

## Structure

The memory system is organized into three tiers:

- **Core Memory**: Essential project information (in `/restaurant_review_scraper/core/`)
- **Recall Memory**: Session summaries and decision history (in `/restaurant_review_scraper/recall/`)
- **Archival Memory**: Detailed technical documentation (in `/restaurant_review_scraper/archival/`)

## Memory Index

The `memory_index.json` file provides a structured way to navigate between related documents. It maps:

- Topics to relevant documents
- Documents to metadata and keywords
- Components to their documentation
- Common queries to appropriate documents

## Usage

See the [CLAUDE_MEMORY_GUIDE.md](../CLAUDE_MEMORY_GUIDE.md) in the root directory for detailed instructions on how to use this memory system.