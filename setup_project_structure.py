#!/usr/bin/env python3
"""
Project Structure Setup Tool

This script creates project instruction structure files for GitHub repositories,
using an interactive approach with configuration saving capabilities.
"""

import os
import json
import yaml
import argparse
import datetime
import inquirer
from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Setup Jinja2 environment for templates
TEMPLATE_DIR = Path(__file__).parent / "templates"
TEMPLATE_DIR.mkdir(exist_ok=True)

env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"])
)

# Default templates will be created if they don't exist
DEFAULT_TEMPLATES = {
    "PROJECT_INSTRUCTIONS.md.j2": """# Working with the {{ project_name }} Project

## Conversation Workflow Guidelines

### Beginning Our Conversation
- Always ask for a "Yes" from me before writing any code or making any changes to my Github repos.
- Please use your Github Model Context Protocol whenever needed.
- When we begin a new chat always make sure to understand structure and dependencies of repo "https://github.com/{{ github_username }}/{{ repo_name }}".
- Read NEXT_STEPS.md "https://github.com/{{ github_username }}/{{ repo_name }}/blob/main/NEXT_STEPS.md" to understand our current enhancement focus and immediate implementation tasks. Please provide all text exactly as written in the file but don't include code artifacts. Instead, just call out if they do exist.
- Read FUTURE_ENHANCEMENTS.md "https://github.com/{{ github_username }}/{{ repo_name }}/blob/main/FUTURE_ENHANCEMENTS.md" to understand the broader enhancement areas we're considering for future work. This context helps ensure our current work aligns with our long-term goals.
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

When working with this {{ project_name }} project:

{% for guideline in project_specific_guidelines %}
{{ loop.index }}. {{ guideline }}
{% endfor %}

## Development Workflow

{% for phase in development_workflow %}
{{ loop.index }}. **{{ phase.name }}**:
{% for task in phase.tasks %}
   - {{ task }}
{% endfor %}

{% endfor %}
""",
    "AI_WORKFLOW_GUIDE.md.j2": """# AI Workflow Guide

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

{% for category in project_specific_categories %}
### {{ category.name }}
{% for item in category.items %}
- {{ item }}
{% endfor %}

{% endfor %}

## Development Workflow

The .claude.json file outlines the following development phases:

{% for phase in development_workflow %}
{{ loop.index }}. **{{ phase.name }}**
   {% for task in phase.tasks %}
   - {{ task }}
   {% endfor %}

{% endfor %}

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
      {% for category in project_specific_categories %}
      "{{ category.id }}": [...],
      {% endfor %}
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
""",
    ".claude.json.j2": """{
  "projectInstructions": {
    "conversationStart": {
      "requiredFiles": [
        "NEXT_STEPS.md",
        "FUTURE_ENHANCEMENTS.md"
      ],
      "actions": [
        "Understand repository structure and dependencies",
        "Summarize current project status",
        "Confirm next steps with human",
        "Never proceed with code writing or changes without getting an explicit 'Yes' approval"
      ]
    },
    "conversationEnd": {
      "requiredQuestions": [
        "Would you like a summary of what we have achieved in this chat?",
        "What items are still pending?",
        "What new items do we need to add?",
        "Do you want to update the NEXT_STEPS.md or FUTURE_ENHANCEMENTS.md files?"
      ]
    },
    "approvalRules": {
      "requireExplicitApproval": [
        "Any code changes",
        "Updates to NEXT_STEPS.md",
        "Updates to FUTURE_ENHANCEMENTS.md",
        "Any documentation updates",
        "Any solution implementation"
      ],
      "approvalFormat": "Must explicitly ask for a 'Yes' before proceeding with any changes"
    },
    "documentationGuidelines": {
      "nextStepsMd": {
        "preserveSections": ["What We've Accomplished"],
        "updateFormat": {
          "recentlyCompleted": "- YYYY-MM-DD: Item description",
          "currentEnhancement": "List of remaining tasks"
        }
      },
      "completedEnhancement": {
        "askAbout": [
          "Selecting a new enhancement from FUTURE_ENHANCEMENTS.md",
          "Updating NEXT_STEPS.md with detailed implementation steps for the newly selected enhancement"
        ]
      }
    },
    "projectEditing": {
      "toolUsage": {
        "allowedTools": [
          "GitHub Model Context Protocol tools only"
        ],
        "prohibitedTools": [
          "fileserver model context protocol"
        ],
        "editingWorkflow": "All edits must be made directly in GitHub repository, never to local files",
        "rationale": "This allows the user to sync changes from GitHub to local machine when ready"
      }
    },
    "projectSpecific": {
      {% for category in project_specific_categories %}
      "{{ category.id }}": [
        {% for item in category.items %}
        "{{ item }}"{% if not loop.last %},{% endif %}
        {% endfor %}
      ]{% if not loop.last %},{% endif %}
      {% endfor %}
    },
    "developmentWorkflow": {
      "phases": [
        {% for phase in development_workflow %}
        {
          "name": "{{ phase.name }}",
          "tasks": [
            {% for task in phase.tasks %}
            "{{ task }}"{% if not loop.last %},{% endif %}
            {% endfor %}
          ]
        }{% if not loop.last %},{% endif %}
        {% endfor %}
      ]
    }
  }
}
""",
    "NEXT_STEPS.md.j2": """# Next Steps for {{ project_name }}

## What We've Accomplished

{{ what_weve_accomplished }}

## Recently Completed

- {{ today_date }}: Set up project instruction and AI workflow structure
{% for item in recently_completed %}
- {{ item }}
{% endfor %}

## Current Enhancement: {{ current_enhancement.name }}

Our current focus is on {{ current_enhancement.description }}. This involves:

{% for task in current_enhancement.tasks %}
- {{ "[x]" if task.completed else "[ ]" }} {{ task.description }}
{% endfor %}

### Tasks in Progress

{% for idx, task in enumerate(current_enhancement.in_progress, 1) %}
{{ idx }}. {{ task }}
{% endfor %}

### Next Focus: {{ current_enhancement.next_focus.name }}

In our next session, we will focus specifically on {{ current_enhancement.next_focus.description }}. Steps include:

{% for idx, step in enumerate(current_enhancement.next_focus.steps, 1) %}
{{ idx }}. {{ step }}
{% endfor %}

### Future Actions

Once we complete {{ current_enhancement.name | lower }}:

{% for idx, action in enumerate(current_enhancement.future_actions, 1) %}
{{ idx }}. {{ action }}
{% endfor %}
""",
    "FUTURE_ENHANCEMENTS.md.j2": """# Future Enhancements for {{ project_name }}

This document outlines strategic enhancements for future development of the {{ project_name }}. These are larger features that require significant planning and development.

{% for enhancement in future_enhancements %}
## {{ loop.index }}. {{ enhancement.name }}

{{ enhancement.description }}

**Potential Features:**
{% for feature in enhancement.features %}
- {{ feature }}
{% endfor %}

**Benefits:**
{% for benefit in enhancement.benefits %}
- {{ benefit }}
{% endfor %}

{% endfor %}
"""
}

