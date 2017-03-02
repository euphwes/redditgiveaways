from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from ..settings import REDDIT_SECRET, REDDIT_CLIENT_ID

import praw

# ----------------------------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------------------------

@csrf_exempt
def run_thread_giveaway(request):

    try:
        url = request.POST['url']
        if not url:
            return HttpResponseBadRequest("Forgot to submit a URL")
    except KeyError as e:
        return HttpResponseBadRequest("Forgot to submit a URL")

    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                         client_secret=REDDIT_SECRET,
                         user_agent='/r/cubers giveaway helper v0.1 (by /u/euphwes)')

    thread = reddit.submission(url=url)
    thread.comments.replace_more(limit=0)

    result = {
        "eligible_comments": list(),
        "duplicate_user_comments": list(),
        "filtered_comments": list(),
        "winner": dict()
    }

    eligible_users = dict()

    for comment in thread.comments:
        if comment.author.name not in eligible_users:
            eligible_users[comment.author.name] = comment.id
            result['eligible_comments'].append({
                'user': '/u/{}'.format(comment.author.name),
                'url': 'http://www.reddit.com/{}'.format(comment.permalink()),
                'first_line': '{}...'.format(comment.body.splitlines()[0])
            })
        else:
            result['duplicate_user_comments'].append({
                'user': '/u/{}'.format(comment.author.name),
                'url': 'http://www.reddit.com/{}'.format(comment.permalink()),
                'first_line': '{}...'.format(comment.body.splitlines()[0])
            })

    return JsonResponse(result)
