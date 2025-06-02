import os
import json
import logging
import hmac
import hashlib
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from webhook_handler import process_github_webhook
from models import db, WebhookLog
from utils import validate_github_signature, get_webhook_data, format_json

# Create and configure the app
app = Flask(__name__)
app.secret_key = os.environ.get("GITHUB_WEBHOOK_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


# Register custom template filters
@app.template_filter('from_json')
def from_json_filter(value):
    """Convert a JSON string to a Python object"""
    try:
        return json.loads(value)
    except:
        return None


@app.template_filter('pretty_json')
def pretty_json_filter(value):
    """Format JSON string for pretty display"""
    return format_json(value)


# Configure SQLite database for storing webhook logs
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///commitboard.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db.init_app(app)

# Create tables within app context
with app.app_context():
    db.create_all()


# Main page - shows recent webhooks and app status
@app.route("/")
def index():
    recent_webhooks = WebhookLog.query.order_by(
        WebhookLog.timestamp.desc()).limit(10).all()
    return render_template("index.html", webhooks=recent_webhooks)


# Webhook endpoint for GitHub push events
@app.route("/webhook/github", methods=["POST"])
def github_webhook():
    # Get GitHub webhook secret from environment
    webhook_secret = os.environ.get("GITHUB_WEBHOOK_SECRET")

    if not webhook_secret:
        logging.warning("GitHub webhook secret not configured")
        return jsonify({"error": "Webhook secret not configured"}), 500

    # Get the signature from the headers
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        logging.warning("No signature provided in GitHub webhook")
        return jsonify({"error": "No signature provided"}), 401

    # Get the raw payload
    payload = request.get_data()

    # Validate the signature
    if not validate_github_signature(payload, signature, webhook_secret):
        logging.warning("Invalid GitHub webhook signature")
        return jsonify({"error": "Invalid signature"}), 401

    # Process the webhook
    try:
        event_type = request.headers.get("X-GitHub-Event", "unknown")
        process_github_webhook(payload, event_type)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logging.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500


# View webhook details
@app.route("/webhook/<int:webhook_id>")
def webhook_details(webhook_id):
    webhook = WebhookLog.query.get_or_404(webhook_id)
    return render_template("webhook_details.html", webhook=webhook)


# API endpoint to get all webhooks (for CLI tool)
@app.route("/api/webhooks", methods=["GET"])
def api_webhooks():
    limit = request.args.get("limit", default=50, type=int)
    webhooks = get_webhook_data(limit)
    return jsonify(webhooks)


# API endpoint to get a specific webhook by ID (for CLI tool)
@app.route("/api/webhooks/<int:webhook_id>", methods=["GET"])
def api_webhook_by_id(webhook_id):
    webhook = WebhookLog.query.get(webhook_id)
    if not webhook:
        return jsonify({"error": "Webhook not found"}), 404
    return jsonify(webhook.to_dict())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
