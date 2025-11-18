import os
from github import Github
from langchain.agents import initialize_agent, Tool, AgentType

# Set up GitHub authentication
token = os.getenv("GITHUB_TOKEN")  # Personal Access Token for GitHub API access
g = Github(token)

# GitHub repository and PR details
repo_name = "preethamkondapaka/ai-pr-reviewer"
pr_number = 1  # Replace with dynamic PR number from event

# Function to check CI/CD status
def check_pr_status(repo_name, pr_number):
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    # Convert PaginatedList to list and reverse it
    commits = list(pr.get_commits())  # Convert the PaginatedList to a list
    statuses = commits[::-1]  # Reverse the list
    
    # Find the latest commit status (this assumes a basic CI status check is running)
    for status in statuses:
        if status.statuses:  # Checking if any status is returned
            latest_status = status.statuses[0]
            if latest_status.state == "success":
                return "approved"
            elif latest_status.state == "error":
                return "blocked"
    return "waiting"

# Function to approve or block PR
def review_pr(repo_name, pr_number, decision):
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    if decision == "approved":
        pr.create_review(body="PR approved by AI Agent", event="APPROVE")
    elif decision == "blocked":
        pr.create_review(body="PR blocked due to failing checks", event="REQUEST_CHANGES")
    else:
        pr.create_review(body="PR is still under review", event="COMMENT")

# Initialize LangChain agent (you can expand this for more decision-making logic)
def agent_review(pr_status):
    if pr_status == "approved":
        return "approved"
    elif pr_status == "blocked":
        return "blocked"
    else:
        return "waiting"

# Main function to trigger agent review process
def trigger_agent_review():
    pr_status = check_pr_status(repo_name, pr_number)
    decision = agent_review(pr_status)
    review_pr(repo_name, pr_number, decision)

if __name__ == "__main__":
    trigger_agent_review()
