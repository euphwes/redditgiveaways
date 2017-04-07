from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from ..settings import REDDIT_SECRET, REDDIT_CLIENT_ID

import praw, random
from datetime import datetime

# ----------------------------------------------------------------------------------------------------------------------

def comment_to_dict(comment):
    return {
        'user': '/u/{}'.format(comment.author.name),
        'url': 'http://www.reddit.com/{}'.format(comment.permalink()),
        'first_line': '{}...'.format(comment.body.splitlines()[0])
    }

# ----------------------------------------------------------------------------------------------------------------------

@csrf_exempt
def run_thread_giveaway(request):

    try:
        url = request.POST['url']
        if not url:
            return HttpResponseBadRequest("Forgot to submit a URL")
    except KeyError as e:
        return HttpResponseBadRequest("Forgot to submit a URL")

    try:
        if not request.POST['date_limit']:
            date_limit = datetime.utcnow().timestamp()
        else:
            date_limit = int(request.POST['date_limit'])
    except KeyError as e:
        date_limit = datetime.utcnow().timestamp()

    try:
        filter_text = request.POST['filter_text']
    except KeyError as e:
        filter_text = None

    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                         client_secret=REDDIT_SECRET,
                         user_agent='/r/cubers giveaway helper v0.1 (by /u/euphwes)')

    try:
        thread = reddit.submission(id=praw.models.Submission.id_from_url(url))
        thread.comments.replace_more(limit=0)
    except praw.exceptions.ClientException as e:
        return HttpResponseBadRequest(str(e))

    result = {
        "eligible_comments": list(),
        "duplicate_user_comments": list(),
        "filtered_comments": list(),
        "too_new_comments": list(),
        "winner": None,
        "thread_title": thread.title,
        "thread_url": url
    }

    eligible_users = dict()

    comments = thread.comments[:]
    comments.sort(key=lambda x: x.created_utc, reverse=True)

    for comment in comments:
        if comment.created_utc > date_limit:
            result['too_new_comments'].append(comment_to_dict(comment))
            continue

        if filter_text and filter_text in comment.body.splitlines()[0]:
            result['filtered_comments'].append(comment_to_dict(comment))
            continue

        if comment.author.name not in eligible_users:
            eligible_users[comment.author.name] = comment.id
            result['eligible_comments'].append(comment_to_dict(comment))
        else:
            result['duplicate_user_comments'].append(comment_to_dict(comment))

    if result['eligible_comments']:
        result['winner'] = random.choice(result['eligible_comments'])

    return JsonResponse(result)
