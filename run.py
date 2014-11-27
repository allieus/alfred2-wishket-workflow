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
    def __init__(self, category=None, q=None):
        self.category = category
        self.q = q
        self.load()

    def load(self):
        self.items = []
        for page in range(1,2):
            url = "http://www.wishket.com/project/?page={}".format(page)
            if self.category:
                url += '&category=' + self.category
            if self.q:
                url += '&q=' + urllib.quote(self.q.encode('utf8'))
            else:
                url += '&q='
            html = get(url)

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

