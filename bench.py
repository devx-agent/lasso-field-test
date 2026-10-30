import json,time,requests,statistics as st,os
S=json.load(open('os.environ.get('LASSO_JSON','lasso.json')')); U=S['rpc_url']; K=S['key']
pub=U.split('/rpc/')[0]+'/rpc/profile/public'
MAIN='0xB3cDDccEe6B150c8efFD55B961afc0Ecefe7f247'; TM='0x6e1A'  # TM wallet looked up below
USDC_BASE='0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
CLAIM_TX='0x4213dfed4a791ca304648b7d46eea71df0ba7eb3c92d3af030c791a339244326'
bal_data='0x70a08231'+MAIN[2:].lower().rjust(64,'0')
calls=[('eth_blockNumber',[]),('eth_getBalance',[MAIN,'latest']),('eth_call',[{'to':USDC_BASE,'data':bal_data},'latest']),('eth_getTransactionReceipt',[CLAIM_TX])]
direct={'base':'https://mainnet.base.org'}
out=[]
def rpc(url,m,p,hdr={}):
    t=time.time(); r=requests.post(url,json={'jsonrpc':'2.0','id':1,'method':m,'params':p},headers={'content-type':'application/json',**hdr},timeout=30); dt=(time.time()-t)*1000
    return r,dt
for name,url,h in [('lasso-premium-fastest',U+'/fastest/base?include_meta=body',{}),('lasso-public',pub+'/base?include_meta=body',{'authorization':'Bearer '+K}),('direct-base.org',direct['base'],{})]:
    for m,p in calls:
        lat=[]
        for i in range(5):
            r,dt=rpc(url,m,p,h); lat.append(dt)
        j=r.json(); meta=j.get('lasso_meta',{})
        res=j.get('result'); res=(res if isinstance(res,str) else ('status='+res['status'] if isinstance(res,dict) and 'status' in res else str(res)[:40])) if res is not None else j.get('error')
        out.append({'route':name,'method':m,'p50_ms':round(st.median(lat)),'max_ms':round(max(lat)),'result':str(res)[:66],'provider':meta.get('selected_provider') or meta.get('provider'),'strategy':meta.get('strategy'),'overhead_ms':meta.get('overhead_ms') or meta.get('overhead_latency_ms'),'req_id':r.headers.get('x-lasso-request-id'),'access':r.headers.get('x-lasso-access'),'usd':r.headers.get('x-lasso-usd'),'bal':r.headers.get('x-lasso-balance-usd'),'fallback':r.headers.get('x-lasso-fallback'),'http':r.status_code})
for o in out: print(json.dumps(o))
json.dump(out,open('bench_base.json','w'),indent=1)
print('meta sample',json.dumps(j.get('lasso_meta'))[:600] if 'lasso_meta' in j else '')
