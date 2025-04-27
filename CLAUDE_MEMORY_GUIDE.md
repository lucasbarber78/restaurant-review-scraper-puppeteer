# Claude-Iterated Memory System Guide for Restaurant Review Scraper

This guide explains how to use the Claude-iterated memory system for the Restaurant Review Scraper project.

## Overview

Unlike traditional documentation approaches that require manual updates and maintenance, the Claude-iterated memory system leverages Claude's ability to:

1. Understand your project's structure and documentation needs
2. Update documentation as part of the development process
3. Maintain consistency across documentation tiers without complex scripts
4. Reference and retrieve relevant information when needed

## Memory Structure

The memory system uses a three-tiered architecture:

- **Core Memory**: Essential project information that provides high-level context
- **Recall Memory**: Session summaries and decision history
- **Archival Memory**: Detailed technical documentation organized by component

### Core Memory

Core memory contains essential information that Claude should always have accessible. This includes:

- Project overview and goals
- System architecture
- Key requirements
- Current status and priorities
- Team workflow guidelines

Core memory files use a simple metadata header and standardized format:

```markdown
---
title: "Document Title"
category: "core"
date_created: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
priority: "high"
---

# Document Title

## Overview
Brief description of the document's purpose

## Content
Main content goes here

## Related Documents
- [Link to related document 1]
- [Link to related document 2]
```

### Recall Memory

Recall memory stores summaries of project conversations and decisions. After each session, Claude can create a session summary following this template:

```markdown
---
title: "Session Summary YYYY-MM-DD"
category: "recall"
date_created: "YYYY-MM-DD"
priority: "medium"
---

# Session Summary: YYYY-MM-DD

## Key Points Discussed
- Point 1
- Point 2
- Point 3

## Decisions Made
- Decision 1
- Decision 2

## Technical Details
- Detail 1
- Detail 2

## Open Questions
- Question 1
- Question 2

## Next Steps
- Step 1
- Step 2

## Artifacts to Archive
- Artifact 1 - Should be stored in [category]
- Artifact 2 - Should be stored in [category]
```

### Archival Memory

Archival memory contains detailed technical documentation organized by component or category:

```markdown
---
title: "Component/Feature Name"
category: "archival/category"
date_created: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
priority: "medium"
components: ["component1", "component2"]
---

# Component/Feature Name

## Purpose
Brief description of the component's purpose

## Implementation Details
Technical details about implementation

## API/Interface
Description of the component's interface

## Dependencies
List of dependencies

## Examples
Usage examples

## Notes
Additional notes, considerations, or warnings

## Related Components
- [Link to related component 1]
- [Link to related component 2]
```

## Memory Index

The memory index (`claude_memory/memory_index.json`) provides a structured way for Claude to find relevant information. It maps:

1. **Topics**: Conceptual areas like "scraping" or "anti-bot measures"
2. **Paths**: Document locations and metadata
3. **Components**: Technical components that span multiple documents
4. **Queries**: Common information needs mapped to relevant documents

This allows Claude to quickly locate relevant information and provide comprehensive answers.

## Workflow

### Development Workflow

1. **Development with Documentation Updates**:
   - Claude assists with both code development and documentation
   - As code is developed, Claude updates corresponding documentation
   - Claude ensures consistency between code and documentation

2. **Starting a Session**:
   - Begin each session by providing context about which area of the project you're working on
   - Claude will reference relevant documentation from the appropriate memory tiers

3. **Ending a Session**:
   - Ask Claude to summarize the session
   - Claude will prepare a session summary for recall memory
   - Claude will identify and update any technical documentation that needs modification

4. **Finding Information**:
   - Ask Claude about specific components, features, or decisions
   - Claude will reference the appropriate memory documents

### Workflow Examples

#### Example 1: Starting a New Project

**User:**
```
Hi Claude, I'd like to work on the restaurant review scraper project. I want to implement a new feature for handling paginated review lists. Could you help me with that?
```

**Claude:**
```
I'd be happy to help you implement a feature for handling paginated review lists. Let me check our current documentation to provide the right context.

From our core memory, I can see that our architecture currently supports basic review extraction, but pagination handling needs improvement. Let me share the relevant information from our documentation:

[Claude references core/architecture.md and other relevant docs]

Based on this information, we should approach the pagination feature in the following way...

[Claude then provides specific guidance based on the project's documentation]
```

