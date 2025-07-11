import base64
import json
from github import Github
from config import config

g = Github(config.github_token)


def commit_review(review_data: dict):
    try:
        repo = g.get_repo("Dcatik/OpenReviewBot")
        file_path = "reviews.json"
        
        try:
            file_content = repo.get_contents(file_path)
            data = json.loads(base64.b64decode(file_content.content).decode("utf-8"))
            sha = file_content.sha
        except Exception:
            data = []
            sha = None
            
        data.append(review_data)
        
        commit_message = f"Add review for {review_data['company_name']}"
        
        if sha:
            repo.update_file(
                file_path,
                commit_message,
                json.dumps(data, indent=4),
                sha,
                branch="main",
            )
        else:
            repo.create_file(
                file_path,
                commit_message,
                json.dumps(data, indent=4),
                branch="main",
            )
    except Exception as e:
        print(f"Failed to commit to GitHub: {e}")