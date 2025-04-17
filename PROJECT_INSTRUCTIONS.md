# Working with the Restaurant Review Scraper Puppeteer Project

## Conversation Workflow Guidelines

### Beginning Our Conversation
- Always ask for a "Yes" from me before writing any code or making any changes to my Github repos.
- Please use your Github Model Context Protocol whenever needed.
- When we begin a new chat always make sure to understand structure and dependencies of repo "https://github.com/lucasbarber78/restaurant-review-scraper-puppeteer".
- Read NEXT_STEPS.md "https://github.com/lucasbarber78/restaurant-review-scraper-puppeteer/blob/main/NEXT_STEPS.md" to understand our current enhancement focus and immediate implementation tasks. Please provide all text exactly as written in the file but don't include code artifacts. Instead, just call out if they do exist.
- Read FUTURE_ENHANCEMENTS.md "https://github.com/lucasbarber78/restaurant-review-scraper-puppeteer/blob/main/FUTURE_ENHANCEMENTS.md" to understand the broader enhancement areas we're considering for future work. This context helps ensure our current work aligns with our long-term goals.
- Make sure to confirm next steps with me and make sure that we want to work on them in a given chat. I might have something else planned.

### Project Editing Guidelines
- Only use GitHub Model Context Protocol tools for making any changes to the project
- Never use the fileserver model context protocol tools unless specifically requested
- Make all edits directly in the GitHub repository, never to local files
- This allows me to sync changes from GitHub to my local machine when ready

### Actions Requiring Explicit Approval
- **NEVER** update NEXT_STEPS.md or FUTURE_ENHANCEMENTS.md without my explicit approval, even if it seems like a minor or obvious change.
- Always ask for explicit approval before implementing any solution or making code changes.
- Do not suggest or make updates to documentation files without specific permission.

### Ending Our Conversation
- At the end of each chat, even if I try to end the conversation without mentioning updates, please ask me:
  - If I'd like a summary of what we have achieved in the chat
  - What items are still pending
  - What new items we need to add
  - If I want to update the NEXT_STEPS.md or FUTURE_ENHANCEMENTS.md files

### Documentation Update Guidelines
If I do approve updates to documentation files, follow these guidelines:

For updating NEXT_STEPS.md:
- Don't overwrite the "What We've Accomplished" section
- Add newly accomplished items to "Recently Completed" with the current date
- Update the "Current Enhancement" section with remaining tasks

If we've completed the current enhancement in NEXT_STEPS.md, ask if I want to:
- Select a new enhancement from FUTURE_ENHANCEMENTS.md
- Update NEXT_STEPS.md with detailed implementation steps for the newly selected enhancement

Always maintain this separation between immediate tasks (NEXT_STEPS.md) and future strategic enhancements (FUTURE_ENHANCEMENTS.md).

## Specific to This Project

When working with this Restaurant Review Scraper Puppeteer project:

1. Always be mindful of anti-bot detection mechanisms and legal compliance
2. Test changes thoroughly before pushing to production
3. Consider the impact on scraping performance and reliability
   - Implement appropriate delays between requests
   - Use stealth plugins to avoid detection
   - Consider rotating user agents and proxies
4. Maintain backward compatibility with existing data structures
5. Document all scraper interactions and data extraction patterns clearly
6. When enhancing the anti-bot detection, provide examples of evasion techniques used
7. For GUI improvements, include simple mockups or descriptions of the proposed changes
8. Always follow best practices for web scraping:
   - Use ethical scraping practices
   - Respect robots.txt
   - Implement proper rate limiting
   - Test on small samples before running large scrapes
9. Implement proper error handling and recovery:
   - Use try/except blocks around network operations
   - Implement retry mechanisms
   - Handle site structure changes gracefully
   - Log errors appropriately
10. Follow Puppeteer best practices:
    - Use appropriate selectors (prefer data attributes over CSS classes)
    - Implement proper page lifecycle management
    - Minimize resource usage
    - Handle browser crashes and restarts
11. API Development:
    - Use FastAPI for any REST API endpoints
    - Document all endpoints with OpenAPI/Swagger
    - Implement proper validation using Pydantic models
    - Use appropriate HTTP status codes
    - Implement proper authentication and authorization
12. Security considerations:
    - Store secrets securely (use environment variables or secure vaults)
    - Implement input validation
    - Use parameterized queries for any database interactions
    - Implement proper authentication for API access
    - Log security-relevant events

## Development Workflow

1. Analysis phase:
   - Understand the structure of review platforms
   - Design scraping strategies
   - Document selectors and extraction patterns
   - Test for anti-bot detection mechanisms

2. Implementation phase:
   - Create or update scraper modules
   - Implement anti-bot evasion techniques
   - Develop data extraction and normalization logic
   - Create multi-client support systems

3. Testing phase:
   - Unit tests for individual components
   - Integration tests for end-to-end scraping
   - Performance testing
   - Detection evasion testing

4. Documentation phase:
   - Update technical documentation
   - Document command-line options
   - Create user guides
   - Document anti-bot evasion techniques

5. Deployment phase:
   - Setup instructions
   - Configuration management
   - Monitoring and maintenance
