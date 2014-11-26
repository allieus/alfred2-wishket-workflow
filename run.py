# coding: utf-8
import sys
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


def safe_print(s):
    if isinstance(s, unicode):
        print(s.encode('utf-8'))
    else:
        print(s)


class Wishket(object):
    def __init__(self, q=None):
        self.q = q
        self.items = []
        self.load()

    def load(self):
        for page in range(1,2):
            url = "http://www.wishket.com/project/?page={}".format(page)
            if self.q:
                url += '&q=' + urllib.quote(self.q.encode('utf8'))
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
    try:
        q = sys.argv[1].decode('utf8')
        q = unicodedata.normalize('NFC', q)
    except IndexError:
        q = None

    wishket = Wishket(q)

    safe_print(u'<?xml version="1.0" encoding="utf-8"?>')
    safe_print(u'<items>')
    for row in wishket.xml():
        safe_print(row)
    safe_print(u'</items>')

