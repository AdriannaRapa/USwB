import hmac
import hashlib
import json
import logging
from models import WebhookLog

def validate_github_signature(payload, signature, secret):
    """
    Validate the GitHub webhook signature against the payload.
    
    Args:
        payload (bytes): The raw webhook payload
        signature (str): The signature from X-Hub-Signature-256 header
        secret (str): The webhook secret
    
    Returns:
        bool: True if the signature is valid, False otherwise
    """
    if not signature or not signature.startswith("sha256="):
        return False
    
    # Get the hash from the signature
    received_hash = signature.split("sha256=")[1]
    
    # Calculate the expected hash
    secret_bytes = secret.encode('utf-8')
    hmac_gen = hmac.new(secret_bytes, payload, hashlib.sha256)
    expected_hash = hmac_gen.hexdigest()
    
    # Compare hashes using a constant-time comparison function
    return hmac.compare_digest(received_hash, expected_hash)

def format_json(json_str):
    """
    Format JSON string for pretty display
    
    Args:
        json_str (str): JSON string
    
    Returns:
        str: Formatted JSON string
    """
    try:
        parsed = json.loads(json_str)
        return json.dumps(parsed, indent=2, sort_keys=True)
    except:
        return json_str

def get_webhook_data(limit=50):
    """
    Get webhook data for the API
    
    Args:
        limit (int): Maximum number of webhook logs to return
    
    Returns:
        list: List of webhook data dictionaries
    """
    webhooks = WebhookLog.query.order_by(WebhookLog.timestamp.desc()).limit(limit).all()
    return [webhook.to_dict() for webhook in webhooks]

def parse_payload_summary(webhook):
    """
    Extract a summary from the webhook payload
    
    Args:
        webhook (WebhookLog): Webhook log object
    
    Returns:
        dict: Summary information
    """
    try:
        payload = json.loads(webhook.payload)
        summary = {
            "repository": webhook.repository,
            "event_type": webhook.event_type,
            "sender": webhook.sender,
            "timestamp": webhook.timestamp
        }
        
        # Add event-specific information
        if webhook.event_type == 'push':
            summary["branch"] = webhook.branch
            summary["commit_count"] = webhook.commit_count
            
            # Get the last commit message
            if "commits" in payload and len(payload["commits"]) > 0:
                summary["last_commit_message"] = payload["commits"][0].get("message", "")
        
        return summary
    except Exception as e:
        logging.error(f"Error parsing payload summary: {str(e)}")
        return {
            "error": "Could not parse payload",
            "repository": webhook.repository,
            "event_type": webhook.event_type
        }
