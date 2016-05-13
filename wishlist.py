from bs4 import BeautifulSoup
import urllib

class Wishlist(object):

    def __init__(self, list_id):
        self.list_id = list_id
        self.list_url = "https://amzn.com/w/" + list_id
        self.item_ids = []

    def get_list_items(self):
        urldata = urllib.urlopen(self.list_url)
        rawhtml = urldata.read()
        html = BeautifulSoup(rawhtml, "lxml")

        for dataobject in html.find_all("div", { "class" : "a-fixed-left-grid a-spacing-large" }):
            html_id = dataobject["id"][5:]

            aid = "itemName_" + html_id
            url_object = dataobject.find("a", id=aid)
            if url_object is not None:
                self.item_ids.append(url_object["href"][4:][:10])

        return self.item_ids
