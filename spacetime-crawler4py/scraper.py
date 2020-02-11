import re
import urllib.robotparser
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
from bs4.element import Comment
from nltk.stem.snowball import SnowballStemmer
from collections import defaultdict
from simhash import Simhash, SimhashIndex
STOPWORDS=set("""
a
about
above
after
again
against
all
am
an
and
any
are
aren't
as
at
be
because
been
before
being
below
between
both
but
by
can't
cannot
could
couldn't
did
didn't
do
does
doesn't
doing
don't
down
during
each
few
for
from
further
had
hadn't
has
hasn't
have
haven't
having
he
he'd
he'll
he's
her
here
here's
hers
herself
him
himself
his
how
how's
i
i'd
i'll
i'm
i've
if
in
into
is
isn't
it
it's
its
itself
let's
me
more
most
mustn't
my
myself
no
nor
not
of
off
on
once
only
or
other
ought
our
ours
""".split("\n"))

urls=set()
sims=set()
objs=[]

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp) -> "list()":
    defrag=urldefrag(url)[0]
    print(defrag)
    if resp.status == 200:
        print("Scanning")
        if defrag not in urls:
            content = resp.raw_response.text
            data=getVisibleText(content)
            simmed=Simhash(data)
            if simmed.value not in sims:
                index=SimhashIndex(objs,k=3)
                if len(index.get_near_dups(simmed))==0:
                    urls.add(defrag)
                    sims.add(simmed.value)
                    objs.append((url,simmed))
                    print(len(urls),len(sims),len(objs))
                    try:
                        file=open("data_dump.txt","a",errors="ignore")
                        to_write=url+ " \n "+ data+ "\n"+ str(simmed.value) +"\n\n"
                        file.write(to_write)
                    except Exception as e:
                        raise e
                    finally:
                        file.close()
            #urls[defrag].add(getVisibleText(content))
            #print(urls[defrag])
        return getAllUrls(url,content)
    else:
        print("Cant scan")
        return []

def filterVisibleText(text):
    if text.parent.name in ['script','[document]','style','meta','head','area','base','basefont','br','col','frame','hr','img','input','isindex','param']:
        return False
    if isinstance(text, Comment):
        return False
    return True

def getVisibleText(content):
    soup = BeautifulSoup(content,features="html.parser")
    allTexts = soup.findAll(text=True)
    visibleText = filter(filterVisibleText,allTexts)
    text=u" ".join(word.strip() for word in visibleText)
    result=""
    for x in text.split():
        result= result+" "+(stem_word(x) if x not in STOPWORDS else "")
    #print(result)
    return result

def stem_word(word:str):
    """Snowball stemmer which we can implement if needed"""
    ks=SnowballStemmer("english")
    return ks.stem(word)

def getAllUrls(url,content):
    FilteredUrls = []
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(url+"/robots.txt")
    rp.read()
    soup = BeautifulSoup(content, features="html.parser")
    for a in soup.find_all('a',href=True):
        if rp.can_fetch("*", a['href']):
            if a['href'] != "#" or a['href'][0] != "/":
                FilteredUrls.append(urldefrag(a['href'])[0])
            elif a['href'][0] == '/' and rp.can_fetch("*",url+a['href']):
                FilteredUrls.append(urldefrag(url+a['href'])[0])
    return FilteredUrls if FilteredUrls != None else []

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["https", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise