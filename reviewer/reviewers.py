import re
from config import *
from config import MESSAGES as _
from requests import post, get
from requests.auth import HTTPBasicAuth

auth_token = HTTPBasicAuth(GITHUB_USERNAME, GITHUB_TOKEN)
reviewer_regex = re.compile(LIST_REVIEWER_REGEX, re.I)
approve_regex = re.compile(LIST_APPROVE_REGEX, re.I)


def get_instance(*args):
    """Get an instance of a reviewer based on MODE."""
    if MODE == 'list':
        return ListReviewer(*args)
    if MODE == 'quorum':
        return QuorumReviewer(*args)
    raise Exception('Invalid MODE')


class Reviewer(object):
    commit_status_url = 'https://api.github.com/repos/%(full_name)s/statuses/%(sha)s'

    def __init__(self, pull_request_url, comments_url, body):
        self.pull_request_url = pull_request_url
        self.comments_url = comments_url
        self.body = body
        self.pr_cache = None
        self.comments_cache = None

    def get_pull_request(self):
        """Get information about the pull request."""
        if not self.pr_cache:
            self.pr_cache = get(self.pull_request_url, auth=auth_token).json()
        return self.pr_cache

    def get_comments(self):
        """Get list of comments from a pull request."""
        if not self.comments_cache:
            self.comments_cache = get(self.comments_url, auth=auth_token).json()
        return self.comments_cache

    def set_commit_status(self, status, description, repo, sha):
        """Call the Github API to update the commit status for the pull request."""
        data = {
            'state': status,
            'description': description,
            'context': 'review',
        }
        url = self.commit_status_url % {'full_name': repo, 'sha': sha}
        return post(url, json=data, auth=auth_token)

    def set_success_commit_status(self, desc):
        """Update Github commit status as success."""
        info = self.get_pull_request()
        sha = info['head']['sha']
        repo = info['head']['repo']['full_name']
        return self.set_commit_status('success', desc, repo, sha)

    def set_pending_commit_status(self, desc):
        """Update Github commit status as pending."""
        info = self.get_pull_request()
        sha = info['head']['sha']
        repo = info['head']['repo']['full_name']
        return self.set_commit_status('pending', desc, repo, sha)

    def review(self):
        """Apply the specific reviewer rules and update Github's commit sattus."""
        raise NotImplementedError


class ListReviewer(Reviewer):
    def get_reviewers(self):
        """Extract a list of usernames from a reviewer list."""
        match = reviewer_regex.match(self.body)
        if not match:
            return []
        return [x.strip('@ ') for x in match.group(1).split(',')]

    def pending_reviewers(self):
        """Extract the reviewers from pull request body and call the Github
        API to check who is still pending reviews."""
        pending = self.get_reviewers()
        comments = self.get_comments()
        for comment in comments:
            username = comment['user']['login']
            if username in pending and approve_regex.search(comment['body']):
                pending.remove(username)
        return pending

    def review(self):
        """Search the pull request body text for a list of reviewers
        based on REVIEWER_LIST_REGEX regex."""
        pending_reviewers = self.pending_reviewers()

        if len(pending_reviewers) == 0:
            resp = self.set_success_commit_status(_['list_success_status_desc'])
            return '', resp.status_code

        msg = _['list_pending_status_desc'] % ', '.join(pending_reviewers)
        resp = self.set_pending_commit_status(msg)
        return msg, resp.status_code


class QuorumReviewer(Reviewer):
    def pending_reviews(self):
        """Get number of pending reviews from comments."""
        pending = QUORUM
        comments = self.get_comments()
        for comment in comments:
            username = comment['user']['login']
            if (approve_regex.search(comment['body'])
                    and (username in QUORUM_USERS or len(QUORUM_USERS) == 0)):
                pending = pending - 1
        return pending

    def review(self):
        """Pull request must have at least QUORUM number of reviews to pass the validation."""
        pending = self.pending_reviews()
        if pending == 0:
            msg = _['quorum_success_status_desc'] % QUORUM
            resp = self.set_success_commit_status(msg)
            return msg, resp.status_code

        msg = _['quorum_pending_status_desc'] % (pending, QUORUM)
        resp = self.set_pending_commit_status(msg)
        return msg, resp.status_code
