from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from bs4 import Comment
from bs4 import element
from datetime import datetime
import re

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


def get_yap_soup():
    url = 'http://www.yaplakal.com/'
    raw_html = simple_get(url)
    return BeautifulSoup(raw_html, 'html.parser')


class YapError(Exception):
    """Base class for Yap parser"""
    pass

class ParserError(YapError):
    """Exception raised if html template has been changed"""

    def __init__(self, message):
        self.message = message

def parse_content(post, soup):
    contents = soup.contents
    lines = []
    for line in contents:
        if type(line) is element.Tag and str(line) == '<br/>':
            pass
        elif type(line) is element.NavigableString:
            if str(line) != '\n':
                lines.append(line.strip())
    post['excerpt'] = '\n'.join(lines)
    post['image_src'] = ''

    picture = soup.img
    youtube_video = soup.find('iframe', attrs={'class':'youtube-player'})
    coub_video = None
    if not youtube_video and soup.iframe:
        link = soup.iframe['src']
        coub_video = link if link.find('coub.com') != -1 else None
    comments = soup.find_all(string=lambda text:isinstance(text, Comment))
    yap_video = None
    if comments:
        for c in comments:
            if 'Begin Video:' in c:
                yap_video = c.replace('Begin Video:', '')

    if youtube_video:
        post['content'] = "YouTube video " + youtube_video['src']
    elif coub_video:
        post['content'] = "Coub video " + coub_video
    elif yap_video:
        post['content'] = "Yap video " + yap_video
    elif picture:
        post['content'] = "Static picture " +  picture['src']
        post['image_src'] = picture['src']
    else:
        post['content'] = "Text or other content"


def get_front_page_posts():
    n_comments_re = re.compile('\((\d+)\)')
    posts = []
    soup = get_yap_soup()
    lenta = soup.find('table', attrs={'class':'lenta'})
    tr = lenta.find_next('tr')
    count = 0
    max_count = 50
    while count < max_count:
        count = count + 1
        post = {'id': count}
        while True:
            if not 'class' in tr.td.attrs:
                tr = tr.find_next('tr')
                continue

            cell_class = tr.td['class']
            if 'newshead' in cell_class:
                if tr.td['id'] == 'topic_' + str(count):
                    if not tr.td.div.div.a is None:
                        post['rating'] = int(tr.td.div.div.a.text)
                    else:
                        post['rating'] = 0
                    post['link'] = tr.td.div.h2.a['href']
                    post['title'] = tr.td.div.h2.a.text
                else:
                    raise ParserError('scipping title')
            elif 'news-content' in cell_class:
                if tr.td['id'] == 'news_' + str(count):
                    parse_content(post, tr.td)
                else:
                    raise ParserError('scipping content')
            elif 'newsbottom' in cell_class:
                post_info = tr.find_all('b')
                for info in post_info:
                    if 'icon-user' in info['class']:
                        post['author'] = info.text
                    elif 'icon-forum' in info['class']:
                        post['section'] = info.text
                    elif 'icon-date' in info['class']:
                        post['date'] = datetime.strptime(info.text, "%d.%m.%Y - %H:%M")
                    elif 'icon-comments' in info['class']:
                        post['comments'] = int(next(iter(n_comments_re.findall(info.span.text)), '0'))
                break
            tr = tr.find_next('tr')
        tr = tr.find_next('tr')
        posts.append(post)
    return posts

if __name__ == "__main__":
    get_front_page_posts()
