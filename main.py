import urllib2
from lxml import etree

f = urllib2.urlopen('http://www.capitol.state.tx.us/Home.aspx')
parser = etree.HTMLParser()
tree = etree.parse(f, parser)

leg_sessions = tree.xpath("//*[@id='cboLegSess']/option/@value")

latest_session = leg_sessions[0]
