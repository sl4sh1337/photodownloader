import os
import vk
import requests
from vers import *
from PIL import Image
from io import BytesIO


class Downloader():
	APP_ID = 0 # Application id, created in vk development tools
    def _authenticate(self):
        session = vk.AuthSession(app_id=self.APP_ID, user_login=self.email, user_password=self.passwd,
                                 scope="messages,photos")
        self.api = vk.API(session)

    def _get_updates(self, updated_ts=None):
        self.r = requests.get(
            self.updates_url.format(self.server["server"], self.server["key"],
                                    self.server["ts"] if updated_ts is None else updated_ts))

    def __init__(self):
        while True:
            try:
                self.email = input("Input email: ")
                self.passwd = input("Input password: ")
                self._authenticate()
                break
            except vk.exceptions.VkAuthError:
                print("Error: wrong email or password")
        self.updates_url ="https://{}?act=a_check&key={}&ts={}&wait=25&mode=2&version=1"

    def exec(self):
        if 'download' not in os.listdir():
            os.mkdir('download')

        os.system("cls")
        self.server = self.api.messages.getLongPollServer()

        print(self.server)
        self._get_updates()

        while True:
            try:
                response = self.r.json()

                if 'updates' in response.keys():
                    for i in response["updates"]:
                        if i[0] == 4 and not (i[2] & 2) and i[7] and 'photo' in i[7].values():
                            attachments = self.api.messages.getById(message_ids=i[1], v=api_version)['items'][0]['attachments']
                            for attachment in attachments:
                                if attachment['type'] == 'photo':
                                    sizes = [int(x[6:]) for x in list(filter(lambda x: 'photo_' in x, attachment['photo']))]
                                    href = attachment['photo']['photo_' + str(max(sizes))]
                                    imgb = requests.get(href)
                                    img = Image.open(BytesIO(imgb.content))
                                    img.save("download/" + href[href.rfind("/") + 1:])
                                    print("Downloaded " + href[href.rfind("/") + 1:])
                    self._get_updates(response["ts"])
                else:
                    print("New server get:")
                    try:
                        self.server = self.api.messages.getLongPollServer()
                    except:
                        self._authenticate()
                        self.server = self.api.messages.getLongPollServer()

                    print(self.server)
                    self._get_updates()
            except Exception as e:
                print(e)
                self._authenticate()
                response = self.r.json()
                self._get_updates(response["ts"])
                pass


if __name__ == '__main__':
    downloader = Downloader()
    downloader.exec()
