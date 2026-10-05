import requests


def get_repo_info(owner: str, repo: str):
    """
    Get public information about a GitHub repository.
    """

    url = f"https://api.github.com/repos/{owner}/{repo}"

    headers = {
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return {
        "success": True,
        "name": data["full_name"],
        "description": data["description"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "open_issues": data["open_issues_count"],
        "language": data["language"],
        "url": data["html_url"]
    }


def get_github_user(username: str):
    """
    Get public information about a GitHub user.
    """

    url = f"https://api.github.com/users/{username}"

    headers = {
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return {
        "success": True,
        "username": data["login"],
        "name": data["name"],
        "bio": data["bio"],
        "public_repos": data["public_repos"],
        "public_gists": data["public_gists"],
        "followers": data["followers"],
        "following": data["following"],
        "github_url": data["html_url"]
    }