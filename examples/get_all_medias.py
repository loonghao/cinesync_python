import sys

import cinesync

with cinesync.EventHandler() as evt:
    if evt.is_offline(): sys.exit()
    for g in evt.get_groups():
        print evt.get_medias_from_group(g)
