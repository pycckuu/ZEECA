from collections.abc import Callable

import tweepy
from pydantic import BaseModel, Field

from cdp_agentkit_core.actions.social.twitter import TwitterAction

POST_TWEET_PROMPT = """
This tool will post a tweet on Twitter. The tool takes the text of the tweet as input. Tweets can be maximum 280 characters."""


class PostTweetInput(BaseModel):
    """Input argument schema for twitter post tweet action."""

    tweet: str = Field(
        ...,
        description="The text of the tweet to post to twitter. Tweets can be maximum 280 characters.",
    )


def post_tweet(client: tweepy.Client, tweet: str) -> str:
    """Post tweet to Twitter.

    Args:
        client (tweepy.Client): The tweepy client to use.
        tweet (str): The text of the tweet to post to twitter. Tweets can be maximum 280 characters.

    Returns:
        str: A message containing the result of the post action and the tweet.

    """
    message = ""

    try:
        client.create_tweet(text=tweet)
        message = f"Successfully posted to Twitter:\n{tweet}"
    except tweepy.errors.TweepyException as e:
        message = f"Error posting to Twitter:\n{tweet}\n{e}"

    return message


class PostTweetAction(TwitterAction):
    """Twitter (X) post tweet action."""

    name: str = "post_tweet"
    description: str = POST_TWEET_PROMPT
    args_schema: type[BaseModel] | None = PostTweetInput
    func: Callable[..., str] = post_tweet