import json
import os
import urllib.request

def fetch_github_data(username="suryanandanbabbar"):
    token = os.environ.get("GITHUB_TOKEN")
    
    data = {
        "name": "Suryanandan Babbar",
        "username": username,
        "commits": 0,
        "stars": 0,
        "public_repos": 0,
        "top_languages": [],
        "latest_repo": "N/A",
        "latest_repo_lang": "N/A",
        "latest_repo_updated": "N/A",
        "latest_release": "N/A"
    }
    
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "Dashboard-Builder"}
    if token:
        headers["Authorization"] = f"token {token}"
        
    try:
        # 1. Fetch User Info
        req = urllib.request.Request(f"https://api.github.com/users/{username}", headers=headers)
        with urllib.request.urlopen(req) as response:
            user_data = json.loads(response.read().decode())
            data["name"] = user_data.get("name", data["name"])
            data["public_repos"] = user_data.get("public_repos", 0)
            
        # 2. Fetch Repos for Stars, Languages, and Latest Repo
        req = urllib.request.Request(f"https://api.github.com/users/{username}/repos?per_page=100&sort=pushed", headers=headers)
        with urllib.request.urlopen(req) as response:
            repos_data = json.loads(response.read().decode())
            
            total_stars = 0
            languages = {}
            for repo in repos_data:
                total_stars += repo.get("stargazers_count", 0)
                lang = repo.get("language")
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
                    
            data["stars"] = total_stars
            sorted_langs = sorted(languages.items(), key=lambda item: item[1], reverse=True)
            data["top_languages"] = [lang for lang, count in sorted_langs[:3]]
            
            if repos_data:
                latest = repos_data[0]
                data["latest_repo"] = latest.get("name", "N/A")
                data["latest_repo_lang"] = latest.get("language", "N/A")
                data["latest_repo_updated"] = latest.get("pushed_at", "N/A").split("T")[0]
                
    except Exception as e:
        print(f"Error fetching GitHub REST data: {e}")

    # 3. GraphQL for Latest Release (if token exists)
    if token:
        query = """
        query($login: String!) {
          user(login: $login) {
            contributionsCollection {
              contributionCalendar {
                totalContributions
              }
            }
            repositories(first: 10, orderBy: {field: PUSHED_AT, direction: DESC}) {
              nodes {
                name
                releases(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
                  nodes {
                    tagName
                  }
                }
              }
            }
          }
        }
        """
        req_data = json.dumps({"query": query, "variables": {"login": username}}).encode('utf-8')
        gql_headers = headers.copy()
        gql_headers["Content-Type"] = "application/json"
        
        try:
            req = urllib.request.Request("https://api.github.com/graphql", data=req_data, headers=gql_headers)
            with urllib.request.urlopen(req) as response:
                gql_data = json.loads(response.read().decode())
                user_node = gql_data.get("data", {}).get("user", {})
                
                data["commits"] = user_node.get("contributionsCollection", {}).get("contributionCalendar", {}).get("totalContributions", 0)
                
                repos = user_node.get("repositories", {}).get("nodes", [])
                
                latest_release = "N/A"
                for repo in repos:
                    releases = repo.get("releases", {}).get("nodes", [])
                    if releases:
                        latest_release = f"{repo.get('name')} {releases[0].get('tagName')}"
                        break
                        
                data["latest_release"] = latest_release
        except Exception as e:
            print(f"Error fetching GitHub GraphQL data: {e}")

    # Save to JSON cache
    with open("github_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("GitHub data fetched and cached to github_data.json")

if __name__ == "__main__":
    fetch_github_data()
