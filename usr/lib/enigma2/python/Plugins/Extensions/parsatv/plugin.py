#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import codecs
from datetime import datetime
from functools import partial
from json import loads as json_loads
from os import remove, stat, system as os_system
from os.path import exists, isfile, join
from re import DOTALL, compile, sub
from sys import version_info

import six
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import (
    MultiContentEntryPixmapAlphaTest,
    MultiContentEntryText,
)
from Components.ServiceEventTracker import InfoBarBase, ServiceEventTracker
from Components.config import config
from Plugins.Plugin import PluginDescriptor
from Screens.InfoBarGenerics import (
    InfoBarAudioSelection,
    InfoBarMenu,
    InfoBarNotifications,
    InfoBarSeek,
    InfoBarSubtitleSupport,
)
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import SCOPE_PLUGINS, resolveFilename
from enigma import (
    RT_HALIGN_LEFT,
    RT_VALIGN_CENTER,
    eListboxPythonMultiContent,
    eServiceReference,
    eTimer,
    gFont,
    getDesktop,
    iPlayableService,
    loadPNG,
)

from . import _, __version__, paypal
from . import Utils, html_conv
from .Console import Console as xConsole

'''
****************************************
*        coded by Lululla & PCD        *
*             skin by MMark            *
*             12/09/2023               *
*       Skin by MMark                  *
****************************************
'''

downloadparsa = None
_session = None

PY3 = version_info.major >= 3
if PY3:
    from urllib.request import Request, urlopen
    unicode = str
    unichr = chr
    long = int
else:
    from urllib2 import Request, urlopen

try:
    from Components.UsageConfig import defaultMoviePath
    downloadparsa = defaultMoviePath()
except Exception:
    if exists("/usr/bin/apt-get"):
        downloadparsa = '/media/hdd/movie/'

if not PY3:
    try:
        import ssl
        sslContext = ssl._create_unverified_context()
    except Exception:
        sslContext = None

try:
    from twisted.internet import ssl
    from twisted.internet._sslverify import ClientTLSOptions
    sslverify = True
except Exception:
    sslverify = False


if sslverify:
    class SNIFactory(ssl.ClientContextFactory):
        def __init__(self, hostname=None):
            self.hostname = hostname

        def getContext(self):
            ctx = self._contextFactory(self.method)
            if self.hostname:
                ClientTLSOptions(self.hostname, ctx)
            return ctx


def ssl_urlopen(url):
    if sslContext:
        return urlopen(url, context=sslContext)
    return urlopen(url)


title_plug = 'Parsa TV '
desc_plugin = '..:: Parsa TV by Lululla {} ::.. '.format(__version__)
plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('parsatv'))
pluglogo = join(plugin_path, 'res/pics/logo.png')
png = join(plugin_path, 'res/pics/tv.png')
installer_url = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL0JlbGZhZ29yMjAwNS90dlBhcnNhL21haW4vaW5zdGFsbGVyLnNo'
developer_url = 'aHR0cHM6Ly9hcGkuZ2l0aHViLmNvbS9yZXBvcy9CZWxmYWdvcjIwMDUvdHZQYXJzYQ=='
screenwidth = getDesktop(0).size()
if screenwidth.width() == 2560:
    path_skin = plugin_path + '/res/skins/uhd/'
elif screenwidth.width() == 1920:
    path_skin = plugin_path + '/res/skins/fhd/'
else:
    path_skin = plugin_path + '/res/skins/hd/'

if Utils.DreamOS():
    path_skin = path_skin + 'dreamOs/'
print('parsa path_skin: ', path_skin)
referer = 'https://www.parsatv.com/'
aspect_manager = Utils.AspectManager()

Panel_Dlist = [
    ('PARSA ALL TV'),
    ('PARSA TV CATEGORY'),
    ('PARSA SPORT')
]

# filter list assign png
EXTRAD = "radio", "radyo", "mix", "fm", "kbit", "rap", "metal", "alternative"
EXTXXX = "adult", "xxx"
EXTCAM = "webcam", "webcams"
EXTMUS = "music", "mtv", "deluxe", "djing", "fashion", "kiss", "mpeg", "sluhay", "stingray", "techno", "viva", "country", "vevo"
EXTSPOR = "sport", "boxing", "racing", "fight", "golf", "knock", "harley", "futbool", "motor", "nba", "nfl", "bull", "poker", "billiar", "fite"
EXTRLX = "relax", "nature", "escape"
EXTMOV = "movie", "film"
EXTWEA = "weather"
EXTFAM = "family"
EXTREL = "religious"
EXTSHP = "shop"
EXTTRV = "travel"


