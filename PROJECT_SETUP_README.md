# Project Instruction Structure Setup Tool

This tool helps you create a standardized project instruction structure for GitHub repositories, making it easy to set up consistent collaboration guidelines across multiple projects.

## Features

- Interactive wizard for gathering project details
- Pre-defined templates for common project types (web scraper, data analysis, API development)
- Custom project type support
- Configuration saving/loading for repeatable setup
- Template-based file generation using Jinja2
- Support for both YAML and JSON configuration files

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements-project-setup.txt
```

2. Ensure Python 3.8+ is installed on your system.

## Usage

### Interactive Mode

Run the script without any arguments to use the interactive mode:

```bash
python setup_project_structure.py
```

This will guide you through a series of questions to configure your project structure.

### Using a Configuration File

You can also use a previously saved configuration file:

```bash
python setup_project_structure.py --config my_project_config.yaml
```

### Non-Interactive Mode

For automation, you can use the non-interactive mode:

```bash
python setup_project_structure.py --config my_project_config.yaml --non-interactive
```

### Additional Options

- `--output-dir`: Specify the directory where files will be generated (default: current directory)
- `--save-config`: Specify where to save the configuration (default: project_config.yaml)

## Generated Files

The script will generate the following files:

- **PROJECT_INSTRUCTIONS.md**: Contains workflow guidelines and project-specific guidelines
- **AI_WORKFLOW_GUIDE.md**: Explains the AI assistant workflow configuration
- **.claude.json**: Configuration for Claude AI assistant
- **NEXT_STEPS.md**: Current enhancement focus and recent accomplishments
- **FUTURE_ENHANCEMENTS.md**: Strategic future enhancement plans

## Configuration Format

The configuration can be in either YAML or JSON format. Here's a sample structure:

```yaml
project_name: "My Project"
repo_name: "my-project"
github_username: "username"
project_type: "web_scraper"  # Can be web_scraper, data_analysis, api_development, or custom
project_specific_categories:
  - id: "securityConsiderations"
    name: "Security Considerations"
    items:
      - "Follow ethical scraping practices"
      - "Respect robots.txt and site terms of service"
      # More items...
  # More categories...
development_workflow:
  - name: "Analysis phase"
    tasks:
      - "Understand the structure of websites to be scraped"
      - "Design scraping strategies"
      # More tasks...
  # More phases...
project_specific_guidelines:
  - "Always be mindful of anti-bot detection mechanisms and legal compliance"
  - "Test changes thoroughly before pushing to production"
  # More guidelines...
what_weve_accomplished: "Brief description of what's been accomplished"
recently_completed:
  - "Item 1"
  - "Item 2"
  # More items...
current_enhancement:
  name: "Enhancement Name"
  description: "Brief description"
  tasks:
    - description: "Task 1"
      completed: true
    - description: "Task 2"
      completed: false
  # More current enhancement details...
future_enhancements:
  - name: "Enhancement 1"
    description: "Description"
    features:
      - "Feature 1"
      - "Feature 2"
    benefits:
      - "Benefit 1"
      - "Benefit 2"
  # More future enhancements...
```

## Creating a Template Repository

To use this tool as part of a template repository system:

1. Create a new GitHub repository
2. Add this script and the requirements file
3. Run the script once to generate default template files
4. Enable the repository as a GitHub template repository
5. When creating new projects, use the template and then customize the files using this script

## Customizing Templates

The script creates default templates in a `templates` directory. You can customize these templates to change the format of the generated files. The templates use Jinja2 syntax.

## Adding New Project Types

To add a new project type, modify the `PROJECT_TYPES` dictionary in the script to include your new project type with appropriate categories, workflow phases, and guidelines.

## Best Practices

1. Save your configuration files for reuse across similar projects
2. Create multiple configurations for different project categories
3. Update your templates as your workflow evolves
4. Consider adding the configuration file to version control for team reference
5. Run the script at the beginning of each new project

## Troubleshooting

- If templates are not found, make sure the `templates` directory exists in the same directory as the script
- If you encounter errors with YAML or JSON files, check their format for syntax errors
- Make sure all required dependencies are installed
