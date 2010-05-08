import cinesync

import os
import re
from urlparse import urlparse


class MediaBase:
    def __init__(self):
        self.user_data = ''
        self.active = False
        self.current_frame = 1
        self.groups = []

    def uses_pro_features(self):
        return False

    def is_valid(self):
        return (self.current_frame >= 1)

    @classmethod
    def load(cls, elem):
        return cinesync.csc_xml.media_from_xml(elem)


class MediaFile(MediaBase):
    def __init__(self, locator_arg=None):
        MediaBase.__init__(self)
        self.locator = MediaLocator(locator_arg)
        self.name = ''
        if self.locator and (self.locator.path or self.locator.url):
            s = self.locator.path or self.locator.url
            self.name = os.path.basename(urlparse(s).path)
        self.notes = ''
        self.annotations = MediaAnnotations()

    def is_valid(self):
        return MediaBase.is_valid(self) and \
               self.locator and self.locator.is_valid() and \
               self.name and \
               all([ann.is_valid() for ann in self.annotations.values()])

    def to_xml(self):
        return cinesync.csc_xml.media_file_to_xml(self)


class MediaAnnotations(dict):
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            ann = cinesync.FrameAnnotation(key)
            dict.__setitem__(self, key, ann)
            return ann


class GroupMovie(MediaBase):
    def __init__(self, group):
        MediaBase.__init__(self)
        self.group = group

    def uses_pro_features(self):
        return True

    def is_valid(self):
        return MediaBase.is_valid(self) and self.group

    def to_xml(self):
        return cinesync.csc_xml.group_movie_to_xml(self)


class MediaLocator:
    def __init__(self, path_or_url_or_hash=None):
        self.path = None
        self.url = None
        self.short_hash = None

        s = path_or_url_or_hash
        if s:
            maybe_url = urlparse(s)

            if os.path.exists(s):
                self.path = s
                self.short_hash = cinesync.short_hash(self.path)
            elif maybe_url and maybe_url.scheme and maybe_url.hostname:
                # The argument could be parsed as a URI (use it as a URL)
                self.url = maybe_url.geturl()
            elif re.match('^[0-9a-f]{40}$', s):
                # Length is 40 characters and consists of all hex digits; assume this is a short hash
                self.short_hash = s
            else:
                # Finally, assume it's a file path
                self.path = s

    def is_valid(self):
        return any([self.path, self.url, self.short_hash])

    @classmethod
    def load(cls, elem):
        return cinesync.csc_xml.media_locator_from_xml(elem)
