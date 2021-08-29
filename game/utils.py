from datetime import datetime


def create_game_name():
    now = datetime.now()
    epoch = datetime.utcfromtimestamp(0)
    return int((now - epoch).total_seconds() * 1000)


def message_to_json(message):
    return {
        'author': message.author.username,
        'game_room': message.game_room.group_channel_name,
        'content': message.content,
        'timestamp': str(message.timestamp),
    }


def messages_to_json(messages):
    result = []
    for message in messages:
        result.append(message_to_json(message))
    return result
