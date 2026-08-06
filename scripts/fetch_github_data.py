import json
import os
import urllib.request
from typing import Dict, List, Any

def get_github_token() -> str:
    """Retrieves the GITHUB_TOKEN from the environment, raising an error if missing."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN environment variable is not configured.")
    return token

def execute_graphql_query(username: str, token: str) -> Dict[str, Any]:
    """Executes the single GraphQL query to fetch all required metadata."""
    query = """
    query($login: String!) {
      user(login: $login) {
        name
        login
        followers {
          totalCount
        }
        repositories(first: 100, isFork: false, ownerAffiliations: OWNER, orderBy: {field: PUSHED_AT, direction: DESC}) {
          totalCount
          nodes {
            name
            stargazerCount
            pushedAt
            primaryLanguage {
              name
            }
          }
        }
      }
    }
    """
    req_data = json.dumps({"query": query, "variables": {"login": username}}).encode('utf-8')
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json",
        "User-Agent": "Dashboard-Builder"
    }
    
    req = urllib.request.Request("https://api.github.com/graphql", data=req_data, headers=headers)
    with urllib.request.urlopen(req) as response:
        gql_data = json.loads(response.read().decode())
        
    if "errors" in gql_data:
        raise RuntimeError(json.dumps(gql_data["errors"], indent=2))
        
    return gql_data.get("data", {}).get("user", {})

def calculate_total_stars(repositories: List[Dict[str, Any]]) -> int:
    """Sums the stargazerCount across all non-fork repositories."""
    return sum(repo.get("stargazerCount", 0) for repo in repositories)

def aggregate_languages(repositories: List[Dict[str, Any]]) -> List[str]:
    """Aggregates primary languages and returns the top 3 by occurrence."""
    languages = {}
    for repo in repositories:
        lang_node = repo.get("primaryLanguage")
        if lang_node and lang_node.get("name"):
            lang = lang_node.get("name")
            languages[lang] = languages.get(lang, 0) + 1
            
    sorted_langs = sorted(languages.items(), key=lambda item: item[1], reverse=True)
    return [lang for lang, _ in sorted_langs[:3]]

def latest_repository(repositories: List[Dict[str, Any]]) -> Dict[str, str]:
    """Determines the most recently pushed repository."""
    if not repositories:
        return {"name": "N/A", "lang": "N/A", "updated": "N/A"}
        
    latest = repositories[0] # The GraphQL query is already ordered by PUSHED_AT DESC
    
    name = latest.get("name", "N/A")
    lang_node = latest.get("primaryLanguage")
    lang = lang_node.get("name") if lang_node else "N/A"
    
    pushed_at = latest.get("pushedAt", "N/A")
    if pushed_at != "N/A":
        pushed_at = pushed_at.split("T")[0]
        
    return {"name": name, "lang": lang, "updated": pushed_at}

def save_cache(data: Dict[str, Any], filename: str = "github_data.json") -> None:
    """Saves the final dictionary to the JSON cache safely."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"Successfully updated {filename}")

def main():
    username = "suryanandanbabbar"
    
    try:
        token = get_github_token()
        user_node = execute_graphql_query(username, token)
        
        if not user_node:
            raise RuntimeError(f"User {username} not found or GraphQL returned no data.")
            
        repos_conn = user_node.get("repositories", {})
        repositories = repos_conn.get("nodes", [])
        
        latest_repo_info = latest_repository(repositories)
        
        data = {
            "name": user_node.get("name", ""),
            "username": user_node.get("login", username),
            # Temporary until a true lifetime commit counter is implemented.
            "commits": "1.3k+",
            "followers": user_node.get("followers", {}).get("totalCount", 0),
            "stars": calculate_total_stars(repositories),
            "public_repos": repos_conn.get("totalCount", 0),
            "top_languages": aggregate_languages(repositories),
            "latest_repo": latest_repo_info["name"],
            "latest_repo_lang": latest_repo_info["lang"],
            "latest_repo_updated": latest_repo_info["updated"]
        }
        
        # Overwrite cache only after a completely successful fetch and parse
        save_cache(data)
        
    except Exception as e:
        print(f"Error fetching GitHub data: {e}")
        print("Previous github_data.json was preserved.")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
