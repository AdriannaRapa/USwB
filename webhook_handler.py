import json
import logging
from datetime import datetime
from flask import current_app
from models import db, WebhookLog
from notion_client import send_commit_to_notion


def process_github_webhook(payload, event_type):
    """
    Process GitHub webhook data and store it in the database,
    and update Notion based on commit messages.
    """
    try:
        payload_str = payload.decode('utf-8')
        payload_data = json.loads(payload_str)

        repository = payload_data.get('repository',
                                      {}).get('full_name',
                                              'Unknown repository')

        if event_type == 'push':
            commits = payload_data.get('commits', [])
            commit_count = len(commits)
            pusher = payload_data.get('pusher', {}).get('name', 'Unknown user')
            ref = payload_data.get('ref', '')
            branch = ref.replace('refs/heads/',
                                 '') if ref.startswith('refs/heads/') else ref

            # Logowanie webhooka do bazy
            webhook_log = WebhookLog(event_type=event_type,
                                     repository=repository,
                                     sender=pusher,
                                     branch=branch,
                                     commit_count=commit_count,
                                     payload=payload_str,
                                     timestamp=datetime.utcnow())
            db.session.add(webhook_log)
            db.session.commit()

            # Obsługa commitów i Notion
            for commit in commits:
                commit_message = commit.get('message', 'No commit message')
                commit_url = commit.get('url', '')
                send_commit_to_notion(commit_message=commit_message,
                                      repo_name=repository,
                                      author_name=pusher,
                                      commit_url=commit_url)

            logging.info(
                f"Stored GitHub {event_type} event for {repository}, branch: {branch}, commits: {commit_count}"
            )

        else:
            # Obsługa innych typów eventów
            webhook_log = WebhookLog(event_type=event_type,
                                     repository=repository,
                                     sender=payload_data.get('sender', {}).get(
                                         'login', 'Unknown user'),
                                     payload=payload_str,
                                     timestamp=datetime.utcnow())
            db.session.add(webhook_log)
            db.session.commit()

            logging.info(f"Stored GitHub {event_type} event for {repository}")

        return True

    except Exception as e:
        logging.error(f"Error processing GitHub webhook: {str(e)}")
        raise
