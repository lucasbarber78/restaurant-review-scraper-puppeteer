---
title: "AI Workflow Guidelines"
category: "core"
date_created: "2025-04-27"
last_updated: "2025-04-27"
priority: "high"
---

# AI Workflow Guidelines

## Overview

This document outlines the workflow for using Claude and the Claude-iterated memory system in the Restaurant Review Scraper project. It provides guidelines for effective collaboration, documentation maintenance, and development processes utilizing Claude's capabilities.

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

## Related Documents

- [Project Overview](project_overview.md)
- [Current Status](current_status.md)
- [Claude Memory Guide](../../../CLAUDE_MEMORY_GUIDE.md)
