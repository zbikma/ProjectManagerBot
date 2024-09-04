from openai import OpenAI
import os
import requests
from dotenv import load_dotenv

# Set the Service account project_manager API KEY
#openai.api_key = os.getenv("OPENAI_API_KEY_SA_PROJECT_MANAGER")

project_description = os.getenv("PROJECT_DESCRIPTION")
github_username = os.getenv("GITHUB_USERNAME")
github_repo = os.getenv("GITHUB_REPO")
github_token = os.getenv("GITHUB_TOKEN")
github_project_name=os.getenv("GITHUB_PROJECT")
headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
        }

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY_SA_PROJECT_MANAGER"),
)



def ask_features_list_from_gpt(project_description):
    # Create a prompt based on the project description
    prompt = f"Generate a list of tasks or issues that should be created in a GitHub project for the following project description: {project_description} showcasing state-of-the-art technologies related to the project domain."
    
    try:
        # Use the chat completions endpoint for chat models
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                "role": "user",
                "content": prompt,
                },
            ],
            )   
        
        issues_text = completion.choices[0].message.content.strip()
        issues = issues_text.split('\n')
        return issues
    except client.error.AuthenticationError as e:
        print(f"Authentication error: {e}")
        raise
    except client.error.OpenAIError as e:
        print(f"OpenAI API error occurred: {e}")
        raise


def create_github_issues(github_username, github_repo,github_token,issues):
     # Fetch environment variables
   
    
    for issue in issues:
        data  = {"title":issue}
        response = response.post(f"https://api.github.com/repos/{github_username}/{github_repo}/issues",
                                 headers=headers,
                                 json=data)
        if response.status_code == 201:
            print(f"Issue created: {issue}")
        else:
            print(f"Failed to create issue: {issue}")

# Function to check if a repository exists
def repo_exists(github_username, github_repo):
    url = f"https://api.github.com/repos/{github_username}/{github_repo}"
    response = requests.get(url, headers=headers)
    return response.status_code == 200

# Function to create a repository if it doesn't exist
def create_repo(github_username, github_repo):
    url = "https://api.github.com/user/repos"
    data = {
        "name": github_repo,
        "private": True,  # Change to False if you want a public repository
        "auto_init": True,  # Automatically create an initial commit with a README
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Repository '{github_repo}' created successfully.")
    else:
        print(f"Failed to create repository: {response.status_code} - {response.text}")

# Create a new project within a repository
def create_github_project(repo_owner, repo_name, project_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/projects"
    data = {
        "name": project_name,
        "body": "Project to track issues for this repository"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        project_url = response.json()['html_url']
        print(f"Project '{project_name}' created successfully: {project_url}")
        return response.json()['id']  # Return the project ID for further use
    else:
        print(f"Failed to create project: {response.status_code} - {response.text}")
        return None
    
# Function to check if the user has any linked projects
def check_for_existing_user_projects(username):
    url = f"https://api.github.com/users/{username}/projects"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        projects = response.json()
        if len(projects) > 0:
            print(f"User '{username}' already has the following projects:")
            for project in projects:
                print(f" - {project['name']}: {project['html_url']}")
            return projects[0]['id']  # Return the first project's ID if you want to use it
        else:
            print(f"User '{username}' has no linked projects.")
            return None
    else:
        print(f"Failed to check for projects: {response.status_code} - {response.text}")
        return None

# Function to create a new project if none exists
def create_github_project(repo_owner, repo_name, project_name):
    headers = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github.inertia-preview+json"
    }
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/projects"
    data = {
        "name": project_name,
        "body": "Project to track issues for this repository"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        project_url = response.json()['html_url']
        print(f"Project '{project_name}' created successfully: {project_url}")
        return response.json()['id']  # Return the project ID for further use
    else:
        print(f"Failed to create project: {response.status_code} - {response.text}")
        return None

# Function to create an issue and add it to a project
def create_github_issues_and_add_to_project(repo_owner, repo_name, issues, project_id, column_name):
    for issue_title in issues:
        issue_data = {
            "title": issue_title,
            "labels": ["enhancement"]
        }
        issue_response = requests.post(f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues",
                                       headers=headers, json=issue_data)
        
        if issue_response.status_code == 201:
            issue_url = issue_response.json()['html_url']
            issue_id = issue_response.json()['id']
            print(f"Issue '{issue_title}' created: {issue_url}")
            
            columns_url = f"https://api.github.com/projects/{project_id}/columns"
            columns_response = requests.get(columns_url, headers=headers)
            if columns_response.status_code == 200:
                columns = columns_response.json()
                print(f"Available columns: {[column['name'] for column in columns]}")  # Debugging line
                column_id = next((column['id'] for column in columns if column['name'].lower() == column_name.lower()), None)
                if column_id:
                    add_to_project_url = f"https://api.github.com/projects/columns/{column_id}/cards"
                    card_data = {
                        "content_id": issue_id,
                        "content_type": "Issue"
                    }
                    card_response = requests.post(add_to_project_url, headers=headers, json=card_data)
                    if card_response.status_code == 201:
                        print(f"Issue '{issue_title}' added to project column '{column_name}'")
                    else:
                        print(f"Failed to add issue to project: {card_response.status_code} - {card_response.text}")
                else:
                    print(f"Column '{column_name}' not found in project. Available columns: {[column['name'] for column in columns]}")
            else:
                print(f"Failed to retrieve project columns: {columns_response.status_code} - {columns_response.text}")
        else:
            print(f"Failed to create issue: {issue_response.status_code} - {issue_response.text}")


# Function to prompt the user to input the project name manually
def prompt_user_for_project_name():
    project_name = input("Please create a project in the repository using the GitHub web interface and enter the project name here: ")
    return project_name

# Function to find the project ID based on the project name
def get_project_id_by_name(username, project_name):
    url = f"https://api.github.com/users/{username}/projects"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        projects = response.json()
        for project in projects:
            if project['name'].lower() == project_name.lower():
                return project['id']
        print(f"Project '{project_name}' not found.")
        return None
    else:
        print(f"Failed to retrieve projects: {response.status_code} - {response.text}")
        return None
# Example usage
if __name__ == "__main__":
    import sys
    
    #project_description = sys.argv[1]
    '''
    project_description = os.getenv("PROJECT_DESCRIPTION")
    github_username = os.getenv("GITHUB_USERNAME")
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPO")
    '''
    issues = ask_features_list_from_gpt(project_description)
    # Check if the repository exists
    if not repo_exists(github_username, github_repo):
        create_repo(github_username, github_repo)
        '''
        project_id = check_for_existing_user_projects(github_username)
    if not project_id:
        print("No project linked to the repository.")
        project_name = prompt_user_for_project_name()
        '''
    
    project_id = get_project_id_by_name(github_username, github_project_name)
        
    if project_id:
        create_github_issues_and_add_to_project(github_username, github_repo, issues, project_id, "To Do")
    #create_github_issues(issues)