import requests
import shutil
from bs4 import BeautifulSoup

class Minister(object):
    """ representation of a minister """
    def __init__(self, wikidata_id, photo_url):
        self.wikidata_id = wikidata_id
        self.photo_url = photo_url
        self.name = "<unset>"

    def get_label(self):
        """ gets and sets the ministers name """
        base_url = "http://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q16019&props=labels&format=json"
        payload = {"action" : "wbgetentities",
                   "ids": "Q" + str(self.wikidata_id),
                   "props": "labels",
                   "format": "json"
                  }
        response = requests.get(base_url, params=payload)
        self.name = response.json()["entities"]["Q" + str(self.wikidata_id)]["labels"]["de"]["value"]


    def get_real_image_url(self):
        """ checks the wikimedia page and gets the actual
        file url for the jpg file
        TODO: This should use an api or something instead
        """
        base_url = "https://commons.wikimedia.org/wiki/File:"
        image_url = base_url + self.photo_url
        response = requests.get(image_url)
        html = BeautifulSoup(response.text)
        return "https:" + html.find('a', text='Original file')['href']


    def get_picture(self):
        """ downloads the minister's picture """
        save_path = "./images/{0}.jpg".format(self.name.replace(' ', '-'))
        if self.photo_url:
            image_url = self.get_real_image_url()
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as local_file:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, local_file)

    def __repr__(self):
        return str(self.wikidata_id) + " " +  self.name


def get_ministers():
    """ executes a wikidata query to get all current ministers
    and creates objects out of them """
    base_url = "https://wdq.wmflabs.org/api"
    query = "CLAIM[39:248352]{" \
            + "(CLAIM[580] AND CLAIM[582:4294967295])"\
            + "OR (CLAIM[580] AND NOCLAIM[582])"\
            + "}"
    payload = {"q": query,
               "props": 18,
              }
    response = requests.get(base_url, params=payload)
    json_response = response.json()
    picture_file_names = json_response["props"]["18"]
    filenames_by_id = dict((prop[0], prop[2]) for prop in picture_file_names)
    all_ministers = []
    for qid in json_response["items"]:
        if qid in filenames_by_id.keys():
            all_ministers.append(Minister(qid, filenames_by_id[qid]))
        else:
            all_ministers.append(Minister(qid, None))
    for minister in all_ministers:
        minister.get_label()
        minister.get_picture()

if __name__ == "__main__":
    get_ministers()