#### Example 2: Session Documentation

**User:**
```
We've finished implementing the proxy rotation feature. The code now supports automatic rotation of proxies based on request count and error rates. Can you update our documentation to reflect these changes?
```

**Claude:**
```
I'll update the documentation to reflect the completed proxy rotation feature. Let me handle that for you:

1. First, I'll update the current status in core memory:
[Claude updates core/current_status.md to reflect completion of proxy rotation]

2. Next, I'll create or update the archival documentation for proxy management:
[Claude creates/updates archival/implementation/proxy_management.md with the new details]

3. Finally, I'll create a session summary for today's work:
[Claude creates a new session summary in recall memory]

All documentation has been updated. The proxy rotation feature is now fully documented across all relevant memory tiers.
```

## Conversation Starters

To start a productive session with Claude:

```
Hi Claude, I'd like to work on the restaurant review scraper project. Could you first review the core documents to understand the project structure, and then help me with [specific task]?
```

```
Claude, let's continue working on the restaurant review scraper. We were last working on [feature/component]. Could you summarize what we've done so far and what our next steps should be?
```

### Ending Conversations

To end a session effectively:

```
Let's wrap up for now. Could you summarize what we've accomplished in this session, update the relevant documentation, and create a session summary in recall memory?
```

```
Before we finish, could you identify any documentation that needs updating based on today's work?
```

## Customizing the Memory System

To adapt the memory system for specific project needs:

1. Update the core memory files with your project details
2. Customize the archival memory categories based on your project's components
3. Modify the memory index to reflect your project's topics and organization

## Proactive Documentation

During longer development sessions, Claude should proactively update documentation at appropriate moments:

### Time-Based Triggers

After approximately 30-45 minutes of continuous development discussion, Claude can proactively suggest:

```
Before we continue, I'd like to update the documentation based on our discussion so far. I'll create interim documentation to capture our progress. This will take just a moment...

[Claude updates relevant documentation]

Now we can continue with [next development task].
```

### Milestone-Based Triggers

When significant development milestones are reached, such as completing a feature or making a key decision:

```
Great! Now that we've completed [milestone], let me update the documentation to reflect this achievement. I'll update:

1. [specific document 1]
2. [specific document 2]

[Claude updates the documents]

Documentation updated. What would you like to work on next?
```

### Context Shift Triggers

When moving from one development area to another:

```
I notice we're shifting from [previous area] to [new area]. Before we make this transition, let me update the documentation for [previous area]. This will ensure we don't lose any important details.

[Claude updates relevant documentation]

Now we can focus on [new area]. Let me check the existing documentation on this topic to provide the relevant context.
```

## Best Practices

1. **Use Consistent Document Formatting**: Follow the provided templates for consistency
2. **Maintain Clear Categories**: Organize archival memory into logical categories
3. **Update the Memory Index**: Ensure the index reflects your project's organization
4. **Prioritize Information**: Use the priority field to indicate importance
5. **Include Metadata**: Always include the metadata header in documents
6. **Cross-Reference Documents**: Link related documents to create a knowledge network
7. **Regularly Review Core Memory**: Keep the high-level documents up to date

## Advantages Over Manual Documentation

1. **Simpler**: No need for dedicated documentation time separated from development
2. **More intuitive**: Documentation updates happen as part of the natural development conversation
3. **Consistent**: Claude ensures documentation follows templates and maintains consistency
4. **Contextual**: Claude understands the project holistically and can make connections between components
5. **Adaptive**: Documentation can evolve based on project needs
6. **Evolutionary**: The system improves over time through natural use

## Restaurant Review Scraper Specific Adaptations

The memory system for this project includes specialized categories for:

1. **Scraping Strategies**: Documentation on how to extract data from different review sites
2. **Anti-Bot Measures**: Techniques for avoiding detection while scraping
3. **Data Processing**: How review data is cleaned and structured
4. **Proxy Management**: Configuration and rotation of proxies

These specialized categories ensure that the documentation reflects the unique aspects of a restaurant review scraper project while maintaining the benefits of the three-tier memory architecture.
