# coding: utf-8
import sys
from optparse import OptionParser
import urllib
import urllib2
import unicodedata
from bs4 import BeautifulSoup


def get(url):
    opener = urllib2.build_opener()
    opener.addheaders = [
        ('User-agent', 'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0'),
        ('Referer', 'http://www.wishket.com/project/'),
    ]
    bin = opener.open(url).read()
    return bin


def escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')


class Wishket(object):
    SORT = {
        'PRICE_DESC': 1,
        'PRICE_ASC': 2,
        'CREATED_AT_DESC': 3,
        'CREATED_AT_ASC': 4,
    }
    def __init__(self, category=None, q=None):
        if category == 'development':
            dev_code, design_code = ('2222222222', '11111111111')
        elif category == 'design':
            dev_code, design_code = ('1111111111', '22222222222')
        else:
            dev_code, design_code = ('2222222222', '22222222222')

        if q:
            q = urllib.quote(q.encode('utf8'))
        else:
            q = 'None'

        page = 1
        self.request_url = 'http://www.wishket.com/project/pl/{}/{}/{}/{}/{}/111111111111111111/'.format(
            page, q, self.SORT['CREATED_AT_DESC'], dev_code, design_code)

        self.load()

    def load(self):
        self.items = []

        html = get(self.request_url)

        soup = BeautifulSoup(html)

        for section in soup.findAll('section', {'class':'project-unit'}):
            title = section.select('.project-title')[0].text
            url = 'http://www.wishket.com' + section.select('a.grid-block')[0]['href']
            deadline = section.select('.project-unit-heading .label')[0].text
            info = ', '.join(info.text for info in section.select('.project-unit-basic-info span'))
            desc = section.select('.project-unit-desc')[0].text
            self.items.append({
                'title': title,
                'url': url,
                'deadline': deadline,
                'info': info,
                'desc': desc,
            })


    def xml(self):
        for idx, item in enumerate(self.items):
            yield u'''<item uid="%(id)s" arg="%(url)s" valid="yes" autocomplete="yes">
    <title>%(name)s (%(deadline)s)</title>
    <subtitle>%(info)s</subtitle>
    <icon>icon.png</icon>
</item>''' % {
                'id': idx,
                'url': item['url'],
                'name': escape(item['title']),
                'deadline': escape(item['deadline']),
                'info': escape(item['info']),
                'desc': escape(item['desc']),
            }


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-d', action='store_const', const='development', dest='category')
    parser.add_option('-g', action='store_const', const='design', dest='category')
    (options, args) = parser.parse_args()

    category = options.category

    if args:
        try:
            q = args[0].decode('utf8')
            q = unicodedata.normalize('NFC', q)
        except IndexError:
            q = None
    else:
        q = None

    print('<?xml version="1.0" encoding="utf-8"?>')
    print('<items>')
    for row in Wishket(category, q).xml():
        print(row.encode('utf8'))
    print('</items>')