# Project type specific templates
PROJECT_TYPES = {
    "web_scraper": {
        "specific_categories": [
            {
                "id": "securityConsiderations",
                "name": "Security Considerations",
                "items": [
                    "Follow ethical scraping practices",
                    "Respect robots.txt and site terms of service",
                    "Store secrets securely (use environment variables or secure vaults)",
                    "Implement proper rate limiting to avoid overloading sites",
                    "Log security-relevant events"
                ]
            },
            {
                "id": "scrapingBestPractices",
                "name": "Scraping Best Practices",
                "items": [
                    "Use appropriate selectors (prefer data attributes over CSS classes)",
                    "Implement random delays between requests",
                    "Use stealth plugins to avoid detection",
                    "Consider rotating user agents and proxies",
                    "Use proper page lifecycle management",
                    "Minimize resource usage",
                    "Handle browser crashes and restarts",
                    "Test on small samples before running large scrapes"
                ]
            },
            {
                "id": "apiDevelopment",
                "name": "API Development",
                "items": [
                    "Use FastAPI for all REST API endpoints",
                    "Document all endpoints with OpenAPI/Swagger",
                    "Implement proper validation using Pydantic models",
                    "Use appropriate HTTP status codes",
                    "Implement proper authentication and authorization"
                ]
            },
            {
                "id": "errorHandling",
                "name": "Error Handling",
                "items": [
                    "Use try/except blocks around network operations",
                    "Implement retry mechanisms",
                    "Handle site structure changes gracefully",
                    "Log errors appropriately"
                ]
            }
        ],
        "development_workflow": [
            {
                "name": "Analysis phase",
                "tasks": [
                    "Understand the structure of websites to be scraped",
                    "Design scraping strategies",
                    "Document selectors and extraction patterns",
                    "Test for anti-bot detection mechanisms"
                ]
            },
            {
                "name": "Implementation phase",
                "tasks": [
                    "Create or update scraper modules",
                    "Implement anti-bot evasion techniques",
                    "Develop data extraction and normalization logic",
                    "Create storage and export mechanisms"
                ]
            },
            {
                "name": "Testing phase",
                "tasks": [
                    "Unit tests for individual components",
                    "Integration tests for end-to-end scraping",
                    "Performance testing",
                    "Detection evasion testing"
                ]
            },
            {
                "name": "Documentation phase",
                "tasks": [
                    "Update technical documentation",
                    "Document command-line options",
                    "Create user guides",
                    "Document anti-bot evasion techniques"
                ]
            },
            {
                "name": "Deployment phase",
                "tasks": [
                    "Setup instructions",
                    "Configuration management",
                    "Monitoring and maintenance"
                ]
            }
        ],
        "specific_guidelines": [
            "Always be mindful of anti-bot detection mechanisms and legal compliance",
            "Test changes thoroughly before pushing to production",
            "Consider the impact on scraping performance and reliability",
            "Maintain backward compatibility with existing data structures",
            "Document all scraper interactions and data extraction patterns clearly",
            "When enhancing the anti-bot detection, provide examples of evasion techniques used",
            "For GUI improvements, include simple mockups or descriptions of the proposed changes",
            "Always follow best practices for web scraping (respect robots.txt, implement rate limiting)",
            "Implement proper error handling and recovery mechanisms",
            "Follow Puppeteer/Playwright best practices"
        ]
    },
    "data_analysis": {
        "specific_categories": [
            {
                "id": "dataHandling",
                "name": "Data Handling",
                "items": [
                    "Implement proper data validation and cleaning",
                    "Handle missing values appropriately",
                    "Document data transformations",
                    "Ensure reproducibility of analysis",
                    "Implement data versioning"
                ]
            },
            {
                "id": "performanceOptimization",
                "name": "Performance Optimization",
                "items": [
                    "Use vectorized operations where possible",
                    "Implement chunking for large datasets",
                    "Consider memory usage optimization",
                    "Profile code to identify bottlenecks",
                    "Use appropriate data structures for specific operations"
                ]
            },
            {
                "id": "visualizationBestPractices",
                "name": "Visualization Best Practices",
                "items": [
                    "Follow data visualization best practices",
                    "Use appropriate chart types for specific data",
                    "Ensure accessibility of visualizations",
                    "Provide context and clear labeling",
                    "Implement interactive elements when appropriate"
                ]
            },
            {
                "id": "errorHandling",
                "name": "Error Handling",
                "items": [
                    "Implement proper exception handling",
                    "Add input validation",
                    "Provide clear error messages",
                    "Log analysis errors appropriately"
                ]
            }
        ],
        "development_workflow": [
            {
                "name": "Data understanding phase",
                "tasks": [
                    "Explore data structure and characteristics",
                    "Identify data quality issues",
                    "Document data sources and formats",
                    "Perform initial statistical analysis"
                ]
            },
            {
                "name": "Data preparation phase",
                "tasks": [
                    "Implement data cleaning procedures",
                    "Handle missing or incorrect values",
                    "Create feature engineering pipeline",
                    "Split data for analysis/training/testing"
                ]
            },
            {
                "name": "Analysis/modeling phase",
                "tasks": [
                    "Develop analysis methods or models",
                    "Implement statistical tests",
                    "Create visualization functions",
                    "Document analysis approach"
                ]
            },
            {
                "name": "Evaluation phase",
                "tasks": [
                    "Validate analysis results",
                    "Perform sensitivity analysis",
                    "Compare against baseline or alternatives",
                    "Document limitations and assumptions"
                ]
            },
            {
                "name": "Deployment phase",
                "tasks": [
                    "Package analysis as reusable components",
                    "Create documentation and examples",
                    "Implement monitoring for data drift",
                    "Set up automated reporting"
                ]
            }
        ],
        "specific_guidelines": [
            "Always document data sources and transformations",
            "Ensure reproducibility of all analyses",
            "Validate results with appropriate statistical tests",
            "Create clear visualizations with proper context",
            "Consider performance implications for large datasets",
            "Document assumptions and limitations",
            "Use appropriate data structures for efficient operations",
            "Include error handling for edge cases",
            "Create reusable components where possible",
            "Provide clear interpretation of results"
        ]
    },
    "api_development": {
        "specific_categories": [
            {
                "id": "securityConsiderations",
                "name": "Security Considerations",
                "items": [
                    "Implement proper authentication and authorization",
                    "Use HTTPS for all endpoints",
                    "Validate all input data",
                    "Implement rate limiting",
                    "Handle sensitive data appropriately",
                    "Follow OWASP security guidelines"
                ]
            },
            {
                "id": "apiDesign",
                "name": "API Design",
                "items": [
                    "Follow RESTful principles",
                    "Use appropriate HTTP methods and status codes",
                    "Implement consistent error handling",
                    "Design for backward compatibility",
                    "Document API with OpenAPI/Swagger",
                    "Implement versioning strategy"
                ]
            },
            {
                "id": "performanceOptimization",
                "name": "Performance Optimization",
                "items": [
                    "Implement caching mechanisms",
                    "Optimize database queries",
                    "Use pagination for large response sets",
                    "Consider asynchronous processing for long-running operations",
                    "Implement connection pooling"
                ]
            },
            {
                "id": "monitoring",
                "name": "Monitoring and Observability",
                "items": [
                    "Implement comprehensive logging",
                    "Add performance metrics collection",
                    "Set up health check endpoints",
                    "Use structured logging format",
                    "Implement distributed tracing"
                ]
            }
        ],
        "development_workflow": [
            {
                "name": "Design phase",
                "tasks": [
                    "Define API requirements and scope",
                    "Design API endpoints and data models",
                    "Create OpenAPI/Swagger specification",
                    "Design authentication and authorization strategy"
                ]
            },
            {
                "name": "Implementation phase",
                "tasks": [
                    "Implement API endpoints",
                    "Create data models and validation",
                    "Implement business logic",
                    "Add security measures"
                ]
            },
            {
                "name": "Testing phase",
                "tasks": [
                    "Create unit tests for components",
                    "Implement integration tests for endpoints",
                    "Perform security testing",
                    "Conduct performance and load testing"
                ]
            },
            {
                "name": "Documentation phase",
                "tasks": [
                    "Generate API documentation",
                    "Create usage examples",
                    "Document authentication process",
                    "Create deployment instructions"
                ]
            },
            {
                "name": "Deployment phase",
                "tasks": [
                    "Set up CI/CD pipeline",
                    "Implement monitoring and logging",
                    "Create deployment environments",
                    "Plan scaling strategy"
                ]
            }
        ],
        "specific_guidelines": [
            "Follow RESTful API design principles",
            "Document all endpoints with OpenAPI/Swagger",
            "Implement proper authentication and authorization",
            "Validate all input data to prevent injection attacks",
            "Use appropriate HTTP status codes",
            "Implement versioning to maintain backward compatibility",
            "Add comprehensive error handling with meaningful messages",
            "Set up rate limiting to prevent abuse",
            "Implement proper logging for debugging and monitoring",
            "Create automated tests for all endpoints"
        ]
    },
    "custom": {
        "specific_categories": [],
        "development_workflow": [],
        "specific_guidelines": []
    }
}

