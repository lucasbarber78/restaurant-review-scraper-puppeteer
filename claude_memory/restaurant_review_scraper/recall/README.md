# Recall Memory

This directory contains session summaries and decision history for the Restaurant Review Scraper project.

## Purpose

Recall memory preserves context between development sessions by storing summaries of conversations, decisions made, and progress achieved. This creates a chronological record of the project's evolution that Claude can reference when needed.

## Contents

- **session_template.md**: Template for creating session summaries
- **session_[DATE].md**: Individual session summaries organized by date

## Usage

At the end of each significant development session, ask Claude to create a session summary. Claude will create a new file in this directory following the format `session_YYYY-MM-DD.md` using the template structure.

When starting a new session, you can ask Claude to review recent session summaries to quickly re-establish context.