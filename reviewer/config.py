from os import environ as env

# ------------------------------------------------------------------------------
# Github username to be used to access the API.
# ------------------------------------------------------------------------------
GITHUB_USERNAME = env.get('GITHUB_USERNAME', '')

# ------------------------------------------------------------------------------
# Github access token to be used to access the API.
# The token need to have at least "repo:status" permission.
# ------------------------------------------------------------------------------
GITHUB_TOKEN = env.get('GITHUB_TOKEN', '')

# ------------------------------------------------------------------------------
# Execution mode, possible values are:
#   list:
#       search the pull request body text for a list of reviewers
#       based on LIST_REVIEWER_REGEX regex.
#   quorum:
#       pull request must have at least QUORUM number of approvals to
#       pass the review.
# ------------------------------------------------------------------------------
MODE = env.get('GITHUB_REVIEWER_MODE', 'quorum')

# ------------------------------------------------------------------------------
# For list mode. Regex used to detect reviewers for the pull request.
# By default this detect the following pattern (case insensitive):
#   Reviewers: @username1, @username2.
#   Reviewer: @username1, @username2.
#   Reviewers: @username1, @username2;
#   Reviewer: @username1, @username2;
# ------------------------------------------------------------------------------
LIST_REVIEWER_REGEX = "reviewer[s]?:\s+(.+?(?=[;|\.]))"

# ------------------------------------------------------------------------------
# Regex used to detect a reviewer approval.
# By default is the thumbs up emoji ":+1:".
# ------------------------------------------------------------------------------
LIST_APPROVE_REGEX = "\:\+1\:"

# ------------------------------------------------------------------------------
# For quorum mode. Number of people that must approve the pull request before
# passing the review. The approvals will be detected using
# the LIST_APROVE_REGEX regex.
# ------------------------------------------------------------------------------
QUORUM = 1

# ------------------------------------------------------------------------------
# For quorum mode. Usernames that can approve a pull request.
# If empty approval from any user is counted.
# ------------------------------------------------------------------------------
QUORUM_USERS = []

# ------------------------------------------------------------------------------
# Strings used in the app.
# ------------------------------------------------------------------------------
MESSAGES = {
    'list_success_status_desc': 'All reviewers approved.',
    'list_pending_status_desc': 'Pending reviews from %s.',

    'quorum_success_status_desc': 'Review quorum of %d met.',
    'quorum_pending_status_desc': '%d review(s) pending to meet the quorum of %d.'
}
