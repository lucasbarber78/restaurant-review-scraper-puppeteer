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

When working with this web scraping project for restaurant reviews:

1. Always be mindful of the sensitivity of website scrapers and anti-bot detection measures
2. Test changes thoroughly in non-headless mode before pushing to production
3. Consider the impact on website performance and avoid overloading sites with requests
   - Implement appropriate delays between requests
   - Use proper throttling techniques
   - Consider the use of rotating proxies for high-volume scraping
4. Maintain backward compatibility with existing data structures
5. Document all scraper interactions and data schema changes clearly
6. When enhancing the anti-bot detection systems, provide examples of expected behavior
7. For GUI improvements, include simple mockups or descriptions of the proposed changes
8. Always follow best practices for scraper design and updates:
   - Use modular code structure for platform-specific scrapers
   - Version scraper components properly
   - Include both modern and legacy selectors where needed
   - Test scrapers thoroughly before deployment
9. Implement proper error handling and retry mechanisms:
   - Use try/except blocks around scraping operations
   - Implement proper exponential backoff for retries
   - Log scraping errors appropriately
   - Handle site structure changes gracefully
10. Follow web scraping best practices:
    - Respect robots.txt when applicable
    - Implement user-agent rotation
    - Use realistic browser fingerprinting
    - Consider session management across requests
    - Limit request rate to avoid IP bans
11. Data Processing:
    - Use consistent date formatting across platforms
    - Implement proper data cleaning and normalization
    - Handle missing or irregular data gracefully
    - Maintain data integrity during export
12. Security considerations:
    - Store API keys and proxies securely
    - Implement secure storage for collected data
    - Sanitize inputs to prevent injection
    - Handle sensitive client information properly

## Development Workflow

1. Analysis phase:
   - Understand the target platform's DOM structure
   - Design scrapers to adapt to changing structures
   - Document selector strategies for each platform
   - Analyze anti-bot detection measures on target sites

2. Implementation phase:
   - Create scraper modules for each platform
   - Implement anti-bot detection countermeasures
   - Develop data processing and normalization
   - Create multi-client handling system

3. Testing phase:
   - Unit tests for individual components
   - Integration tests for full scraping workflow
   - Performance testing with different anti-bot settings
   - Resilience testing with various network conditions

4. Documentation phase:
   - Update technical documentation
   - Document command-line options
   - Create usage guides for different scenarios
   - Document troubleshooting techniques

5. Deployment phase:
   - Setup instructions
   - Configuration templates
   - Monitoring systems for scraper health
   - Maintenance procedures for handling site changes
