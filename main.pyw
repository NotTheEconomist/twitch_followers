#!/usr/bin/python3
import api
import tkinter as tk

from tkinter import ttk

WIDTH = 210
HEIGHT = 410


class App(tk.Tk):
    """App is little more than a GUI wrapper around the API"""

    # time in ms between runs
    TICK = 1000  # 1s

    def __init__(self, *args, channel_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_name = channel_name
        self.followers = self.get_followers()
        self.clear_new_followers()
        self.device = api.get_device("Note III")  # for pushbullet integration
        self.new_box = ttk.Label(master=self,
                                 text=self.new_followers_output)
        self.clear_new_followers()
        self.viewers = tk.IntVar(master=self, value=0)  # updated with api.get_viewers
        self.button_clear_new = ttk.Button(master=self,
                                           command=self.clear_new_followers,
                                           text="Clear New Follower")
        self.label_num_followers = ttk.Label(master=self,
                                             text=self.num_followers)
        self.label_viewers = ttk.Label(master=self,
                                       textvariable=self.viewers)
        self.tick()

        ttk.Label(text="New Followers:").grid(row=0, columnspan=5)
        self.new_box.grid(row=1, rowspan=18, columnspan=5)
        ttk.Label(text="V:").grid(row=19, column=0, sticky=tk.E)
        self.label_viewers.grid(row=19, column=1)
        self.button_clear_new.grid(row=19, column=2)
        ttk.Label(text="F:").grid(row=19, column=3, sticky=tk.E)
        self.label_num_followers.grid(row=19, column=4)

        self.columnconfigure(0, minsize=20)
        self.columnconfigure(1, minsize=20)
        self.columnconfigure(2, minsize=120)
        self.columnconfigure(3, minsize=20)
        self.columnconfigure(4, minsize=20)

        for rownum in range(20):
            self.rowconfigure(rownum, minsize=20)

        # ttk.Button(master=self, command=self.debug,
        #            text="DEBUG").grid(row=10, column=0)

    @property
    def new_followers(self):
        return [follower for follower in self.followers if follower.new]

    @property
    def new_followers_output(self):
        """Pretty output of new_followers"""
        if not self.new_followers:
            return ''
        return "\n".join([f.name for f in sorted(self.new_followers)])

    @property
    def num_followers(self):
        return str(len(self.followers))

    def debug(self):
        for follower in self.followers:
            print(follower.name, follower.new)

    def get_followers(self):
        return api.get_followers(self.channel_name)

    def clear_new_followers(self):
        for follower in self.followers:
            follower.see()

    def tick(self):
        # Re-run after self.TICK ms
        self.after(self.TICK, self.tick)

        # Update self.followers with results of API calls to Twitch
        existing = self.followers
        updated = self.get_followers()
        new = updated - existing  # set difference here showing only new followers
        lost = existing - updated  # set defference here showing followers that unfollowed
        for follower in lost:
            self.followers.remove(follower)
        self.followers.update(new)

        # Update the GUI labels with new output
        self.viewers.set(api.get_viewers(self.channel_name))
        self.new_box.configure(text=self.new_followers_output)
        self.label_num_followers.configure(text=self.num_followers)

        # If you have new followers: push the info to your pushbullet device
        if new:
            title = "New Followers:"
            body = "\n".join([follower.name for follower in new])
            api.push_note_to_device(self.device, title, body)


if __name__ == "__main__":
    channel_name = "nottheeconomisttv"
    app = App(channel_name=channel_name)
    app.geometry("{}x{}".format(WIDTH, HEIGHT))
    app.mainloop()
