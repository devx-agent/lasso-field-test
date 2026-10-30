import asyncio,json,os,sys
sys.argv=['x']; exec(open('ws_test.py').read().split('async def main')[0])
async def main():
    base=W.split('/profile/')[0]+'/profile/public'
    h={'authorization':'Bearer '+K}
    r=await asyncio.gather(sub('base public ws',base+'/base',h),sub('tempo public ws',base+'/tempo',h),sub('arbitrum public ws',base+'/arbitrum',h),sub('ethereum public ws',base+'/ethereum',h))
    json.dump(r,open('ws_public_result.json','w'),indent=1)
    for x in r: print(x['name'],'heads',x['heads'],'gaps',x['gaps'],'dups',x['dups'],'reconn',x['reconnects'],'first_ms',x['first_ms'],'errs',x['errors'][:2])
asyncio.run(main())
