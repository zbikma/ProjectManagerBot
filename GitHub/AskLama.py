import os
import requests
from transformers import LlamaForCausalLM, LlamaTokenizer




# Set up the LLaMA model from Hugging Face
model_name = "meta-llama/Llama-2-7b-chat-hf"  # Use the appropriate LLaMA model available in Hugging Face
tokenizer = LlamaTokenizer.from_pretrained(model_name)
model = LlamaForCausalLM.from_pretrained(model_name)

def ask_features_list_from_llama(project_description):
    # Create a prompt based on the project description
    prompt = f"Generate a list of tasks or issues that should be created in a GitHub project for the following project description: {project_description} \
        showcasing state of the art technologies related to the project domain"
        
    # Tokenize the input prompt
    inputs = tokenizer(prompt, return_tensors="pt")

    # Generate a response from the LLaMA model
    outputs = model.generate(**inputs, max_length=2000)

    # Decode the output to get the text
    issues_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Convert the response into a list of issues
    issues = issues_text.strip().split('\n')
    return issues

def create_github_issues(issues):
    # Fetch environment variables
    github_username = os.getenv("GITHUB_USERNAME")
    github_repo = os.getenv("GITHUB_REPO")
    github_token = os.getenv("GITHUB_TOKEN")
    
    headers = {
        "Authorization": f'token {github_token}'
    }
    for issue in issues:
        data = {"title": issue}
        response = requests.post(f"https://api.github.com/repos/{github_username}/{github_repo}/issues",
                                 headers=headers,
                                 json=data)
        if response.status_code == 201:
            print(f"Issue created: {issue}")
        else:
            print(f"Failed to create issue: {issue}, {response.content}")

# Example usage
if __name__ == "__main__":
    # Get project description from environment variable or input
    project_description = os.getenv("PROJECT_DESCRIPTION", "Describe your project here")
    
    # Generate issues using the LLaMA model
    issues = ask_features_list_from_llama(project_description)
    
    # Create issues in the GitHub repository
    create_github_issues(issues)
