from amazonproduct import API
from wishlist import Wishlist
from helpers import is_empty
from mail import send_diff_update
from datetime import datetime
from operator import itemgetter
import config
import MySQLdb


def scrape_wish_list_items(list_id):
    """ Populate wish_list_items with data from wishlist """
    print "Scraping wishlist..."

    wish = Wishlist(list_id)
    item_ids = wish.get_list_items()

    wishlist_items = []

    api = API(locale='us')
    for item_id in item_ids:
        try:
            result = api.item_lookup(item_id, ResponseGroup="Large")
            for item in result.Items.Item:
                itm = { "title": item.ItemAttributes.Title, "price": item.Offers.Offer.OfferListing.Price.FormattedPrice, "amazonid": item.ASIN }
                wishlist_items.append(itm)
        except:
            print "!!! Failed getting " + item_id

    print "Completed scraping."
    return wishlist_items


def populate(itms):
    """ Populate table if user items is empty """
    print "Populating..."
    
    sql = "INSERT INTO items (title, price, amazonid, userid, date_added) VALUES "
    values = ""

    i = 0
    for itm in itms:
        values += "('%s', '%s', '%s', '%d', '%s')" % (itm["title"], itm["price"], itm["amazonid"], 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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

    changed_items = []
    
    j = 0
    for itm in itms:
        itm_price = float(str(itm["price"])[1:])
        dbitm_price = float(str(dbitms[j]["price"])[1:])
        if itm_price != dbitm_price:
            itmlist = [itm, dbitms[j]]
            changed_items.append(itmlist)
        j += 1

    print "Done comparing."

    return changed_items

def check_new(itms, dbitms):
    """ Check if there are amazonids not in the database """
    print "Checking for new items to add..."

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
        j += 1

    if is_empty(newitms):
        print "No new items."
    else:
        print "New items found."
        insert_new_items(newitms)


def check_delete(itms, dbitms):
    """ Delete items no longer in list. """
    print "Checking for old items to delete..."

    def delete_old_items(old_ids):
        db = MySQLdb.connect(config.database.HOST, config.database.USER, config.database.PASSWD, config.database.DB)
        cursor = db.cursor()

        for oid in old_ids:
            sql = "DELETE FROM items WHERE amazonid = '" + oid + "'"
            try:
                cursor.execute(sql)
            except:
                db.rollback()
                
        db.commit()
        db.close()

        print "Done deleting old items."

    dbids = []
    ids = []
    oldids = []

    for itm in dbitms:
        dbids.append(itm["amazonid"])

    for itm in itms:
        ids.append(itm["amazonid"])

    for i in dbids:
        if i not in ids:
            oldids.append(i)

    if is_empty(oldids):
        print "No old items."
    else:
        print "Old items found."
        delete_old_items(oldids)

def format_data(data):
    """ Format data in same form as wish_list_items for easy comparing """
    itms = []
    for item in data:
        itm = { "title": item[0], "price": item[1], "amazonid": item[2] }
        itms.append(itm)

    itms = sorted(itms, key=itemgetter("amazonid"))
    return itms

def inform_different(diff):
    """ Send email with lowered prices """
    print "Preparing updated information..."

    diff_info = []
    inc_diff_info = []

    def update_items(d):
        print "Updating items..."
        for itm in d:
            db = MySQLdb.connect(config.database.HOST, config.database.USER, config.database.PASSWD, config.database.DB)
            cursor = db.cursor()

            sql = "UPDATE items SET price='%s' WHERE amazonid='%s'" % (itm[3], itm[1])

            cursor.execute(sql)
            db.commit()
            db.close()

        print "Done updating database."
    
    new_price = 0

    for difference in diff:
        new_price = float(str(difference[0]["price"])[1:])
        old_price = float(str(difference[1]["price"])[1:])
        price_diff = ""
        if new_price < old_price:
            print "Found a dropped price. Item " + difference[0]["title"] + " dropped."
            price_diff = old_price - new_price
            l = [difference[0]["title"], difference[0]["amazonid"], ("%.2f" % (price_diff)), difference[0]["price"]]
            diff_info.append(l)
        elif new_price > old_price:
            print "Found a price increase. Item " + difference[0]["title"] + " increased."
            price_diff = new_price - old_price
            l = [difference[0]["title"], difference[0]["amazonid"], ("%.2f" % (price_diff)), difference[1]["price"]]
            inc_diff_info.append(l)

    if not is_empty(diff_info):
        print "Sending email with price drops."
        send_diff_update(diff_info)
        update_items(diff_info)
    
    if not is_empty(inc_diff_info):
        print "Updating price increases."
        update_items(inc_diff_info)

    if is_empty(diff_info) and is_empty(inc_diff_info):
        print "No price changes found. This should really ever happen."

def main():
    wishlist_items = scrape_wish_list_items(config.info.LISTID)
    wishlist_items = sorted(wishlist_items, key=itemgetter("amazonid"))

    print wishlist_items

    def get_data():
        db = MySQLdb.connect(config.database.HOST, config.database.USER, config.database.PASSWD, config.database.DB)
        cursor = db.cursor()

        cursor.execute("SELECT title, price, amazonid FROM items where userid = 1")

        data = cursor.fetchall()

        db.close()

        return data

    print format_data(get_data())

    if is_empty(get_data()):
        populate(wishlist_items)
    else:
        check_new(wishlist_items, format_data(get_data()))
        check_delete(wishlist_items, format_data(get_data()))
        different = compare(wishlist_items, format_data(get_data()))
        if is_empty(different):
            # Nothing is different, don't do anything
            print "No changes found."
        else:
            inform_different(different)


if __name__ == "__main__":
    main()
