from github import Github
import json
import datetime

import os
from dotenv import load_dotenv

# Set the Service account project_manager API KEY
#openai.api_key = os.getenv("OPENAI_API_KEY_SA_PROJECT_MANAGER")

#project_description = os.getenv("PROJECT_DESCRIPTION")
github_username = os.getenv("GITHUB_USERNAME")
github_repo = os.getenv("GITHUB_REPO")
github_token = os.getenv("GITHUB_TOKEN")
#github_project_name=os.getenv("GITHUB_PROJECT")


# Initialize the GitHub client
g = Github(github_token)

# Load your GitHub repository
repo = g.get_repo(f"{github_username}/{github_repo}")

# Load the milestones and tasks from a JSON file
with open('GithubAutomation/milestons.json', 'r') as f:
    milestones_data = json.load(f)

def create_milestone(title, description, due_date):
    """Create a milestone in GitHub"""
    milestone = repo.create_milestone(
        title=title,
        state="open",
        description=description,
        due_on=due_date
    )
    return milestone

def create_issue(title, body, milestone_number):
    """Create an issue associated with a milestone"""
    repo.create_issue(
        title=title,
        body=body,
        milestone=repo.get_milestone(milestone_number)
    )

def main():
    for milestone in milestones_data:
        title = milestone['title']
        description = milestone['description']
        due_on = milestone['due_on']
        
        # Convert due date string to a datetime object
        due_date = datetime.datetime.strptime(due_on, '%Y-%m-%dT%H:%M:%SZ')
        
        # Create milestone and get its number
        created_milestone = create_milestone(title, description, due_date)
        milestone_number = created_milestone.number

        # Create issues for each task in the milestone
        for task in milestone['tasks']:
            task_title = task['title']
            task_description = task.get('description', '')
            create_issue(task_title, task_description, milestone_number)

    print("Milestones and issues created successfully!")

if __name__ == "__main__":
    main()
