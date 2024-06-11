import requests
import json
import logging

# APIキーを取得
config = json.load(open('config.json'))
logger = logging.getLogger(__name__)

def get_top_headlines(api_key, country='jp', category='general', page_size=5):
    base_url = 'https://newsapi.org/v2/top-headlines'
    headers = {'X-Api-Key': api_key}
    params = {
        'country': country,
        'category': category,
        'page_size': page_size
    }

    response = requests.get(base_url, headers=headers, params=params)
    data = response.json()

    if data['status'] != 'ok':
        raise Exception(f"API error: {data['message']}")

    return data['articles']


def post_to_discord(webhook_url, news, include_title=True):
    for article in news:
        try:
            message_content = f"{article['title']}\n{article['description']}\nRead more: {article['url']}"

            payload = {
                'content': message_content
            }

            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()

            if response.status_code != 204:
                logger.error(f"Failed to post news: Status code {response.status_code}")
            else:
                logger.info(f"Successfully posted news: {article['title']}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error posting news: {e}")

        except Exception as e:
            logger.exception(e)


def is_valid_webhook_url(webhook_url):
    test_message = "This is a test message."

    payload = {
        'content': test_message
    }

    response = requests.post(webhook_url, json=payload)

    if response.status_code == 204:
        return True
    else:
        return False


def main():
    # DiscordのWebhook URLを読み込む
    webhook_url = config['webhook']

    # DiscordのWebhookのURL
    if not is_valid_webhook_url(webhook_url):
        logger.error("Invalid Discord webhook URL.")
        return

    # News APIのAPIキーを読み込
    api_key = config['api_key']

    # トップニュースを取得
    try:
        news = get_top_headlines(api_key, country='jp', category='general')
    except Exception as e:
        logger.exception(e)
        return

    if news:
        # Discordにニュースを投稿
        post_to_discord(webhook_url, news)
    else:
        logger.error("Failed to get top headlines.")


if __name__ == "__main__":
    main()
