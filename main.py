import urllib2
from lxml import etree

def grab(url):
    f = urllib2.urlopen(url)
    return etree.parse(f, etree.HTMLParser())

def get_simple_text(tree,id):
    ''' TODO figure out how to make this a method so we can use self instead of tree '''
    print 'hi', tree.xpath('//*[@id="%s"]/text()' % id)[0]
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
    bill['name'] = get_simple_text(tree, "usrBillInfoTabs_lblBill")
    bill['author'] = get_simple_text(tree, "cellAuthors")
    bill['caption_text'] = get_simple_text(tree, "cellCaptionText")
    return bill

def get_house_bills_list(session):
    tree = grab('http://www.capitol.state.tx.us/Reports/Report.aspx?LegSess=%s&ID=housefiled' % session)
    return tree.xpath("//table//a/@href")

def get_senate_bills_list(session):
    gree = grab('http://www.capitol.state.tx.us/Reports/Report.aspx?LegSess=%s&ID=senatefiled' % session)
    return tree.xpath("//table//a/@href")
