---
title: "AI Workflow Guidelines"
category: "core"
date_created: "2025-04-27"
last_updated: "2025-04-27"
priority: "high"
related_documents:
  - "claude_memory/restaurant_review_scraper/core/project_overview.md"
  - "claude_memory/restaurant_review_scraper/core/current_status.md"
  - "claude_memory/CLAUDE_MEMORY_GUIDE.md"
---

# AI Workflow Guidelines

## Overview

This document outlines the workflow for using Claude and the Claude-iterated memory system in the Restaurant Review Scraper project. It provides guidelines for effective collaboration, documentation maintenance, and development processes utilizing Claude's capabilities.

## The .claude.json Configuration

The `.claude.json` file provides structured instructions for the AI assistant to ensure consistent project management across multiple conversations. It helps maintain a standardized approach to:

- Starting conversations
- Ending conversations
- Following approval rules
- Managing documentation updates
- Adhering to project-specific technical guidelines
- Following the established development workflow

### Structure of .claude.json

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

### Updating the .claude.json File

If you need to update the workflow instructions:

1. Edit the `.claude.json` file directly
2. Follow the established JSON structure
3. Commit the changes to the repository

## Collaboration Workflow

### Starting a Development Session

When starting a new development session:

1. **Provide Context**
   ```
   Hi Claude, I'd like to work on the Restaurant Review Scraper project. Let's focus on [specific component/feature]. Could you help me with [specific task]?
   ```

2. **Project Orientation**
   - Ask Claude to review relevant documentation from core and archival memory
   - Request a summary of current status and recent progress
   - Clarify any ambiguities or questions about the documentation

3. **Session Planning**
   - Outline the specific goals for the session
   - Identify which components will be affected
   - Decide on the development approach

### During Development

During the development session:

1. **Code Development**
   - Work collaboratively with Claude on code implementation
   - Use Claude to explain complex concepts or algorithms
   - Ask Claude to suggest implementations for specific features

2. **Documentation-Driven Development**
   - Refer to existing documentation for requirements and specifications
   - Ask Claude to help maintain consistency with established architecture
   - Update documentation as implementation details are clarified

3. **Iterative Refinement**
   - Review and refine code with Claude's assistance
   - Discuss trade-offs and alternatives for implementation approaches
   - Test solutions against requirements and constraints

4. **Proactive Documentation**
   - After implementing significant features or making key decisions, ask Claude to update relevant documentation
   - For longer sessions, Claude may proactively suggest documentation updates at natural breaking points

### Ending a Session

When concluding a development session:

1. **Session Summary**
   ```
   Let's wrap up for today. Could you summarize what we've accomplished, update the relevant documentation, and create a session summary in recall memory?
   ```

2. **Documentation Updates**
   - Ask Claude to identify and update all affected documentation
   - Review proposed changes to ensure accuracy
   - Confirm that the memory index remains consistent

3. **Next Steps Planning**
   - Discuss and document next steps
   - Identify open questions or issues to address in future sessions
   - Set priorities for the next development session

## Approval Requirements

Claude will always request explicit approval before:
- Making any code changes
- Updating NEXT_STEPS.md
- Updating FUTURE_ENHANCEMENTS.md
- Making any documentation updates
- Implementing any solution

The approval process requires an explicit "Yes" from you before proceeding with any changes.

### Project Editing Guidelines

Claude will:
1. Only use GitHub Model Context Protocol tools for making changes to the project
2. Never use the fileserver model context protocol tools unless specifically requested
3. Make all edits directly in the GitHub repository, never to local files
4. This workflow allows you to sync changes from GitHub to your local machine when ready

## Documentation Maintenance

### When to Update Documentation

Documentation should be updated:

1. **When implementing new features**
   - Update requirements to reflect actual implementation
   - Document design decisions and rationale
   - Create or update technical details in archival memory

2. **When making architectural changes**
   - Update architecture documentation in core memory
   - Ensure consistency across related documents
   - Document migration paths or compatibility concerns

