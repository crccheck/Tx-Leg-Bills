import re
import urllib2
from lxml import etree
import couchdb

DATABASE = {
    'name': 'bills',
    'host': 'localhost',
    'port': '5984'
}

def grab(url):
    '''shortcut to pull a url as a element tree object ready for transversal'''
    f = urllib2.urlopen(url)
    #print "Pulling %s Bytes from %s" % (f.headers.dict['content-length'], url)
    if f.geturl() != url:
        raise Exception("Bad URL, got %s but expected %s" % (f.geturl(), url))
    return etree.parse(f, etree.HTMLParser())

def get_text_by_id(tree,id):
    '''shortcut that works similar to javascript's getElementById(id).innerHTML
    TODO figure out how to make this a method so we can use self instead of tree '''
    return tree.xpath('//*[@id="%s"]/text()' % id)[0]

def get_all_sessions():
    '''Figure out the names of the legislative sessions'''
    tree = grab('http://www.capitol.state.tx.us/Home.aspx')
    return tree.xpath("//*[@id='cboLegSess']/option/@value")

def get_current_session():
    '''Figure out what the current legislative session is'''
    return get_all_sessions()[0]

def get_bill(session, bill=None):
    '''return a dict that represents a bill and the id for the bill'''
    url = session if bill is None else 'http://www.capitol.state.tx.us/BillLookup/History.aspx?LegSess=%s&Bill=%s' % (session, bill)
    tree = grab(url)
    bill = {}
    bill['url'] = url
    bill['name'] = get_text_by_id(tree, "usrBillInfoTabs_lblBill")
    bill['session'] = get_text_by_id(tree, "usrBillInfoTabs_lblItem1Data")
    bill['author'] = get_text_by_id(tree, "cellAuthors")
    bill['caption_text'] = get_text_by_id(tree, "cellCaptionText")
    bill['subject'] = [dict(zip(['subject_name', 'subject_id'],re.match(r'(.*) \((.*)\)',t).groups()))
                        for t in tree.xpath('//*[@id="cellSubjects"]')[0].itertext()]
    bill['action'] = [dict(
                    [(i, j) for (i,j) in
                    zip(['stage', 'description', 'comment', 'date', 'time', 'journal'],
                    [td.strip() for td in tr.xpath('./td/text()')]
                    ) if j]) for tr in tree.xpath('//table[@rules="rows"]//tr[@id]')]
    id = re.sub(r'[^-0-9a-zA-Z]', '', "%s-%s" % (bill['session'], bill['name']))
    return bill, id, tree

def get_house_bills_list(session):
    tree = grab('http://www.capitol.state.tx.us/Reports/Report.aspx?LegSess=%s&ID=housefiled' % session)
    return tree.xpath("//table//a/@href")

def get_senate_bills_list(session):
    tree = grab('http://www.capitol.state.tx.us/Reports/Report.aspx?LegSess=%s&ID=senatefiled' % session)
    return tree.xpath("//table//a/@href")

def get_today_bills_list():
    tree = grab('http://www.capitol.state.tx.us/Reports/Report.aspx?&ID=todayfiled')
    return tree.xpath("//table//a/@href")

def get_session_bills(session = None):
    if session is None:
        session = get_current_session()
    db = couch_start('bills_%s' % session)

    bill_list = get_house_bills_list(session)
    bill_list.extend(get_senate_bills_list(session))
    n = len(bill_list)
    if n:
        for i, url in enumerate(bill_list, start=1):
            bill, id, _ = get_bill(url)
            doc = db.get(id)
            if doc:
                print "%d / %d Update %s" % (i, n, id)
                doc.update(bill)
                db[doc.id] = doc
            else:
                print "%d / %d Save %s" % (i, n, id)
                db[id] = bill
    else:
        print "No Bills To Pull"

def get_today_bills():
    db = couch_start()
    bill_list = get_today_bills_list()
    n = len(bill_list)
    if n:
        for i, url in enumerate(bill_list, start=1):
            bill, id, _ = get_bill(url)
            doc = db.get(id)
            if doc:
                print "%d / %d Update %s" % (i, n, id)
                doc.update(bill)
                db[doc.id] = doc
            else:
                print "%d / %d Save %s" % (i, n, id)
                db[id] = bill
    else:
        print "No Bills To Pull"

def couch_start(dbname = None):
    if dbname is None:
        dbname = DATABASE['name']
    print 'dbname is ',dbname
    dbname = dbname.lower()
    server = couchdb.client.Server()
    try:
        db = server.create(dbname)
    except couchdb.PreconditionFailed as e:
        db = server[dbname]
    return db

if __name__ == "__main__":
    pass
