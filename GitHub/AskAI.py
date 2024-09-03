from openai import OpenAI
import os
import requests
from dotenv import load_dotenv

# Set the Service account project_manager API KEY
#openai.api_key = os.getenv("OPENAI_API_KEY_SA_PROJECT_MANAGER")



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
    github_username = os.getenv("GITHUB_USERNAME")
    github_repo = os.getenv("GITHUB_REPO")
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Authorization": f'tokeng {github_token}'
    }
    for issue in issues:
        data  = {"title":issue}
        response = response.post(f"https://api.github.com/repos/{github_username}/{github_repo}/issues",
                                 headers=headers,
                                 json=data)
        if response.status_code == 201:
            print(f"Issue created: {issue}")
        else:
            print(f"Failed to create issue: {issue}")

# Example usage
if __name__ == "__main__":
    import sys
    
    #project_description = sys.argv[1]
    project_description = os.getenv("PROJECT_DESCRIPTION")
    issues = ask_features_list_from_gpt(project_description)
    
    create_github_issues(issues)