import sys, os
import cPickle
pickle_file = sys.argv[1]
assert os.path.isfile(pickle_file)

results = cPickle.load(open(pickle_file,'rb'))

from pprint import pprint
all_apps = set()
from collections import defaultdict
coords = defaultdict(list)
app_totals = defaultdict(float)
app_totals_count = defaultdict(int)
app_failures = defaultdict(int)
for key, result in results.items():
    app, coord = key.split('__')
    all_apps.add(app)
    app_totals[app] += result[1]
    app_totals_count[app] += 1
    if result[0] == "FAILED":
        app_failures[app] += 1
    else:
        app_failures[app] += 0
    this_result = (result[0], result[1], '\n'.join(result[2]))
    if coord in coords:
        coords[coord][app] = this_result
    else:
        coords[coord] = {app:this_result}
    
all_apps = list(all_apps)
all_apps.sort()
coords = dict(coords)
print "\t", "App".ljust(15)
print "_"*70

for coord, results in coords.items():
    print coord.ljust(39), repr(results[all_apps[0]][2])
    for app in all_apps:
        print "\t",app.ljust(15),
        data = results[app]
        print str(data[1])[:7].ljust(15),
        if len(data[0]) > 50:
            print repr(data[0][:50])+'...'
        else:
            print repr(data[0][:50])
    print
        
        


print
print "FAILURES:"
for app, count in dict(app_failures).items():
    print app.ljust(20), count

print
print "TOTALS:"
for app, total in dict(app_totals).items():
    print app.ljust(20), str(total).ljust(20), total/app_totals_count[app], "seconds/request"
