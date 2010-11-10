import re
import urllib2
from lxml import etree
import couchdb

def grab(url):
    f = urllib2.urlopen(url)
    if f.geturl() != url:
        raise Exception("Bad URL, got %s but expected %s" % (f.geturl(), url))
    return etree.parse(f, etree.HTMLParser())

def get_text_by_id(tree,id):
    ''' TODO figure out how to make this a method so we can use self instead of tree '''
    return tree.xpath('//*[@id="%s"]/text()' % id)[0]

def get_all_sessions():
    tree = grab('http://www.capitol.state.tx.us/Home.aspx')
    return tree.xpath("//*[@id='cboLegSess']/option/@value")

def get_current_session():
    return get_all_sessions()[0]

def get_bill(session, bill=None):
    url = session if bill is None else 'http://www.capitol.state.tx.us/BillLookup/History.aspx?LegSess=%s&Bill=%s' % (session, bill)
    tree = grab(url)
    bill = {}
    bill['url'] = url
    bill['name'] = get_text_by_id(tree, "usrBillInfoTabs_lblBill")
    bill['session'] = get_text_by_id(tree, "usrBillInfoTabs_lblItem1Data")
    bill['id'] = re.sub(r'[^-0-9a-zA-Z]', '', "%s-%s" % (bill['name'], bill['session']))
    bill['author'] = get_text_by_id(tree, "cellAuthors")
    bill['caption_text'] = get_text_by_id(tree, "cellCaptionText")
    bill['actions'] = [dict(
                    [(i, j) for (i,j) in
                    zip(['stage', 'description', 'comment', 'date', 'time', 'journal'],
                    [td.strip() for td in tr.xpath('./td/text()')]
                    ) if j]) for tr in tree.xpath('//table[@rules="rows"]//tr[@id]')]
    return bill
    return bill, tree

def get_house_bills_list(session):
    tree = grab('http://www.capitol.state.tx.us/Reports/Report.aspx?LegSess=%s&ID=housefiled' % session)
    return tree.xpath("//table//a/@href")

def get_senate_bills_list(session):
    gree = grab('http://www.capitol.state.tx.us/Reports/Report.aspx?LegSess=%s&ID=senatefiled' % session)
    return tree.xpath("//table//a/@href")


DATABASE = {
    'name': 'bills',
    'host': 'localhost',
    'port': '5984'
}

def couch_start():
    server = couchdb.client.Server()
    try:
        db = server.create(DATABASE['name'])
    except couchdb.PreconditionFailed as e:
        db = server[DATABASE['name']]
    return db

