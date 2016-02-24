from amazonproduct import API
from wishlist import Wishlist
from helpers import is_empty
import config
import MySQLdb

wish_list_items = []

def scrape_wish_list_items(list_id):
    wish = Wishlist(list_id)
    item_ids = wish.get_list_items()
    api = API(locale='us')
    for item_id in item_ids:
        try:
            result = api.item_lookup(item_id, ResponseGroup="Large")
            for item in result.Items.Item:
                if hasattr(item.ItemAttributes, 'ListPrice'):
                    itm = { "title": item.ItemAttributes.Title, "price": item.ItemAttributes.ListPrice.FormattedPrice, "amazonid": item.ASIN }
                    wish_list_items.append(itm)
        except:
            print "!!! Failed getting " + item_id


def populate(itms):
    """ Populate table if user items is empty """
    print "Populating..."
    
    sql = "INSERT INTO items (title, price, amazonid, userid) VALUES "
    values = ""

    i = 0
    for itm in itms:
        values += "('%s', '%s', '%s', '%d')" % (itm["title"], itm["price"], itm["amazonid"], 1)
        values += "," if i != len(itms) - 1 else ";"
        i += 1

    sql = sql + values

    db = MySQLdb.connect(config.database.HOST, config.database.USER, config.database.PASSWD, config.database.DB)
    cursor = db.cursor()

    try:
        cursor.execute(sql)
        db.commit()
        print "Completed populating."
    except:
        db.rollback()
        print "Error, rolling back."

    db.close()

def compare(itms, dbitms):
    """ Compare new data to old for changes """
    print "Comparing..."

    print "Done comparing."

def check_new(itms, dbitms):
    """ Check if there are amazonids not in the database """
    print "Checking for new items..."

    def insert_new_items(new_itms):
        sql = "INSERT INTO items (title, price, amazonid, userid) VALUES "
        db = MySQLdb.connect(config.database.HOST, config.database.USER, config.database.PASSWD, config.database.DB)
        cursor = db.cursor()

        k = 0
        values = ""
        for itm in new_itms:
            values += "('%s', '%s', '%s', '%d')" % (itm["title"], itm["price"], itm["amazonid"], 1)
            values += "," if k != len(new_itms) - 1 else ";"
            k += 1

        sql = sql + values

        try:
            print sql
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

        db.close()

        print "Done inserting new items."

    dbids = []
    ids = []
    newitms = []

    for itm in dbitms:
        dbids.append(itm["amazonid"])

    for itm in itms:
        ids.append(itm["amazonid"])

    j = 0
    for i in ids:
        if i not in dbids:
            newitms.append(itms[j])

    if is_empty(newitms):
        print "No new items."
    else:
        insert_new_items(newitms)
        print "New items found."


def check_delete(itms, dbitms):
    """ Delete items no longer in list. """
    print "Checking for old items to delete..."

def format_data(data):
    """ Format data in same form as wish_list_items for easy comparing """
    itms = []
    for item in data:
        itm = { "title": item[0], "price": item[1], "amazonid": item[2] }
        itms.append(itm)

    return itms

def main():
    scrape_wish_list_items(config.info.LISTID)

    db = MySQLdb.connect(config.database.HOST, config.database.USER, config.database.PASSWD, config.database.DB)
    cursor = db.cursor()

    cursor.execute("SELECT title, price, amazonid FROM items where userid = 1")

    data = cursor.fetchall()

    if is_empty(data):
        populate(wish_list_items)
    else:
        formatted_data = format_data(data)
        check_new(wish_list_items, formatted_data)
        compare(wish_list_items, formatted_data)

    db.close()

if __name__ == "__main__":
    main()