def returnpng(name):
    if 'radio' in name.lower():
        png = join(plugin_path, 'res/pics/radio.png')
    elif 'webcam' in name.lower():
        png = join(plugin_path, 'res/pics/webcam.png')
    elif 'music' in name.lower():
        png = join(plugin_path, 'res/pics/music.png')
    elif 'sport' in name.lower():
        png = join(plugin_path, 'res/pics/sport.png')
    elif 'travel' in name.lower():
        png = join(plugin_path, 'res/pics/travel.png')
    elif 'relax' in name.lower():
        png = join(plugin_path, 'res/pics/relax.png')
    elif 'xxx' in name.lower():
        png = join(plugin_path, 'res/pics/xxx.png')
    elif 'movie' in name.lower():
        png = join(plugin_path, 'res/pics/movie.png')
    elif 'family' in name.lower():
        png = join(plugin_path, 'res/pics/family.png')
    elif 'religious' in name.lower():
        png = join(plugin_path, 'res/pics/religious.png')
    elif 'weather' in name.lower():
        png = join(plugin_path, 'res/pics/weather.png')
    else:
        png = join(plugin_path, 'res/pics/tv.png')
    return png


class OneSetList(MenuList):
    def __init__(self, items):
        MenuList.__init__(self, items, True, eListboxPythonMultiContent)
        if screenwidth.width() == 2560:
            self.l.setItemHeight(60)
            self.l.setFont(0, gFont('Regular', 42))
        elif screenwidth.width() == 1920:
            self.l.setItemHeight(50)
            self.l.setFont(0, gFont('Regular', 32))
        else:
            self.l.setItemHeight(50)
            self.l.setFont(0, gFont('Regular', 24))


