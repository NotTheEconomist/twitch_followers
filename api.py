import requests

pb_secret_key = "MY SECRET PUSHBULLET API KEY"

twitch_headers = {"Accept": "application/vnd.twitchtv.3+json"}
pb_headers = {"Authorization": "Bearer {}".format(pb_secret_key),
              "Content-Type": "application/json"}

twitch_base_point = r"https://api.twitch.tv/kraken"
pb_base_point = r"https://api.pushbullet.com/v2"


class Follower(object):
    """Follower objects are little more than wrappers around a string with a one-time unique `new` flag

    composing the object like this allows the application to avoid the common idiom of keeping a list of
    items that have been seen. Use `new` to check this flag, and `see()` to mark it as not new forever.
    """

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
    """get_followers expects the name of a twitch channel and issues a command via the Twitch API that
    returns a set of that channel's followers (as Follower objects).
    """
    request_target = "/".join([twitch_base_point, "channels", channel_name, "follows"])
    r = requests.get(request_target, headers=twitch_headers)
    return {Follower(d['user'].get("display_name")) for d in r.json()['follows']}


def get_viewers(channel_name):
    """get_viewers expects the name of a twitch channel and issues a command via the Twitch API that
    returns a list of that channel's viewers (as strings).
    """
    request_target = "/".join([twitch_base_point, "streams", channel_name])
    r = requests.get(request_target, headers=twitch_headers)
    stream = r.json()['stream']
    if stream is None:
        return 0
    else:
        return stream['viewers']


def get_device(nickname):
    """get_device returns a device object from the PushBullet API, given the nickname you should have
    already assigned to it through PushBullet.
    """
    r = requests.get("{}/devices".format(pb_base_point), headers=pb_headers)
    match = [d for d in r.json()['devices'] if
             nickname.lower() in d.get('nickname', '').lower()]
    if len(match) == 1:
        return match[0]
    elif not match:
        raise ValueError("nickname returned no results")
    else:
        raise ValueError("nickname is not unique, returns {} results".format(len(match)))


def push_note_to_device(device, title, body):
    """push_note_to_device expects a device object (from get_device) and a title and body for the
    push, then submits a push notification through the PushBullet API to that device.
    """
    payload = {"type": "note", "title": title, "body": body}
    if device is not None:
        payload.update({"device_iden": device['iden']})
    p = requests.post("{}/pushes".format(pb_base_point), headers=pb_headers, json=payload)
    return p


if __name__ == "__main__":
    print(get_followers("nottheeconomisttv"))
    note = get_device("note III")
    push_note_to_device(note, "blah", "boo")