def create_template_files():
    """Create default template files if they don't exist."""
    for filename, content in DEFAULT_TEMPLATES.items():
        template_path = TEMPLATE_DIR / filename
        if not template_path.exists():
            with open(template_path, 'w') as f:
                f.write(content)
            print(f"Created template: {template_path}")

def save_config(config: Dict[str, Any], output_file: str) -> None:
    """Save configuration to a file."""
    with open(output_file, 'w') as f:
        if output_file.endswith('.json'):
            json.dump(config, f, indent=2)
        else:
            yaml.dump(config, f, sort_keys=False)
    print(f"Configuration saved to {output_file}")

def load_config(input_file: str) -> Dict[str, Any]:
    """Load configuration from a file."""
    with open(input_file, 'r') as f:
        if input_file.endswith('.json'):
            return json.load(f)
        else:
            return yaml.safe_load(f)

def get_project_info() -> Dict[str, Any]:
    """Collect basic project information."""
    questions = [
        inquirer.Text('project_name', message="What is the project name?"),
        inquirer.Text('repo_name', message="What is the repository name?"),
        inquirer.Text('github_username', message="What is your GitHub username?"),
        inquirer.List('project_type',
                     message="What type of project is this?",
                     choices=['web_scraper', 'data_analysis', 'api_development', 'custom']),
    ]
    answers = inquirer.prompt(questions)
    
    return answers