def OneSetListEntry(name, idx):
    res = [name]
    png = returnpng(name)
    if screenwidth.width() == 2560:
        res.append(MultiContentEntryPixmapAlphaTest(
            pos=(5, 5), size=(50, 50), png=loadPNG(png)))
        res.append(MultiContentEntryText(
            pos=(90, 0), size=(1200, 50), font=0, text=name,
            color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    elif screenwidth.width() == 1920:
        res.append(MultiContentEntryPixmapAlphaTest(
            pos=(5, 7), size=(40, 40), png=loadPNG(png)))
        res.append(MultiContentEntryText(
            pos=(70, 0), size=(1000, 50), font=0, text=name,
            color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(
            pos=(3, 10), size=(40, 40), png=loadPNG(png)))
        res.append(MultiContentEntryText(
            pos=(50, 0), size=(500, 50), font=0, text=name,
            color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


def showlistpars(data, lst):
    """Populate a MenuList with one row per entry in `data`."""
    plist = [OneSetListEntry(name, idx) for idx, name in enumerate(data)]
    lst.setList(plist)


def returnIMDB(text_clear):
    text = html_conv.html_unescape(text_clear)

    if Utils.is_TMDB and Utils.TMDB:
        try:
            _session.open(Utils.TMDB.tmdbScreen, text, 0)
        except Exception as e:
            print("[XCF] TMDB error:", e)
        return True

    if Utils.is_tmdb and Utils.tmdb:
        try:
            _session.open(Utils.tmdb.tmdbScreen, text, 0)
        except Exception as e:
            print("[XCF] tmdb error:", e)
        return True

    if Utils.is_imdb and Utils.imdb:
        try:
            Utils.imdb(_session, text)
        except Exception as e:
            print("[XCF] IMDb error:", e)
        return True

    _session.open(MessageBox, text, MessageBox.TYPE_INFO)
    return True


# ---------------------------------------------------------------------------
# Main screen
# ---------------------------------------------------------------------------

class MainParsa(Screen):
    def __init__(self, session):
        self.session = session
        global _session
        _session = session
        skin = join(path_skin, 'settings.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = 'MainParsa'
        Screen.__init__(self, session)
        self.setTitle(title_plug)
        self['text'] = OneSetList([])
        self['title'] = Label(title_plug)
        self['info'] = Label(_('Loading data... Please wait'))
        self["paypal"] = Label()
        self['key_yellow'] = Button(_('Update'))
        self['key_yellow'].hide()
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Exit'))
        self["key_blue"] = Button()
        self['key_blue'].hide()
        self["key_green"].hide()
        self.Update = False
        self.new_version = '0.0'
        self.new_changelog = ''
        self["actions"] = ActionMap(
            ["OkCancelActions", "HotkeyActions", "InfobarEPGActions",
             "ChannelSelectBaseActions", "DirectionActions"],
            {
                "yellow": self.update_me,
                "yellow_long": self.update_dev,
                "info_long": self.update_dev,
                "infolong": self.update_dev,
                "showEventInfoPlugin": self.update_dev,
                "ok": self.okRun,
                "green": self.okRun,
                "cancel": self.closerm,
                "red": self.closerm,
            },
            -1,
        )

        self.timer = eTimer()
        if exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.check_vers)
        else:
            self.timer.callback.append(self.check_vers)
        self.timer.start(500, 1)
        self.onLayoutFinish.append(self.updateMenuList)
        self.onLayoutFinish.append(self.layoutFinished)

    def check_vers(self):
        remote_version = '0.0'
        remote_changelog = ''
        try:
            req = Request(Utils.b64decoder(installer_url),
                          headers={'User-Agent': 'Mozilla/5.0'})
            page = Utils.urlopen(req, timeout=10).read()
            if not page:
                return
            data = page.decode("utf-8") if PY3 else page
            if data:
                for line in data.split("\n"):
                    if line.startswith("version"):
                        remote_version = line.split("'")[1]
                    if line.startswith("changelog"):
                        remote_changelog = line.split("'")[1]
                        break
        except Exception as e:
            print("[ParsaTV] check_vers error:", e)
            return

        self.new_version = remote_version
        self.new_changelog = remote_changelog

        def _ver(t):
            try:
                return tuple(int(x) for x in t.split('.'))
            except (ValueError, AttributeError):
                return (0,)

        try:
            if _ver(__version__) < _ver(remote_version):
                self.Update = True
                self['key_yellow'].show()
                self.session.open(
                    MessageBox,
                    _("New version %s is available\n\n"
                      "Changelog: %s\n\n"
                      "Press info_long or yellow_long to force update.")
                    % (self.new_version, self.new_changelog),
                    MessageBox.TYPE_INFO, timeout=5)
        except Exception as e:
            print("[ParsaTV] version compare error:", e)

    def update_me(self):
        if self.Update:
            self.session.openWithCallback(
                self.install_update, MessageBox,
                _("New version %s is available.\n\n"
                  "Changelog: %s\n\n"
                  "Do you want to install it now?")
                % (self.new_version, self.new_changelog),
                MessageBox.TYPE_YESNO)
        else:
            self.session.open(
                MessageBox,
                _("Congrats! You already have the latest version..."),
                MessageBox.TYPE_INFO, timeout=4)

    def update_dev(self):
        try:
            req = Request(Utils.b64decoder(developer_url),
                          headers={'User-Agent': 'Mozilla/5.0'})
            page = Utils.urlopen(req, timeout=10).read()
            if not page:
                return
            data = json_loads(page)
            remote_date = data['pushed_at']
            strp = datetime.strptime(remote_date, '%Y-%m-%dT%H:%M:%SZ')
            remote_date = strp.strftime('%Y-%m-%d')
            self.session.openWithCallback(
                self.install_update, MessageBox,
                _("Do you want to install update ( %s ) now?") % remote_date,
                MessageBox.TYPE_YESNO)
        except Exception as e:
            print('update_dev error:', e)

    def install_update(self, answer=False):
        if answer:
            cmd1 = ('wget -q "--no-check-certificate" '
                    + Utils.b64decoder(installer_url) + ' -O - | /bin/sh')
            self.session.open(
                xConsole, 'Upgrading...',
                cmdlist=[cmd1],
                finishedCallback=self.myCallback,
                closeOnSuccess=False)
        else:
            self.session.open(
                MessageBox, _("Update Aborted!"),
                MessageBox.TYPE_INFO, timeout=3)

    def myCallback(self, result=None):
        print('install_update result:', result)

    def layoutFinished(self):
        self["paypal"].setText(paypal())
        self.setTitle(self.setup_title)

    def closerm(self):
        Utils.deletetmp()
        self.close()

    def updateMenuList(self):
        self.menu_list = list(Panel_Dlist)
        items = [OneSetListEntry(x, idx) for idx, x in enumerate(Panel_Dlist)]
        self['text'].setList(items)
        self["key_green"].show()
        self['info'].setText(_('Please select ...'))

    def okRun(self):
        self.keyNumberGlobalCB(self['text'].getSelectedIndex())

    def keyNumberGlobalCB(self, idx):
        sel = self.menu_list[idx]
        if sel == _('PARSA SPORT'):
            self.session.open(parsasport)
        elif sel == _('PARSA ALL TV'):
            self.session.open(parsatv)
        elif sel == _('PARSA TV CATEGORY'):
            self.session.open(parsatv2)


# ---------------------------------------------------------------------------
# Category list
# ---------------------------------------------------------------------------

class parsatv2(Screen):
    """Shows the list of categories."""

    def __init__(self, session):
        self.session = session
        global _session
        _session = session
        skin = join(path_skin, 'settings.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = 'ParsaTV'
        Screen.__init__(self, session)
        self.setTitle(title_plug)
        self.name = 'Parsa Category'
        self.url = 'https://www.parsatv.com/m/'
        self['title'] = Label(title_plug)
        self['text'] = OneSetList([])
        self['info'] = Label(_('Loading data... Please wait'))
        self["paypal"] = Label()
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self["key_green"].hide()
        self['key_blue'].hide()
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self.timer.start(1500, True)
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "ButtonSetupActions",
             "DirectionActions"],
            {
                "ok": self.okRun,
                "green": self.okRun,
                "red": self.close,
                "cancel": self.close,
            },
            -2,
        )
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self["paypal"].setText(paypal())
        self.setTitle(self.setup_title)

    def _gotPageLoad(self):
        base_url = self.url
        self.names = []
        self.urls = []
        try:
            content = Utils.ReadUrl2(base_url, referer)
            if not content:
                self['info'].setText(_('Network error - please retry'))
                return
            if not six.PY2:
                content = six.ensure_str(content)

            match = compile(
                r'<tr>.*?<td id=".*?><li>(.+?)<a>.*?</td>.*?</tr>',
                DOTALL).findall(content)

            items = sorted(name + "###" + base_url + '\n' for name in match)
            for item in items:
                self.names.append(item.split("###")[0])
                self.urls.append(item.split("###")[1])

            self['info'].setText(_('Please select ...'))
            self["key_green"].show()
            showlistpars(self.names, self['text'])
        except Exception as e:
            print("[parsatv2] _gotPageLoad error:", e)
            self['info'].setText(_('Error loading page'))

    def okRun(self):
        if not self.names:
            return
        idx = self["text"].getSelectionIndex()
        if idx < 0 or idx >= len(self.names):
            return
        self.session.open(parsatv3, self.names[idx], self.urls[idx])


# ---------------------------------------------------------------------------
# Single category
# ---------------------------------------------------------------------------

class parsatv3(Screen):
    """Shows the channels of a single category."""

    def __init__(self, session, name, url):
        self.session = session
        global _session
        _session = session
        skin = join(path_skin, 'settings.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = 'Parsa Category'
        Screen.__init__(self, session)
        self.setTitle(title_plug)
        self.name = name
        self.url = url
        self['title'] = Label(title_plug)
        self['text'] = OneSetList([])
        self['info'] = Label(_('Loading data... Please wait'))
        self["paypal"] = Label()
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Play'))
        self['key_yellow'] = Button(_('Convert'))
        self["key_blue"] = Button()
        self["key_green"].hide()
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self.timer.start(1500, True)
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "ButtonSetupActions",
             "DirectionActions"],
            {
                "ok": self.okRun,
                "green": self.okRun,
                "red": self.close,
                "yellow": self.convert,
                "cancel": self.close,
            },
            -2,
        )
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self["paypal"].setText(paypal())
        self.setTitle(self.setup_title)

    def convert(self, answer=None):
        if answer is None:
            self.session.openWithCallback(
                self.convert, MessageBox,
                _("Do you want to convert %s to a favorite .tv bouquet?\n\n"
                  "Warning: this may take a while depending on the\n"
                  "number of streams contained!") % self.name)
        elif answer:
            namex = self.name.lower().replace(' ', '-').strip()
            if Utils.DreamOS():
                from Tools.BoundFunction import boundFunction
                self.timer_conn = self.timer.timeout.connect(
                    boundFunction(make_m3u2, namex))
            else:
                self.timer.callback.append(partial(make_m3u2, namex))
            self.timer.start(500, True)

    def _gotPageLoad(self):
        self.names = []
        self.urls = []
        items = []
        url = self.url
        name = self.name
        namex = name.lower().replace(" ", "-").strip()

        xxxname = (downloadparsa + namex + "_conv.m3u"
                   if exists(downloadparsa) else "/tmp/" + namex + "_conv.m3u")

        try:
            content = Utils.ReadUrl2(url, referer)
            if not content:
                self['info'].setText(_('Network error - please retry'))
                return
            if not six.PY2:
                content = six.ensure_str(content)

            anchor = name + "<a></a>"
            n1 = content.find(anchor)
            if n1 == -1:
                self['info'].setText(_('Category not found: %s') % name)
                return
            n2 = content.find("<td id=", n1 + len(anchor))
            content2 = content[n1:] if n2 == -1 else content[n1:n2]

            match = compile(
                r'<li><a href="(.+?)#.*?"><button.*?myButton">(.+?)</button',
                DOTALL).findall(content2)

            with open(xxxname, "w") as fh:
                fh.write("#EXTM3U\n")
                for u, n in match:
                    if u.startswith("http"):
                        u = u.replace(" ", "%20")
                        n_clean = n.replace("%20", " ")
                        items.append(n_clean + "###" + u + "\n")
                        fh.write("#EXTINF:-1," + n_clean + "\n")
                        fh.write(u + "\n")

            items.sort()
            for item in items:
                self.names.append(item.split("###")[0])
                self.urls.append(item.split("###")[1])

            self["info"].setText(_("Please select ..."))
            self["key_green"].show()
            self["key_yellow"].show()
            showlistpars(self.names, self["text"])
            print("-------------parsatv3-------------")
        except Exception as e:
            print("[parsatv3] _gotPageLoad error:", e)
            self['info'].setText(_('Error loading page'))

    def okRun(self):
        if not self.names:
            return
        idx = self["text"].getSelectionIndex()
        if idx < 0 or idx >= len(self.names):
            return
        name, url = self.names[idx], self.urls[idx]
        try:
            content = Utils.ReadUrl2(url, referer)
            if not content:
                raise ValueError("Empty response")
            if not six.PY2:
                content = six.ensure_str(content)
            n1 = content.find('class="myButton" id=', 0)
            n2 = content.find("</button></a>", n1)
            if n1 == -1 or n2 == -1:
                raise ValueError("Stream URL not found")
            match = compile(r'<a href="(.+?)"><b', DOTALL).findall(content[n1:n2])
            if not match:
                raise ValueError("No video link found")
            self.session.open(Playgo, name, match[-1])
        except Exception as e:
            print("[parsatv3] okRun error:", e)
            self.session.open(
                MessageBox, _("Unable to extract stream:\n%s") % e,
                MessageBox.TYPE_ERROR, timeout=5)


# ---------------------------------------------------------------------------
# Sport
# ---------------------------------------------------------------------------

class parsasport(Screen):
    """Scrapes channels from the 'Sport' category."""

    def __init__(self, session):
        self.session = session
        skin = join(path_skin, 'settings.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = 'Parsa Sport'
        Screen.__init__(self, session)
        self.setTitle(title_plug)
        self.name = 'ParsaSport'
        self.url = 'http://www.parsatv.com/m/'
        self['text'] = OneSetList([])
        self['info'] = Label(_('Loading data... Please wait'))
        self["paypal"] = Label()
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Play'))
        self['key_yellow'] = Button(_('Convert'))
        self["key_blue"] = Button()
        self["key_green"].hide()
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self.timer.start(1500, True)
        self['title'] = Label(title_plug)
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "ButtonSetupActions",
             "DirectionActions"],
            {
                "ok": self.okRun,
                "green": self.okRun,
                "red": self.close,
                "yellow": self.convert,
                "cancel": self.close,
            },
            -2,
        )
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self["paypal"].setText(paypal())
        self.setTitle(self.setup_title)

    def convert(self, answer=None):
        if answer is None:
            self.session.openWithCallback(
                self.convert, MessageBox,
                _("Do you want to convert to a favorite .tv bouquet?\n\n"
                  "Warning: this may take a while depending on the\n"
                  "number of streams contained!"))
        elif answer:
            namex = self.name.lower().replace(' ', '-').strip()
            if Utils.DreamOS():
                from Tools.BoundFunction import boundFunction
                self.timer_conn = self.timer.timeout.connect(
                    boundFunction(make_m3u2, namex))
            else:
                self.timer.callback.append(partial(make_m3u2, namex))
            self.timer.start(500, True)

    def _gotPageLoad(self):
        self.names = []
        self.urls = []
        items = []
        url = self.url
        namex = self.name.lower().replace(' ', '-').strip()

        xxxname = (downloadparsa + namex + '_conv.m3u'
                   if exists(downloadparsa) else '/tmp/' + namex + '_conv.m3u')

        try:
            content = Utils.ReadUrl2(url, referer)
            if not content:
                self['info'].setText(_('Network error - please retry'))
                return
            if not six.PY2:
                content = six.ensure_str(content)

            start_marker = '<td id="sport">'
            n1 = content.find(start_marker)
            if n1 == -1:
                self['info'].setText(_('Sport category not found'))
                return
            n2 = content.find('<td id="', n1 + len(start_marker))
            content2 = content[n1:] if n2 == -1 else content[n1:n2]

            match = compile(
                r'<li><a href="(.+?)#.*?"><button.*?myButton">(.+?)</button',
                DOTALL).findall(content2)

            with open(xxxname, 'w') as fh:
                fh.write("#EXTM3U\n")
                for u, n in match:
                    if u.startswith('http'):
                        u = u.replace(' ', '%20')
                        n_clean = n.replace('%20', ' ')
                        items.append(n_clean + "###" + u + '\n')
                        fh.write('#EXTINF:-1,' + n_clean + '\n')
                        fh.write(u + '\n')

            items.sort()
            for item in items:
                self.names.append(item.split("###")[0])
                self.urls.append(item.split("###")[1])

            self['info'].setText(_('Please select ...'))
            self["key_green"].show()
            self['key_yellow'].show()
            showlistpars(self.names, self['text'])
            print('-------------sport-------------')
        except Exception as e:
            print('[parsasport] _gotPageLoad error:', e)
            self['info'].setText(_('Error loading page'))

    def okRun(self):
        if not self.names:
            return
        idx = self["text"].getSelectionIndex()
        if idx < 0 or idx >= len(self.names):
            return
        name, url = self.names[idx], self.urls[idx]
        try:
            content = Utils.ReadUrl2(url, referer)
            if not content:
                raise ValueError("Empty response")
            if not six.PY2:
                content = six.ensure_str(content)
            n1 = content.find('class="myButton" id=', 0)
            n2 = content.find("</button></a>", n1)
            if n1 == -1 or n2 == -1:
                raise ValueError("Stream URL not found")
            match = compile(r'<a href="(.+?)"><b', DOTALL).findall(content[n1:n2])
            if not match:
                raise ValueError("No video link found")
            self.session.open(Playgo, name, match[-1])
        except Exception as e:
            print('[parsasport] okRun error:', e)
            self.session.open(
                MessageBox, _("Unable to extract stream:\n%s") % e,
                MessageBox.TYPE_ERROR, timeout=5)


# ---------------------------------------------------------------------------
# All TV (Persian section, all categories)
# ---------------------------------------------------------------------------

class parsatv(Screen):
    """Loads every channel from the Persian section of the mobile page."""

    def __init__(self, session):
        self.session = session
        skin = join(path_skin, 'settings.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = 'Parsa TV'
        Screen.__init__(self, session)
        self.setTitle(title_plug)
        self.name = 'ParsaTv'
        self.url = 'https://www.parsatv.com/m/'
        self['text'] = OneSetList([])
        self['info'] = Label(_('Loading data... Please wait'))
        self["paypal"] = Label()
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Play'))
        self['key_yellow'] = Button(_('Convert'))
        self["key_blue"] = Button()
        self["key_green"].hide()
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self.timer.start(1500, True)
        self['title'] = Label(title_plug)
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "ButtonSetupActions",
             "DirectionActions"],
            {
                "ok": self.okRun,
                "green": self.okRun,
                "red": self.close,
                "yellow": self.convert,
                "cancel": self.close,
            },
            -2,
        )
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self["paypal"].setText(paypal())
        self.setTitle(self.setup_title)

    def convert(self, answer=None):
        if answer is None:
            self.session.openWithCallback(
                self.convert, MessageBox,
                _("Do you want to convert to a favorite .tv bouquet?\n\n"
                  "Warning: this may take a while depending on the\n"
                  "number of streams contained!"))
        elif answer:
            namex = self.name.lower().replace(' ', '-').strip()
            if Utils.DreamOS():
                from Tools.BoundFunction import boundFunction
                self.timer_conn = self.timer.timeout.connect(
                    boundFunction(make_m3u2, namex))
            else:
                self.timer.callback.append(partial(make_m3u2, namex))
            self.timer.start(500, True)

    def _gotPageLoad(self):
        self.names = []
        self.urls = []
        items = []
        url = self.url
        namex = self.name.lower().replace(' ', '-').strip()

        xxxname = (downloadparsa + namex + '_conv.m3u'
                   if exists(downloadparsa) else '/tmp/' + namex + '_conv.m3u')

        try:
            content = Utils.ReadUrl2(url, referer)
            if not content:
                self['info'].setText(_('Network error - please retry'))
                return
            if not six.PY2:
                content = six.ensure_str(content)

            n1 = content.find('<td id="persian">')
            if n1 == -1:
                self['info'].setText(_('Persian category not found'))
                return
            content = content[n1:]

            match = compile(
                r'<li><a href="(.+?)#.*?"><button.*?myButton">(.+?)</button',
                DOTALL).findall(content)

            with open(xxxname, 'w') as fh:
                fh.write("#EXTM3U\n")
                for u_item, n_item in match:
                    if u_item.startswith('http'):
                        u_fixed = u_item.replace(' ', '%20')
                        n_fixed = n_item.replace('%20', ' ')
                        items.append(n_fixed + "###" + u_fixed + '\n')
                        fh.write('#EXTINF:-1,' + n_fixed + '\n')
                        fh.write(u_fixed + '\n')

            items.sort()
            for item in items:
                self.names.append(item.split("###")[0])
                self.urls.append(item.split("###")[1])

            self['info'].setText(_('Please select ...'))
            self["key_green"].show()
            self['key_yellow'].show()
            showlistpars(self.names, self['text'])
            print('-------------parsatv-------------')
        except Exception as e:
            print('[parsatv] _gotPageLoad error:', e)
            self['info'].setText(_('Error loading page'))

    def okRun(self):
        if not self.names:
            return
        idx = self["text"].getSelectionIndex()
        if idx < 0 or idx >= len(self.names):
            return
        name, url = self.names[idx], self.urls[idx]
        try:
            content = Utils.ReadUrl2(url, referer)
            if not content:
                raise ValueError("Empty response")
            if not six.PY2:
                content = six.ensure_str(content)
            n1 = content.find('class="myButton" id=', 0)
            n2 = content.find("</button></a>", n1)
            if n1 == -1 or n2 == -1:
                raise ValueError("Stream URL not found")
            match = compile(r'<a href="(.+?)"><b', DOTALL).findall(content[n1:n2])
            if not match:
                raise ValueError("No video link found")
            self.session.open(Playgo, name, match[-1])
        except Exception as e:
            print('[parsatv] okRun error:', e)
            self.session.open(
                MessageBox, _("Unable to extract stream:\n%s") % e,
                MessageBox.TYPE_ERROR, timeout=5)


# ---------------------------------------------------------------------------
# Infobar show/hide
# ---------------------------------------------------------------------------

class TvInfoBarShowHide:
    """InfoBar show/hide control."""

    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3
    skipToggleShow = False

    def __init__(self):
        self["ShowHideActions"] = ActionMap(
            ["InfobarShowHideActions"],
            {"toggleShow": self.OkPressed, "hide": self.hide}, 0)
        self.__event_tracker = ServiceEventTracker(
            screen=self,
            eventmap={iPlayableService.evStart: self.serviceStarted})
        self.__state = self.STATE_SHOWN
        self.__locked = 0
        self.hideTimer = eTimer()
        try:
            self.hideTimer_conn = self.hideTimer.timeout.connect(self.doTimerHide)
        except Exception:
            self.hideTimer.callback.append(self.doTimerHide)
        self.hideTimer.start(5000, True)
        self.onShow.append(self.__onShow)
        self.onHide.append(self.__onHide)

    def OkPressed(self):
        self.toggleShow()

    def toggleShow(self):
        if self.skipToggleShow:
            self.skipToggleShow = False
            return
        if self.__state == self.STATE_HIDDEN:
            self.show()
            self.hideTimer.stop()
        else:
            self.hide()
            self.startHideTimer()

    def serviceStarted(self):
        if self.execing and config.usage.show_infobar_on_zap.value:
            self.doShow()

    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()

    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            self.hideTimer.stop()
            idx = config.usage.infobar_timeout.index
            if idx:
                self.hideTimer.start(idx * 1500, True)

    def __onHide(self):
        self.__state = self.STATE_HIDDEN

    def doShow(self):
        self.hideTimer.stop()
        self.show()
        self.startHideTimer()

    def doTimerHide(self):
        self.hideTimer.stop()
        if self.__state == self.STATE_SHOWN:
            self.hide()

    def lockShow(self):
        try:
            self.__locked += 1
        except Exception:
            self.__locked = 0
        if self.execing:
            self.show()
            self.hideTimer.stop()
            self.skipToggleShow = False

    def unlockShow(self):
        try:
            self.__locked -= 1
        except Exception:
            self.__locked = 0
        self.__locked = max(self.__locked, 0)
        if self.execing:
            self.startHideTimer()

    def debug(self, obj, text=""):
        print("{} {}\n".format(text, obj))


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

class Playgo(
    InfoBarBase,
    InfoBarMenu,
    InfoBarSeek,
    InfoBarAudioSelection,
    InfoBarSubtitleSupport,
    InfoBarNotifications,
    TvInfoBarShowHide,
    Screen,
):
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    ENABLE_RESUME_SUPPORT = True
    ALLOW_SUSPEND = True
    screen_timeout = 5000

    def __init__(self, session, name, url):
        global SREF, streaml
        Screen.__init__(self, session)
        self.session = session
        self.skinName = 'MoviePlayer'
        streaml = False
        self.allowPiP = False
        self.service = None
        self.url = url
        self.pcip = 'None'
        self.name = html_conv.html_unescape(name)
        self.state = self.STATE_PLAYING
        for x in (InfoBarBase, InfoBarMenu, InfoBarSeek, InfoBarAudioSelection,
                  InfoBarSubtitleSupport, InfoBarNotifications, TvInfoBarShowHide):
            x.__init__(self)

        SREF = self.session.nav.getCurrentlyPlayingServiceReference()
        self["actions"] = ActionMap(
            ["MoviePlayerActions", "MovieSelectionActions", "MediaPlayerActions",
             "EPGSelectActions", "MediaPlayerSeekActions", "ColorActions",
             "OkCancelActions", "InfobarShowHideActions", "InfobarActions",
             "InfobarSeekActions"],
            {
                "leavePlayer": self.cancel,
                "epg": self.showIMDB,
                "info": self.showIMDB,
                "tv": self.cicleStreamType,
                "stop": self.leavePlayer,
                "cancel": self.cancel,
                "exit": self.leavePlayer,
                "back": self.cancel,
            },
            -1,
        )

        if '8088' in str(self.url):
            self.onFirstExecBegin.append(self.slinkPlay)
        else:
            self.onFirstExecBegin.append(self.cicleStreamType)
        self.onClose.append(self.cancel)

    def showIMDB(self):
        if returnIMDB(self.name):
            print('show imdb/tmdb')

    def slinkPlay(self, url):
        ref = "{}:{}".format(
            url.replace(":", "%3a"), self.name.replace(":", "%3a"))
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(str(self.name))
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def openTest(self, servicetype, url):
        ref = "{}:0:1:0:0:0:0:0:0:0:{}:{}".format(
            servicetype,
            url.replace(":", "%3a"),
            self.name.replace(":", "%3a"))
        if streaml is True:
            url = 'http://127.0.0.1:8088/' + str(url)
            ref = "{}:0:1:0:0:0:0:0:0:0:{}:{}".format(
                servicetype,
                url.replace(":", "%3a"),
                self.name.replace(":", "%3a"))
            print('streaml reference:   ', ref)
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(str(self.name))
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def cicleStreamType(self):
        from itertools import cycle, islice
        self.servicetype = '4097'
        url = str(self.url)
        streamtypelist = ["4097"]
        if exists("/usr/bin/apt-get"):
            streamtypelist.append("8193")
        currentindex = next(
            (i for i, item in enumerate(streamtypelist)
             if str(item) == str(self.servicetype)), 0)
        nextStreamType = islice(cycle(streamtypelist), currentindex + 1, None)
        self.servicetype = str(next(nextStreamType))
        self.openTest(self.servicetype, url)

    def up(self):
        pass

    def down(self):
        self.up()

    def doEofInternal(self, playing):
        self.cancel()

    def __evEOF(self):
        self.end = True

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback is not None:
            self.infoCallback()

    def showAfterSeek(self):
        if isinstance(self, TvInfoBarShowHide):
            self.doShow()

    def cancel(self):
        if isfile('/tmp/hls.avi'):
            remove('/tmp/hls.avi')
        self.session.nav.stopService()
        self.session.nav.playService(SREF)
        aspect_manager.restore_aspect()
        self.close()

    def leavePlayer(self):
        self.cancel()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_m3u2(namex):
    if not Utils.checkInternet():
        return

    if exists(downloadparsa):
        xxxname = downloadparsa + str(namex) + '_conv.m3u'
        xxxnamex = downloadparsa + str(namex) + '.m3u'
    else:
        xxxname = '/tmp/' + str(namex) + '_conv.m3u'
        xxxnamex = '/tmp/' + str(namex) + '.m3u'

    if not exists(xxxname):
        return

    try:
        with open(xxxnamex, 'w') as out:
            out.write("#EXTM3U\n")
            with open(xxxname, 'rb') as src:
                lines = [x.decode('utf8').strip() for x in src]

            for line in lines:
                line = line.replace(' ', '%20')

                if line.startswith('#EXTINF'):
                    name = line.split(',', 1)[-1].replace('%20', ' ').rstrip('\n')
                    out.write('#EXTINF:-1,' + name + '\n')

                elif line.startswith("http"):
                    req = Request(line)
                    req.add_header(
                        'User-Agent',
                        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; '
                        'rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                    r = urlopen(req, None, 15)
                    content = r.read()
                    r.close()
                    if not content:
                        continue
                    if isinstance(content, bytes):
                        try:
                            content = content.decode("utf-8")
                        except Exception as e:
                            print("Error decoding content:", e)

                    n1 = content.find('class="myButton" id=')
                    n2 = content.find("</button></a>", n1)
                    content2 = content[n1:n2] if n1 != -1 and n2 != -1 else ''

                    if content2:
                        for url2 in compile(
                                r'<a href="(.+?)"><b', DOTALL).findall(content2):
                            if url2.startswith('http'):
                                out.write(url2.replace(' ', '%20') + '\n')

        convert_bouquet(namex)
    except Exception as e:
        print('make_m3u2 error:', e)


def convert_bouquet(namex):
    btype = "radio" if "radio" in namex.lower() else "tv"

    name_file = namex.replace("/", "_").replace(",", "").replace(" ", "-")
    cleanName = sub(r'[<>:"/\\|?*]', "_", str(name_file))
    cleanName = sub(r" ", "_", cleanName)
    cleanName = sub(r"\d+:\d+:[\d.]+", "_", cleanName)
    name_file = sub(r"_+", "_", cleanName)
    bouquetname = "userbouquet.{}.{}".format(name_file.lower(), btype.lower())

    print("Converting bouquet {}".format(name_file))

    if exists(downloadparsa):
        src_file = str(downloadparsa) + str(namex) + ".m3u"
    else:
        src_file = "/tmp/" + str(namex) + ".m3u"

    if not exists(src_file):
        return

    path1 = "/etc/enigma2/" + str(bouquetname)
    path2 = "/etc/enigma2/bouquets." + str(btype.lower())

    if stat(src_file).st_size == 0:
        return

    tmplist = [
        "#NAME {} ({})".format(name_file.upper(), btype.upper()),
        "#SERVICE 1:64:0:0:0:0:0:0:0:0::{} CHANNELS".format(name_file),
        "#DESCRIPTION --- {} ---".format(name_file),
    ]

    namel = ""
    servicez = ""
    descriptionz = ""

    with open(src_file) as src:
        for line in src:
            if line.startswith("#EXTINF"):
                namel = "{}".format(line.split(",", 1)[-1])
                descriptionz = "".join(
                    ("#DESCRIPTION %s" % namel).splitlines())
            elif line.startswith("http"):
                tag = "2" if btype.upper() == "RADIO" else "1"
                servicea = "#SERVICE 4097:0:{}:0:0:0:0:0:0:0:{}".format(
                    tag, line.replace(":", "%3a"))
                servicez = "".join(
                    (servicea + ":" + namel).splitlines())

            if servicez not in tmplist:
                tmplist.append(servicez)
                tmplist.append(descriptionz)

    with open(path1, "w+") as fh:
        existing = fh.read()
        for item in tmplist:
            if item not in existing:
                fh.write("%s\n" % item)
                print("item -------- ", item)

    in_bouquets = 0
    if exists(path2):
        with open(path2) as fh:
            for line in fh:
                if bouquetname in line:
                    in_bouquets = 1
                    break

    if in_bouquets == 0:
        with open(path2, "a+") as fh:
            fh.write(
                '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "'
                + str(bouquetname) + '" ORDER BY bouquet\n')

    try:
        from enigma import eDVBDB
        eDVBDB.getInstance().reloadServicelist()
        eDVBDB.getInstance().reloadBouquets()
        print("all bouquets reloaded...")
    except Exception:
        os_system(
            "wget -qO - http://127.0.0.1/web/servicelistreload?mode=2 "
            "> /dev/null 2>&1 &")
        print("bouquets reloaded...")

    _session.open(
        MessageBox, _("Bouquets reloaded."),
        MessageBox.TYPE_INFO, timeout=5)


# ---------------------------------------------------------------------------
# Plugin entry points
# ---------------------------------------------------------------------------

def main(session, **kwargs):
    try:
        session.open(MainParsa)
    except Exception:
        import traceback
        traceback.print_exc()


def Plugins(**kwargs):
    ico_path = "logo.png"
    if not exists("/var/lib/dpkg/status"):
        ico_path = plugin_path + "/res/pics/logo.png"
    extensions_menu = PluginDescriptor(
        name=title_plug,
        description=desc_plugin,
        where=PluginDescriptor.WHERE_EXTENSIONSMENU,
        fnc=main,
        needsRestart=True,
    )
    result = [
        PluginDescriptor(
            name=title_plug,
            description=desc_plugin,
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon=ico_path,
            fnc=main,
        ),
        extensions_menu,
    ]
    return result
