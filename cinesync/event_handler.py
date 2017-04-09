import os
import sys
import xml.etree.cElementTree as ET
from optparse import OptionParser

import cinesync


class EventHandler(object):
    def __init__(self, argv=sys.argv, stdin=sys.stdin):
        try:
            self.session = cinesync.Session.load(stdin)
        except Exception:
            self.session = None

        parser = OptionParser()
        parser.add_option('--key')
        parser.add_option('--offline-key')
        parser.add_option('--user')
        parser.add_option('--save-format')
        parser.add_option('--save-dir')
        parser.add_option('--url')
        (options, rest_args) = parser.parse_args(argv[1:])
        if options.key is None: raise cinesync.CineSyncError('--key argument is required')
        if options.save_format is None: raise cinesync.CineSyncError('--save-format argument is required')
        self.session_key = options.key if options.key != cinesync.OFFLINE_KEY else None
        self.offline_session_key = options.offline_key if options.offline_key != cinesync.ONLINE_KEY else None
        self.save_format = options.save_format
        self.user = options.user
        self.save_ext = {'JPEG': 'jpg', 'PNG': 'png'}[self.save_format]
        self.save_parent = options.save_dir
        self.url = options.url

    def is_offline(self):
        return self.session_key == None

    def get_medias(self):
        medias = []
        if self.session:
            for m in self.session.media:
                medias.append(m.locator.path)
        return medias

    def get_groups(self):
        if self.session:
            return self.session.groups

    def get_medias_from_group(self, group_name):
        ns = '{%s}' % cinesync.SESSION_V3_NAMESPACE
        elem = ET.fromstring(self.session.to_xml())
        data = {}
        medias = []
        for e in elem.findall(ns + 'media'):
            group = e.findall(ns + 'group')
            if group is not None:
                s = []
                for g in group:
                    s.append(g.text)
                path = e.find(ns + 'locators/%spath' % ns).text
                if s:
                    data.update({path: s})
        for path, g in data.items():
            if group_name in g:
                medias.append(path)
        return medias

    def saved_frame_path(self, media_file, frame):
        if self.save_parent is None:
            return None
        if not media_file.annotations[frame].drawing_objects:
            return None

        base = '%s-%05d' % (media_file.name, frame)

        i = 1

        p2 = None
        while True:
            p = p2
            p2, i = self.__saved_frame_ver_path(base, i)
            if not os.path.exists(p2):
                return p

    def __saved_frame_ver_path(self, base, version):
        v = ' (%d)' % version if version > 1 else ''
        basename = base + v + '.' + self.save_ext
        return os.path.join(self.save_parent, basename), version + 1

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass
