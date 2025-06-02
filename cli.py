#!/usr/bin/env python3
import os
import sys
import json
import argparse
import requests
from datetime import datetime

# Default server URL when running locally
DEFAULT_SERVER = "http://localhost:5000"

def get_server_url():
    """Get the server URL from environment or use default"""
    return os.environ.get("COMMITBOARD_SERVER", DEFAULT_SERVER)

def list_webhooks(args):
    """List recent webhooks"""
    server_url = get_server_url()
    limit = args.limit if args.limit else 10
    
    try:
        response = requests.get(f"{server_url}/api/webhooks?limit={limit}")
        response.raise_for_status()
        webhooks = response.json()
        
        if not webhooks:
            print("No webhooks found.")
            return
            
        # Print the webhooks in a table format
        print(f"{'ID':<5} {'Event Type':<15} {'Repository':<40} {'Sender':<20} {'Date':<20}")
        print("-" * 100)
        
        for webhook in webhooks:
            # Format the timestamp
            timestamp = webhook.get('timestamp', '')
            if timestamp:
                timestamp = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                
            print(f"{webhook['id']:<5} {webhook['event_type'][:15]:<15} {webhook['repository'][:40]:<40} {webhook['sender'][:20]:<20} {timestamp:<20}")
            
    except requests.RequestException as e:
        print(f"Error: Could not connect to the server at {server_url}")
        print(f"Details: {str(e)}")
        sys.exit(1)

def view_webhook(args):
    """View details of a specific webhook"""
    server_url = get_server_url()
    webhook_id = args.id
    
    try:
        response = requests.get(f"{server_url}/api/webhooks/{webhook_id}")
        response.raise_for_status()
        webhook = response.json()
        
        # Print the webhook details
        print(f"Webhook ID: {webhook['id']}")
        print(f"Event Type: {webhook['event_type']}")
        print(f"Repository: {webhook['repository']}")
        print(f"Sender: {webhook['sender']}")
        
        if webhook.get('branch'):
            print(f"Branch: {webhook['branch']}")
            
        if webhook.get('commit_count'):
            print(f"Commit Count: {webhook['commit_count']}")
            
        if webhook.get('timestamp'):
            timestamp = datetime.fromisoformat(webhook['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"Timestamp: {timestamp}")
            
        if args.payload and webhook.get('payload'):
            print("\nPayload:")
            print(json.dumps(webhook['payload'], indent=2))
            
    except requests.RequestException as e:
        print(f"Error: Could not connect to the server at {server_url}")
        print(f"Details: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="CommitBoard CLI - Manage GitHub webhook events")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List webhooks command
    list_parser = subparsers.add_parser("list", help="List recent webhooks")
    list_parser.add_argument("-l", "--limit", type=int, help="Limit the number of webhooks to display")
    list_parser.set_defaults(func=list_webhooks)
    
    # View webhook command
    view_parser = subparsers.add_parser("view", help="View webhook details")
    view_parser.add_argument("id", type=int, help="Webhook ID to view")
    view_parser.add_argument("-p", "--payload", action="store_true", help="Show full payload")
    view_parser.set_defaults(func=view_webhook)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the command or show help
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