def customize_project_type(project_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Customize configuration based on project type."""
    if project_type == 'custom':
        # For custom project type, we'll ask for more details
        config = collect_custom_project_details(config)
    else:
        # For predefined project types, use default values
        project_template = PROJECT_TYPES[project_type]
        config['project_specific_categories'] = project_template['specific_categories']
        config['development_workflow'] = project_template['development_workflow']
        config['project_specific_guidelines'] = project_template['specific_guidelines']
    
    return config

def collect_custom_project_details(config: Dict[str, Any]) -> Dict[str, Any]:
    """Collect details for a custom project type."""
    # Collect categories
    categories = []
    add_category = True
    
    while add_category:
        category_questions = [
            inquirer.Text('name', message="Category name (e.g., 'Security Considerations'):"),
            inquirer.Text('id', message="Category ID (e.g., 'securityConsiderations'):"),
        ]
        category = inquirer.prompt(category_questions)
        
        # Collect items for this category
        items = []
        add_item = True
        
        while add_item:
            item = inquirer.prompt([
                inquirer.Text('item', message=f"Add item to '{category['name']}' (leave empty to finish):"),
            ])
            
            if item['item']:
                items.append(item['item'])
            else:
                add_item = False
        
        if items:
            category['items'] = items
            categories.append(category)
        
        # Ask if user wants to add another category
        add_another = inquirer.prompt([
            inquirer.Confirm('add', message="Add another category?", default=False),
        ])
        add_category = add_another['add']
    
    config['project_specific_categories'] = categories
    
    # Collect development workflow phases
    phases = []
    add_phase = True
    
    while add_phase:
        phase_questions = [
            inquirer.Text('name', message="Phase name (e.g., 'Analysis phase'):"),
        ]
        phase = inquirer.prompt(phase_questions)
        
        # Collect tasks for this phase
        tasks = []
        add_task = True
        
        while add_task:
            task = inquirer.prompt([
                inquirer.Text('task', message=f"Add task to '{phase['name']}' phase (leave empty to finish):"),
            ])
            
            if task['task']:
                tasks.append(task['task'])
            else:
                add_task = False
        
        if tasks:
            phase['tasks'] = tasks
            phases.append(phase)
        
        # Ask if user wants to add another phase
        add_another = inquirer.prompt([
            inquirer.Confirm('add', message="Add another development phase?", default=False),
        ])
        add_phase = add_another['add']
    
    config['development_workflow'] = phases
    
    # Collect project-specific guidelines
    guidelines = []
    add_guideline = True
    
    while add_guideline:
        guideline = inquirer.prompt([
            inquirer.Text('guideline', message="Add project-specific guideline (leave empty to finish):"),
        ])
        
        if guideline['guideline']:
            guidelines.append(guideline['guideline'])
        else:
            add_guideline = False
    
    config['project_specific_guidelines'] = guidelines
    
    return config

def get_current_enhancement() -> Dict[str, Any]:
    """Collect information about the current enhancement."""
    enhancement = {}
    
    questions = [
        inquirer.Text('name', message="What is the current enhancement name?"),
        inquirer.Text('description', message="Brief description of the enhancement:"),
    ]
    answers = inquirer.prompt(questions)
    enhancement.update(answers)
    
    # Tasks for the enhancement
    tasks = []
    add_task = True
    
    while add_task:
        task = inquirer.prompt([
            inquirer.Text('description', message="Add a task (leave empty to finish):"),
            inquirer.Confirm('completed', message="Is this task completed?", default=False),
        ])
        
        if task['description']:
            tasks.append(task)
        else:
            add_task = False
    
    enhancement['tasks'] = tasks
    
    # Tasks in progress
    in_progress = []
    add_in_progress = True
    
    while add_in_progress:
        task = inquirer.prompt([
            inquirer.Text('task', message="Add a task in progress (leave empty to finish):"),
        ])
        
        if task['task']:
            in_progress.append(task['task'])
        else:
            add_in_progress = False
    
    enhancement['in_progress'] = in_progress
    
    # Next focus
    next_focus = {}
    next_focus_questions = [
        inquirer.Text('name', message="What is the next focus area name?"),
        inquirer.Text('description', message="Brief description of the next focus:"),
    ]
    next_focus.update(inquirer.prompt(next_focus_questions))
    
    # Steps for next focus
    steps = []
    add_step = True
    
    while add_step:
        step = inquirer.prompt([
            inquirer.Text('step', message="Add a step for the next focus (leave empty to finish):"),
        ])
        
        if step['step']:
            steps.append(step['step'])
        else:
            add_step = False
    
    next_focus['steps'] = steps
    enhancement['next_focus'] = next_focus
    
    # Future actions
    future_actions = []
    add_action = True
    
    while add_action:
        action = inquirer.prompt([
            inquirer.Text('action', message="Add a future action (leave empty to finish):"),
        ])
        
        if action['action']:
            future_actions.append(action['action'])
        else:
            add_action = False
    
    enhancement['future_actions'] = future_actions
    
    return enhancement

def get_future_enhancements() -> List[Dict[str, Any]]:
    """Collect information about future enhancements."""
    enhancements = []
    add_enhancement = True
    
    while add_enhancement:
        enhancement = {}
        
        questions = [
            inquirer.Text('name', message="Enhancement name:"),
            inquirer.Text('description', message="Brief description:"),
        ]
        answers = inquirer.prompt(questions)
        enhancement.update(answers)
        
        # Features
        features = []
        add_feature = True
        
        while add_feature:
            feature = inquirer.prompt([
                inquirer.Text('feature', message="Add a potential feature (leave empty to finish):"),
            ])
            
            if feature['feature']:
                features.append(feature['feature'])
            else:
                add_feature = False
        
        enhancement['features'] = features
        
        # Benefits
        benefits = []
        add_benefit = True
        
        while add_benefit:
            benefit = inquirer.prompt([
                inquirer.Text('benefit', message="Add a benefit (leave empty to finish):"),
            ])
            
            if benefit['benefit']:
                benefits.append(benefit['benefit'])
            else:
                add_benefit = False
        
        enhancement['benefits'] = benefits
        
        enhancements.append(enhancement)
        
        # Ask if user wants to add another enhancement
        add_another = inquirer.prompt([
            inquirer.Confirm('add', message="Add another future enhancement?", default=False),
        ])
        add_enhancement = add_another['add']
    
    return enhancements

def collect_project_details(config_file: Optional[str] = None) -> Dict[str, Any]:
    """Collect all project details either from config or interactively."""
    config = {}
    
    # Load configuration if provided
    if config_file and os.path.exists(config_file):
        config = load_config(config_file)
        print(f"Loaded configuration from {config_file}")
    
    # Interactive mode for missing configuration
    if 'project_name' not in config or 'repo_name' not in config or 'github_username' not in config:
        project_info = get_project_info()
        config.update(project_info)
    
    # Get project type specific settings
    project_type = config.get('project_type', 'custom')
    if ('project_specific_categories' not in config or 
        'development_workflow' not in config or 
        'project_specific_guidelines' not in config):
        config = customize_project_type(project_type, config)
    
    # Get what we've accomplished
    if 'what_weve_accomplished' not in config:
        what_accomplished = inquirer.prompt([
            inquirer.Text('what_weve_accomplished', 
                         message="What have we accomplished so far? (brief description)",
                         default="We have started the development of the project."),
        ])
        config.update(what_accomplished)
    
    # Get recently completed items
    if 'recently_completed' not in config:
        recently_completed = []
        add_item = True
        
        while add_item:
            item = inquirer.prompt([
                inquirer.Text('item', message="Add a recently completed item (leave empty to finish):"),
            ])
            
            if item['item']:
                recently_completed.append(item['item'])
            else:
                add_item = False
        
        config['recently_completed'] = recently_completed
    
    # Get current enhancement
    if 'current_enhancement' not in config:
        config['current_enhancement'] = get_current_enhancement()
    
    # Get future enhancements
    if 'future_enhancements' not in config:
        config['future_enhancements'] = get_future_enhancements()
    
    # Add today's date
    config['today_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
    
    return config

def generate_files(config: Dict[str, Any], output_dir: str) -> None:
    """Generate project instruction files from templates."""
    # Ensure templates exist
    create_template_files()
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate all files
    for template_name in DEFAULT_TEMPLATES.keys():
        output_file = template_name.replace('.j2', '')
        template = env.get_template(template_name)
        content = template.render(**config)
        
        with open(output_path / output_file, 'w') as f:
            f.write(content)
        
        print(f"Generated {output_file}")

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Generate project instruction structure files.')
    parser.add_argument('--config', help='Path to configuration file (JSON or YAML)')
    parser.add_argument('--output-dir', default='.', help='Directory to output files')
    parser.add_argument('--save-config', default='project_config.yaml', help='Save configuration to file')
    parser.add_argument('--non-interactive', action='store_true', help='Non-interactive mode')
    
    args = parser.parse_args()
    
    # Create template directory and default templates
    create_template_files()
    
    if args.non_interactive and not args.config:
        print("Error: Non-interactive mode requires a configuration file.")
        return
    
    # Collect project details
    if args.non_interactive:
        config = load_config(args.config)
    else:
        config = collect_project_details(args.config)
        save_config(config, args.save_config)
    
    # Generate files
    generate_files(config, args.output_dir)
    
    print(f"\nProject instruction structure setup complete. Files generated in {args.output_dir}.")
    print(f"Configuration saved to {args.save_config}")
    print("\nYou can now use this configuration for future projects or updates.")

if __name__ == "__main__":
    main()