3. **When fixing significant bugs**
   - Document the root cause and solution
   - Update related technical documentation
   - Note any implications for other components

4. **At regular milestones**
   - Update current status at the completion of planned milestones
   - Review and refresh all core documentation
   - Ensure recall memory accurately captures project history

### Documentation Update Process

When updating documentation:

1. **Identify affected documents**
   - Use the memory index to find related documents
   - Consider impacts across all three memory tiers

2. **Update in order of specificity**
   - Start with detailed archival memory documents
   - Update relevant recall memory session summaries
   - Refresh core memory documents as needed

3. **Maintain cross-references**
   - Ensure "Related Documents" sections remain accurate
   - Update the memory index if new topics or relationships emerge

4. **Validate documentation**
   - Check for consistency across documents
   - Ensure all metadata is accurate and up-to-date

### NEXT_STEPS.md Updates

When updating NEXT_STEPS.md (with approval):
- The "What We've Accomplished" section will be preserved
- Newly completed items will be added to "Recently Completed" with the current date
- The "Current Enhancement" section will be updated with remaining tasks

If a current enhancement is completed, Claude will ask if you want to:
- Select a new enhancement from FUTURE_ENHANCEMENTS.md
- Update NEXT_STEPS.md with detailed implementation steps for the newly selected enhancement

## Memory Tiers Usage Guidelines

### Core Memory Usage

Core memory documents should:
- Provide high-level information accessible to all team members
- Be updated when there are significant project changes
- Maintain a stable structure with consistent formatting
- Focus on "what" and "why" rather than detailed "how"

### Recall Memory Usage

Recall memory documents should:
- Capture key discussions and decisions chronologically
- Reference specific technical details implemented in each session
- Identify any issues or open questions
- Track the evolution of the project over time

### Archival Memory Usage

Archival memory documents should:
- Contain detailed technical information for specific components
- Include implementation details, algorithms, and techniques
- Be organized by functional area or component
- Contain examples and usage notes where appropriate

## Session Summary Template

Session summaries should follow this structure:

```markdown
---
title: "Session Summary YYYY-MM-DD"
category: "recall"
date_created: "YYYY-MM-DD"
priority: "medium"
---

# Session Summary: YYYY-MM-DD

## Key Points Discussed
- List main topics and areas discussed
- Include important context or constraints

## Decisions Made
- Document specific decisions with rationale
- Note alternatives considered and why they were rejected

## Technical Details
- Record implementation specifics
- Include any algorithms or approaches developed

## Open Questions
- List unresolved questions or issues
- Note areas requiring further research

## Next Steps
- Outline planned next actions
- Set priorities for future work

## Artifacts to Archive
- Identify documents to be created or updated in archival memory
- Specify the appropriate location for each artifact
```

## Project-Specific Development Workflow

The project follows these development phases as outlined in .claude.json:

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

## Specialized Workflows for the Scraper Project

### Selector Development Workflow

When developing selectors for new review sites:

1. **Analysis Phase**
   - Collaboratively analyze the site structure with Claude
   - Document patterns and challenges in archival memory
   - Develop a selector strategy document

2. **Implementation Phase**
   - Implement selectors based on the strategy
   - Test with actual site examples
   - Document selector patterns in archival memory

3. **Maintenance Phase**
   - Track changes to site structure over time
   - Update selectors as needed
   - Document structural changes in recall memory

### Anti-Detection Feature Development

When developing anti-detection features:

1. **Research and Documentation**
   - Document detection mechanisms in archival memory
   - Research countermeasures and approaches
   - Create a strategy document in archival memory

2. **Implementation**
   - Implement countermeasures incrementally
   - Test against detection systems
   - Document implementation details

3. **Ongoing Maintenance**
   - Monitor detection effectiveness
   - Update countermeasures as detection methods evolve
   - Maintain documentation of the arms race

## Project-Specific Technical Guidelines

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

## Related Documents

- [Project Overview](project_overview.md)
- [Current Status](current_status.md)
- [Claude Memory Guide](../../../CLAUDE_MEMORY_GUIDE.md)
