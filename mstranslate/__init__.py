# -*- coding: UTF-8 -*-
import urllib
import urllib2

try:
    from xml.etree.cElementTree import ElementTree, Element, tostring
except ImportError:
    from xml.etree.ElementTree import ElementTree, Element, tostring

# Normalise some mappings to microsoft ones
CODEMAP = {
    'zh-cn': 'zh-CHS',
    'zh-tw': 'zh-CHT',
    'iw': 'he',
}

INV_CODEMAP = dict(zip(CODEMAP.values(), CODEMAP.keys()))

# 1st June 2011
LANGUAGES = (
    'ar',
    'bg',
    'zh-CHS',
    'zh-CHT',
    'cs',
    'da',
    'nl',
    'en',
    'et',
    'fi',
    'fr',
    'de',
    'el',
    'ht',
    'he',
    'hu',
    'id',
    'it',
    'ja',
    'ko',
    'lv',
    'lt',
    'no',
    'pl',
    'pt',
    'ro',
    'ru',
    'sk',
    'sl',
    'es',
    'sv',
    'th',
    'tr',
    'uk',
    'vi',
)

ENDPOINT = 'http://api.microsofttranslator.com/V2/Http.svc/'

NS = 'http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2'
NSA = 'http://schemas.microsoft.com/2003/10/Serialization/Arrays'

DEBUG = True

####################

def to_ms(code):
    return CODEMAP.get(code, code)

def from_ms(code):
    return INV_CODEMAP.get(code, code)
    
def get_languages_for_translate(appid):
    params = {
        'appid': appid
    }
    root = _get('GetLanguagesForTranslate', params)
    return _xpath(root, 'string')

def detect(appid, text):
    params = {
        'appid': appid, 
        'text': text.encode('utf-8'), 
    }
    root = _get('Detect', params)
    return root.text
    
def translate(appid, text, to_code, from_code='', 
              content_type='text/html', category='general'):
    params = {
        'appid': appid, 
        'text': text.encode('utf-8'), 
        'to': str(to_code),
        'from': str(from_code),
        'contentType': content_type, 
        'category': category
    }
    root = _get('Translate', params)
    return root.text

def translate_array(appid, texts, to_code, from_code='', 
                    content_type='text/html', category='general'):
    # this api sucks, what a surprise!
    texts_xml = ''.join([ """
        <string xmlns="%(nsa)s"><![CDATA[%(text)s]]></string>
    """ % {'nsa': NSA, 'text': t.encode('utf-8') } for t in texts ])
    xml = """
    <TranslateArrayRequest>
        <AppId>%(appid)s</AppId>
        <From>%(from_code)s</From>
        <Options>
            <Category xmlns="%(ns)s">%(category)s</Category>
            <ContentType xmlns="%(ns)s">%(content_type)s</ContentType>
            <ReservedFlags xmlns="%(ns)s"></ReservedFlags>
            <Uri xmlns="%(ns)s"></Uri>
            <User xmlns="%(ns)s"></User>
        </Options>
        <Texts>
            %(texts_xml)s
        </Texts>
        <To>%(to_code)s</To>
    </TranslateArrayRequest>
    """ % {'texts_xml': texts_xml,
           'to_code': str(to_code),
           'from_code': str(from_code),
           'content_type': str(content_type),
           'category': str(category),
           'appid': appid,
           'ns': NS,
           }
    root = _post('TranslateArray', xml)
    return _xpath(root, 'TranslateArrayResponse/TranslatedText')

####################

class TranslateError(Exception):
    pass

def _parse(f):
    tree = ElementTree()
    tree.parse(f)
    root = tree.getroot()
    if root.tag == 'html':
        # weird api, returns unstructured html on error
        try:
            err = root.findall('p')[2].text
        except:
            try:
                err = root.find('h1').text
            except:
                err = 'Unknown error'
        raise TranslateError(err)
    # if DEBUG:
    #     print tostring(root)
    return root
    
def _get(method, params):
    url = '%s%s?%s' % (ENDPOINT, method, urllib.urlencode(params))
    req = urllib2.Request(url) 
    f = urllib2.urlopen(req)
    return _parse(f)

def _post(method, data):
    url = ENDPOINT + method
    req = urllib2.Request(url, data=data, headers={'Content-Type':'text/xml; charset=utf-8'})
    f = urllib2.urlopen(req)
    return _parse(f)

def _xpath(root, xpath):
    try:
        # namespaces, gotta love em
        ns = root.tag.split('}', 1)[0][1:]
        if ns:
            xpath = '/'.join([ '{%s}%s' % (ns, p) for p in xpath.split('/') if len(p) > 0 ])
    except:
        pass
    return [ t.text for t in root.findall(xpath) ]

####################

if __name__ == '__main__':
    appid = 'YOUR APPID HERE'
    print detect(appid, u"Raccolta di funzionalità per l'utilizzo tramite il servizio HTTP chiamate")
    print translate(appid, 'The Microsoft Translator services can be used in web or client applications to perform language translation operations.', to_code='ja')
    for t in translate_array(appid, [u'Servizio HTTP', u"Raccolta di funzionalità per l'utilizzo tramite il servizio HTTP chiamate"], 'en'):
        print t
