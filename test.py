from GetCommitLines import get_lines_changed_per_day
import requests
import json


reqdat = get_lines_changed_per_day(["C:/Users/ggijs/Projecton", "C:/Users/ggijs/dupunkto"], ['ckvsite', 'gijs6.nl', 'meliag', 'gss', 'school.gijs6.nl', 'somplus'], ["json"])

print(json.dumps(reqdat, indent=4))
