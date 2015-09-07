# Headers:
# Accept: application/vnd.twitchtv.3+json

import requests

pb_secret_key = "MY SECRET PUSHBULLET API KEY"

twitch_headers = {"Accept": "application/vnd.twitchtv.3+json"}
pb_headers = {"Authorization": "Bearer {}".format(pb_secret_key),
              "Content-Type": "application/json"}

channel_name = "nottheeconomisttv"
twitch_base_point = r"https://api.twitch.tv/kraken"
pb_base_point = r"https://api.pushbullet.com/v2"


class Follower(object):

    def __init__(self, name, is_new=True):
        self.name = name
        self.__new = is_new

    @property
    def new(self):
        return self.__new

    def see(self):
        self.__new = False

    def __hash__(self):
        return hash(self.name)

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __eq__(self, other):
        return self.name == other.name


def get_followers(channel_name):
    request_target = "/".join([twitch_base_point, "channels", channel_name, "follows"])
    r = requests.get(request_target, headers=twitch_headers)
    return {Follower(d['user'].get("display_name")) for d in r.json()['follows']}


def get_viewers(channel_name):
    request_target = "{}/streams/{}".format(twitch_base_point, channel_name)
    r = requests.get(request_target, headers=twitch_headers)
    stream = r.json()['stream']
    if stream is None:
        return 0
    else:
        return stream['viewers']


def get_device(nickname):
    r = requests.get("{}/devices".format(pb_base_point), headers=pb_headers)
    match = [d for d in r.json()['devices'] if
             nickname.lower() in d.get('nickname', '').lower()]
    if len(match) == 1:
        return match[0]
    else:
        raise ValueError(
            "nickname is not unique, returns {} results".format(len(match)))


def push_note_to_device(device, title, body):
    payload = {"type": "note", "title": title, "body": body}
    if device is not None:
        payload.update({"device_iden": device['iden']})
    p = requests.post("{}/pushes".format(pb_base_point), headers=pb_headers, json=payload)
    return p


if __name__ == "__main__":
    print(get_followers(channel_name))
    note = get_device("note III")
    push_note_to_device(note, "blah", "boo")
