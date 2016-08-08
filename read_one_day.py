import sys
import pickle
import os

DATA_ROOT = "data"

if __name__ == "__main__":
    f_name = sys.argv[1]
    sid = sys.argv[2]
    data = {}
    with open(os.path.join(DATA_ROOT, f_name), 'r') as f:
        data = pickle.load(f)
    for stock in data:
        if stock.get('id') == sid:
            print stock
            break
    else:
        print "Not exist"
