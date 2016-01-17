from flask import Flask, request
from reviewers import get_instance


app = Flask(__name__)


@app.route("/ping")
def ping():
    return "pong"


@app.route("/", methods=['POST'])
def index():
    """Execute specific function based on X-GitHub-Event header."""
    event = request.headers.get('X-GitHub-Event')
    if not event:
        return 'Bad Request', 400

    payload = request.json
    if event == 'pull_request':
        return pull_request(payload)
    elif event == 'issue_comment':
        return issue_comment(payload)
    else:
        return 'Event not supported', 200


def pull_request(payload):
    """Responds to 'pull_request' events."""
    try:
        action = payload['action']
        pull_request_url = payload['pull_request']['url']
        body = payload['pull_request']['body']
        comments_url = payload['pull_request']['comments_url']
    except KeyError:
        return 'Bad Request', 400

    if action not in ['opened', 'reopened']:
        return 'Nothing to do', 200

    return get_instance(pull_request_url, comments_url, body).review()


def issue_comment(payload):
    """Responds to 'issue_comment' events."""
    try:
        body = payload['issue']['body']
        comments_url = payload['issue']['comments_url']
        pull_request_url = payload['issue']['pull_request']['url']
    except KeyError:
        return 'Bad Request', 400

    return get_instance(pull_request_url, comments_url, body).review()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
