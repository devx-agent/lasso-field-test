import asyncio,json,time,os,websockets,requests
S=json.load(open(os.environ.get('LASSO_JSON','lasso.json'))); W=S['ws_url']; K=S['key']
DUR=int(os.environ.get('DUR','240'))
async def sub(name,url,hdr=None):
    st={'name':name,'heads':0,'gaps':0,'dups':0,'reconnects':0,'first_ms':None,'meta_frames':0,'errors':[]}
    last=None; t0=time.time(); seen=set()
    while time.time()-t0<DUR:
        try:
            async with websockets.connect(url,additional_headers=hdr,open_timeout=15,ping_interval=20) as ws:
                await ws.send(json.dumps({'jsonrpc':'2.0','id':1,'method':'eth_subscribe','params':['newHeads']}))
                while time.time()-t0<DUR:
                    m=json.loads(await asyncio.wait_for(ws.recv(),timeout=30))
                    if m.get('method')=='eth_subscription':
                        n=int(m['params']['result']['number'],16)
                        if st['first_ms'] is None: st['first_ms']=round((time.time()-t0)*1000)
                        if n in seen: st['dups']+=1
                        elif last is not None and n>last+1: st['gaps']+=n-last-1
                        seen.add(n); last=max(last or n,n); st['heads']+=1
                    elif 'lasso_meta' in json.dumps(m)[:200]: st['meta_frames']+=1
        except Exception as e:
            st['errors'].append(type(e).__name__+':'+str(e)[:80]); st['reconnects']+=1; await asyncio.sleep(2)
    st['last']=last; st['secs']=DUR; return st
async def main():
    pub=W.split('/ws/')[0] if '/ws/' in W else None
    tasks=[sub('base premium ws',W+'/fastest/base'),sub('tempo premium ws',W+'/fastest/tempo'),sub('arbitrum premium ws',W+'/fastest/arbitrum')]
    r=await asyncio.gather(*tasks)
    print(json.dumps(r,indent=1)); json.dump(r,open('ws_result.json','w'),indent=1)
asyncio.run(main())
