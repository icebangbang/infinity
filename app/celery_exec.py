#!/Library/Frameworks/Python.framework/Versions/3.8/bin/python3.8
# -*- coding: utf-8 -*-
import re
import sys
from celery.__main__ import main
if __name__ == '__main__':

    # -A manage.celery worker -l info -P  gevent -Q day_level -c 1 -n worker-test
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
