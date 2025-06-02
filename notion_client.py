import os
import requests

NOTION_API_URL = "https://api.notion.com/v1"
NOTION_API_TOKEN = os.environ.get("NOTION_API_TOKEN")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")
NOTION_VERSION = "2022-06-28"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}


# 🔍 Wyciąga tytuł i opis z commita (pierwsza linia = tytuł, reszta = opis)
def parse_commit_message(commit_message):
    lines = commit_message.strip().split('\n', 1)
    task_title = lines[0].strip()
    description = lines[1].strip() if len(lines) > 1 else "Brak opisu"
    return task_title, description


# 🔍 Szuka zadania w Notion po tytule
def search_page_by_commit(task_title):
    url = f"{NOTION_API_URL}/databases/{NOTION_DATABASE_ID}/query"
    data = {
        "filter": {
            "property": "Nazwa zadania",
            "title": {
                "contains": task_title
            }
        }
    }
    response = requests.post(url, headers=HEADERS, json=data)
    results = response.json().get("results", [])
    return results[0] if results else None


# ✅ Aktualizuje status i dane commita, jeśli strona istnieje
def update_page_status_to_done(page_id,
                               commit_url=None,
                               author_name=None,
                               description=None):
    url = f"{NOTION_API_URL}/pages/{page_id}"

    properties = {"Status": {"select": {"name": "Zrobione"}}}

    if commit_url:
        properties["Link do GitHub commit"] = {"url": commit_url}
    if author_name:
        properties["Osoba odpowiedzialna za commit"] = {
            "rich_text": [{
                "text": {
                    "content": author_name
                }
            }]
        }
    if description:
        properties["Opis zadania"] = {
            "rich_text": [{
                "text": {
                    "content": description
                }
            }]
        }

    data = {"properties": properties}
    response = requests.patch(url, headers=HEADERS, json=data)
    print("Update response:", response.status_code, response.text)
    return response.status_code == 200


# 👤 Pobiera ID użytkownika Notion po nazwie (jeśli chcesz dodać do "people")
def get_user_id_by_name(name):
    url = f"{NOTION_API_URL}/users"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("Error fetching users:", response.status_code, response.text)
        return None
    for user in response.json().get("results", []):
        if user.get("name", "").lower() == name.lower():
            return user["id"]
    return None


# 🚀 Główna funkcja wywoływana z webhooka
def send_commit_to_notion(commit_message,
                          repo_name,
                          author_name,
                          commit_url,
                          full_message="Brak opisu"):
    task_title, description = parse_commit_message(commit_message)
    existing_page = search_page_by_commit(task_title)

    if existing_page:
        page_id = existing_page["id"]
        print(f"Found existing page: {page_id}, updating status to Zrobione.")
        return update_page_status_to_done(page_id,
                                          commit_url=commit_url,
                                          author_name=author_name,
                                          description=description)

    user_id = get_user_id_by_name(author_name)

    properties = {
        "Nazwa zadania": {
            "title": [{
                "text": {
                    "content": task_title
                }
            }]
        },
        "Status": {
            "select": {
                "name": "Zrobione"
            }
        },
        "Link do GitHub commit": {
            "url": commit_url
        },
        "Opis zadania": {
            "rich_text": [{
                "text": {
                    "content": description
                }
            }]
        },
        "Osoba odpowiedzialna za commit": {
            "rich_text": [{
                "text": {
                    "content": author_name
                }
            }]
        }
    }

    if user_id:
        properties["Osoba odpowiedzialna"] = {"people": [{"id": user_id}]}

    data = {
        "parent": {
            "database_id": NOTION_DATABASE_ID
        },
        "properties": properties
    }

    response = requests.post(f"{NOTION_API_URL}/pages",
                             headers=HEADERS,
                             json=data)
    print("Create response:", response.status_code, response.text)
    return response.status_code in [200, 201]
