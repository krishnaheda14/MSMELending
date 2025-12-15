import json
p='analytics/CUST_MSM_00005_earnings_spendings.json'
with open(p) as f:
    d=json.load(f)
mi=d.get('cashflow_metrics',{}).get('monthly_inflow',{})
# collect numeric entries
pairs=[]
for k,v in mi.items():
    try:
        val=float(v)
    except:
        continue
    pairs.append((k,val))
pairs_sorted=sorted(pairs, key=lambda x: x[1], reverse=True)
print('Top 10 monthly inflows:')
for k,v in pairs_sorted[:10]:
    print(f'{k}: {v:,.2f}')
print('\nMonths > 500k:')
for k,v in pairs_sorted:
    if v>500000:
        print(f'{k}: {v:,.2f}')
print('\nTotal months counted:', len(pairs))
# compute mean/std
import math
vals=[v for _,v in pairs]
if vals:
    mean=sum(vals)/len(vals)
    var=sum((x-mean)**2 for x in vals)/len(vals)
    std=math.sqrt(var)
    cv=std/mean if mean else None
    print(f"\nComputed monthly CV: mean={mean:,.2f}, std={std:,.2f}, cv={cv:.4f}")
else:
    print('No numeric monthly inflows found')
