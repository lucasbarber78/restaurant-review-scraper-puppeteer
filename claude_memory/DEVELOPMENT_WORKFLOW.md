# Claude Memory System Development Workflow

This document explains how to maintain the Claude-iterated memory system during ongoing development of the Restaurant Review Scraper. It provides guidelines for keeping documentation up-to-date, properly cross-referenced, and integrated with the development process.

## Understanding the Memory System

The Claude Memory System is organized into three tiers:

1. **Core Memory**: Essential project information (high-level overview, architecture, requirements)
2. **Recall Memory**: Session summaries and decision history
3. **Archival Memory**: Detailed technical documentation

Each tier serves a different purpose and is maintained in a specific way during development.

## Documentation During Development

### When to Update Documentation

Documentation should be updated at these key points in the development process:

1. **Planning Phase**
   - Update core memory with new requirements
   - Create archival documents for new components or features
   - Document design decisions and trade-offs

2. **Implementation Phase**
   - Create detailed implementation documents in archival memory
   - Update core architecture documents if design changes
   - Document APIs, interfaces, and key components

3. **Testing Phase**
   - Document testing procedures and results
   - Update archival memory with lessons learned
   - Document bug fixes and workarounds

4. **Release Phase**
   - Update the current status document
   - Ensure all documentation is consistent with the final implementation
   - Create a session summary for major releases

### Documentation Workflow for Common Tasks

#### Adding a New Feature

1. **Before Implementation**
   - Update core/requirements.md with new requirements
   - Update core/current_status.md to include the new feature
   - Create archival design documents as needed

2. **During Implementation**
   - Update memory_index.json to reference new documents
   - Create detailed implementation documents in archival memory
   - Create a session summary for significant development sessions

3. **After Implementation**
   - Update core/current_status.md to mark the feature as complete
   - Ensure cross-references between documents are accurate
   - Review and validate all affected documentation

#### Fixing a Bug

1. **Document the Issue**
   - Create an entry in recall memory about the bug
   - Document the root cause analysis

2. **Document the Fix**
   - Update affected archival documents with the solution
   - Document any workarounds or edge cases

3. **Update Status**
   - Update core/current_status.md with the fix
   - Add lessons learned to appropriate archival documents

#### Refactoring Code

1. **Document the Need for Refactoring**
   - Create a session summary explaining the motivation
   - Document the current issues in archival memory

2. **Document the Approach**
   - Update archival documents with the refactoring strategy
   - Document any architectural changes in core memory

3. **After Refactoring**
   - Update all affected documents to reflect the new structure
   - Ensure cross-references remain valid
   - Document performance improvements or other benefits

## Maintaining the Memory Index

The `memory_index.json` file maps topics to relevant documents and should be kept up-to-date during development.

### When to Update the Memory Index

1. **Adding New Documents**
   - Add entries for each new document
   - Include appropriate metadata and keywords
   - Create relationships to existing documents

2. **Modifying Document Content**
   - Update keywords if the document focus changes
   - Adjust relationships if necessary

3. **Reorganizing Documentation**
   - Update all affected document paths
   - Ensure relationships remain valid
   - Adjust component groupings if needed

### Memory Index Structure

Each entry in the memory index should follow this format:

```json
{
  "path": "relative/path/to/document.md",
  "title": "Human-readable title",
  "category": "core|recall|archival",
  "component": "specific-component-name",
  "keywords": ["keyword1", "keyword2"],
  "related_documents": ["path/to/related1.md", "path/to/related2.md"]
}
```

## Working with Claude

Claude is a key partner in maintaining documentation. Here's how to effectively use Claude for documentation:

### Documentation Creation

1. **Request Focused Documents**
   - Ask Claude to create specific documents for new features or components
   - Provide context about the purpose and intended audience

2. **Provide Templates**
   - Use existing documents as templates for consistency
   - Refer Claude to the document structure in CLAUDE_MEMORY_GUIDE.md

3. **Review and Refine**
   - Review Claude-generated documentation for accuracy
   - Provide feedback to improve future documentation

### Documentation Updates

1. **Direct Updates**
   - Ask Claude to update specific documents when implementation details change
   - Specify exactly what needs to be updated

2. **Cross-Reference Maintenance**
   - Ask Claude to check cross-references when documents change
   - Have Claude update memory_index.json as needed

3. **Consistency Checks**
   - Periodically ask Claude to review documentation for consistency
   - Request metadata validation across documents

## Session Summaries

Session summaries in recall memory provide a chronological history of the project. Here's how to maintain them:

### Creating Session Summaries

1. **End of Development Sessions**
   - Create a summary after significant development work
   - Use the session template in recall/session_template.md

2. **Decision Documentation**
   - Document key decisions and their rationale
   - Reference related archival documents

3. **Progress Tracking**
   - Record achievements and progress
   - Document open questions and next steps

### Naming Convention

Session summaries follow this naming pattern:
- `session_YYYY-MM-DD.md` for single sessions in a day
- `session_YYYY-MM-DD_N.md` where N is a number for multiple sessions in one day

## Best Practices

1. **Document as You Go**
   - Don't wait until the end of development to update documentation
   - Document decisions while context is fresh

2. **Maintain Cross-References**
   - Always update related document links when changing content
   - Check memory_index.json for accuracy

3. **Use Consistent Formatting**
   - Follow the templates in the Claude Memory Guide
   - Maintain consistent metadata headers

4. **Keep Documentation Balanced**
   - Core memory should remain high-level and stable
   - Archival memory should contain detailed implementation specifics
   - Recall memory should track the project's evolution

5. **Validate Regularly**
   - Periodically review documentation for accuracy
   - Ask Claude to help identify inconsistencies

## Documentation Maintenance Checklist

Use this checklist when making significant changes:

- [ ] Update relevant core documents
- [ ] Create or update archival documents with implementation details
- [ ] Create a session summary in recall memory
- [ ] Update memory_index.json with any new documents
- [ ] Validate cross-references between documents
- [ ] Check for consistent formatting and metadata
- [ ] Update current_status.md with the latest status

## Related Documents

- [Claude Memory Guide](CLAUDE_MEMORY_GUIDE.md)
- [Migration Tracking](MIGRATION_TRACKING.md)
- [Core Memory README](restaurant_review_scraper/core/README.md)
- [Recall Memory README](restaurant_review_scraper/recall/README.md)
- [Archival Memory README](restaurant_review_scraper/archival/README.md)
