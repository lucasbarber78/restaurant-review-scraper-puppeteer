# AI Workflow Guide

This document explains how the AI assistant (Claude) workflow is configured for this project to ensure consistent collaboration.

## Purpose of .claude.json

The `.claude.json` file provides structured instructions for the AI assistant to ensure consistent project management across multiple conversations. It helps maintain a standardized approach to:

- Starting conversations
- Ending conversations
- Following approval rules
- Managing documentation updates
- Adhering to project-specific technical guidelines
- Following the established development workflow

## Conversation Workflow

### Beginning Conversations

When starting a new conversation, Claude will:
1. Read the latest versions of NEXT_STEPS.md and FUTURE_ENHANCEMENTS.md
2. Understand the repository structure and dependencies
3. Summarize the current project status
4. Confirm next steps with you before proceeding
5. Always request a "Yes" before writing any code or making changes

### Project Editing Guidelines

Claude will:
1. Only use GitHub Model Context Protocol tools for making changes to the project
2. Never use the fileserver model context protocol tools unless specifically requested
3. Make all edits directly in the GitHub repository, never to local files
4. This workflow allows you to sync changes from GitHub to your local machine when ready

### Ending Conversations

At the end of every conversation, Claude will ask:
1. If you would like a summary of achievements during the chat
2. What items are still pending
3. What new items need to be added
4. If you want to update the NEXT_STEPS.md or FUTURE_ENHANCEMENTS.md files

## Approval Requirements

Claude will always request explicit approval before:
- Making any code changes
- Updating NEXT_STEPS.md
- Updating FUTURE_ENHANCEMENTS.md
- Making any documentation updates
- Implementing any solution

The approval process requires an explicit "Yes" from you before proceeding with any changes.

## Documentation Guidelines

When updating NEXT_STEPS.md (with approval):
- The "What We've Accomplished" section will be preserved
- Newly completed items will be added to "Recently Completed" with the current date
- The "Current Enhancement" section will be updated with remaining tasks

If a current enhancement is completed, Claude will ask if you want to:
- Select a new enhancement from FUTURE_ENHANCEMENTS.md
- Update NEXT_STEPS.md with detailed implementation steps for the newly selected enhancement

## Project-Specific Guidelines

The .claude.json file includes detailed guidelines for:

### Security Considerations
- Ethical scraping practices
- Secure storage of secrets
- Input validation
- Proper rate limiting
- Security event logging

### Scraping Best Practices
- Anti-bot detection techniques
- Selector strategies
- Error handling
- Browser management
- Proxy rotation implementation
- Puppeteer optimization
- Resource usage monitoring

### API Development
- FastAPI for REST endpoints
- OpenAPI/Swagger documentation
- Pydantic model validation
- HTTP status code usage
- Authentication and authorization

### Error Handling
- Try/except blocks for network operations
- Retry mechanisms
- Graceful handling of site structure changes
- Error logging

## Development Workflow

The .claude.json file outlines the following development phases:

1. **Analysis Phase**
   - Understanding website structure
   - Designing scraping strategies
   - Documenting selectors and extraction patterns
   - Testing for anti-bot detection mechanisms

2. **Implementation Phase**
   - Creating/updating scraper modules
   - Implementing anti-bot evasion techniques
   - Developing data extraction and normalization logic
   - Creating multi-client support systems

3. **Testing Phase**
   - Unit testing components
   - Integration testing for end-to-end scraping
   - Performance testing
   - Detection evasion testing

4. **Documentation Phase**
   - Updating technical documentation
   - Documenting command-line options
   - Creating user guides
   - Documenting anti-bot evasion techniques

5. **Deployment Phase**
   - Creating setup instructions
   - Managing configuration
   - Setting up monitoring and maintenance

## How to Update the .claude.json File

If you need to update the workflow instructions:

1. Edit the `.claude.json` file directly
2. Follow the established JSON structure
3. Commit the changes to the repository

## Structure of .claude.json

The `.claude.json` file uses the following structure:

```json
{
  "projectInstructions": {
    "conversationStart": {
      "requiredFiles": [...],
      "actions": [...]
    },
    "conversationEnd": {
      "requiredQuestions": [...]
    },
    "approvalRules": {
      "requireExplicitApproval": [...],
      "approvalFormat": "..."
    },
    "projectEditing": {
      "toolUsage": {
        "allowedTools": [...],
        "prohibitedTools": [...],
        "editingWorkflow": "..."
      }
    },
    "documentationGuidelines": {
      "nextStepsMd": {
        "preserveSections": [...],
        "updateFormat": {...}
      },
      "completedEnhancement": {
        "askAbout": [...]
      }
    },
    "projectSpecific": {
      "securityConsiderations": [...],
      "scrapingBestPractices": [...],
      "apiDevelopment": [...],
      "errorHandling": [...]
    },
    "developmentWorkflow": {
      "phases": [
        {
          "name": "...",
          "tasks": [...]
        },
        ...
      ]
    }
  }
}
```

This structured format allows for clear guidance and consistent collaboration throughout the development process.