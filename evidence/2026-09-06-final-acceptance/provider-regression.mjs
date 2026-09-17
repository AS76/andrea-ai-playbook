import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {pathToFileURL} from 'node:url';
const dist=process.argv[2] ?? '/usr/lib/node_modules/openclaw/dist';
const file=fs.readdirSync(dist).find(f=>/^model-auth-provider-config-.*\.js$/.test(f));
const text=fs.readFileSync(`${dist}/${file}`,'utf8');
const snapshotFile=text.match(/from "\.\/(runtime-snapshot-[^"]+)"/)[1];
const mod=await import(pathToFileURL(`${dist}/${file}`));
const snap=await import(pathToFileURL(`${dist}/${snapshotFile}`));
const match=mod.u, publish=snap.E, metadata=snap.s, clear=snap.t;
const cfg=(credential='test-a')=>({models:{providers:{p:{apiKey:credential,baseUrl:'https://example.invalid',models:Array.from({length:406},(_,i)=>({id:`m${i}`,name:`m${i}`}))},q:{apiKey:'test-q',models:[]}}}});
const call=(inputConfig,runtimeConfig,provider='p')=>match({inputConfig,runtimeConfig,provider});
const baseline=(a,b,p='p')=>!a?.models?.providers?.[p]||!b?.models?.providers?.[p]?false:snap.d({models:{providers:{[p]:a.models.providers[p]}}})===snap.d({models:{providers:{[p]:b.models.providers[p]}}});
let count=0;const test=(name,fn)=>{fn();count++;console.log(`PASS ${name}`)};
let a=cfg(),b=cfg();
test('same identity',()=>assert.equal(call(a,a),true));
test('structurally equivalent distinct configs',()=>assert.equal(call(a,b),true));
test('different credentials and provider settings',()=>{assert.equal(call(a,cfg('test-b')),false);let x=cfg();x.models.providers.p.baseUrl='https://different.invalid';assert.equal(call(a,x),false)});
test('repeated calls',()=>{for(let i=0;i<1000;i++)assert.equal(call(a,b),true)});
test('real publication metadata identity and revision',()=>{publish(b,b);const m=metadata();assert.equal(m,metadata());assert.equal(m,metadata());publish(b,b);assert.notEqual(m,metadata());assert.equal(metadata().revision,m.revision+1);assert.equal(call(a,b),true)});
test('real source-only publication lifecycle',()=>{const m=metadata();assert.equal(snap.O({expectedRevision:m.revision,sourceConfig:cfg()}),true);assert.notEqual(metadata(),m);assert.equal(metadata().revision,m.revision+1)});
test('config replacement',()=>{b=cfg('test-c');publish(b,b);assert.equal(call(a,b),false);b=cfg();publish(b,b);assert.equal(call(a,b),true)});
test('mutation without publication remains observable',()=>{const m=metadata();b.models.providers.p.apiKey='mutated';assert.equal(metadata(),m);assert.equal(call(a,b),false);b.models.providers.p.apiKey='test-a';assert.equal(call(a,b),true);b.models.providers.p.models[0].name='changed';assert.equal(call(a,b),false);b.models.providers.p.models[0].name='m0';assert.equal(call(a,b),true)});
test('missing provider',()=>{assert.equal(call(a,b,'absent'),false);assert.equal(call({},b),false);assert.equal(call(a,null),false)});
test('multiple providers',()=>{assert.equal(call(a,b,'q'),true);b.models.providers.q.apiKey='test-other';assert.equal(call(a,b,'q'),false);assert.equal(call(a,b,'p'),true)});
test('clear reset and reused revision',()=>{const m=metadata();clear();assert.equal(metadata(),null);publish(b,b);assert.notEqual(metadata(),m);assert.equal(metadata().revision,1);assert.equal(call(a,b),true)});
test('canonical hash fallback equivalence including undefined/null',()=>{for(const value of [null,undefined,0,-0,false,'',NaN,Infinity]){let x=cfg(),y=cfg();x.models.providers.p.extra=value;y.models.providers.p.extra=null;assert.equal(call(x,y),baseline(x,y))}});
test('reference comparison matrix',()=>{for(let i=0;i<100;i++){const x=cfg(`test-${i%7}`),y=cfg(`test-${i%5}`);assert.equal(call(x,y),baseline(x,y))}});
test('canonical edge cases, key ordering and sparse arrays',()=>{
 const cases=[[{a:1,b:2},{b:2,a:1}],[{a:undefined},{a:null}],[[,1],[undefined,1]],[[,],[,]],[[null],[undefined]],[{a:[{b:0}]},{a:[{b:-0}]}]];
 for(const [left,right] of cases){let x=cfg(),y=cfg();x.models.providers.p.extra=left;y.models.providers.p.extra=right;assert.equal(call(x,y),baseline(x,y));}
});
test('deterministic generated canonical differential corpus',()=>{
 let seed=17;const next=()=>seed=(Math.imul(seed,1664525)+1013904223)>>>0;
 const gen=(depth)=>{let k=next()%8;if(depth===0||k<4)return [null,undefined,next()%50,`s${next()%13}`,false,true,NaN,Infinity][next()%8];if(k<6)return Array.from({length:next()%5},()=>gen(depth-1));const o={};for(let i=0,n=next()%5;i<n;i++)o[`k${next()%9}`]=gen(depth-1);return o};
 for(let i=0;i<1000;i++){const x=cfg(),y=cfg();x.models.providers.p.extra=gen(3);y.models.providers.p.extra=i%2?structuredClone(x.models.providers.p.extra):gen(3);assert.equal(call(x,y),baseline(x,y));}
});
const t=performance.now();for(let i=0;i<1000;i++)call(a,a);console.log(`same-object 1000 calls: ${(performance.now()-t).toFixed(1)}ms`);
if(process.argv[3]) test('prior cache mutation bug reproduced and corrected',()=>{
 const prior=fs.readFileSync(process.argv[3],'utf8');
 const start=prior.indexOf('let providerSnapshotMatchMetadata;');const end=prior.indexOf('\nfunction sentinelizeConfigSecretRefEnvApiKey',start);
 const ctx=vm.createContext({getRuntimeConfigSnapshotMetadata:snap.s,resolveProviderConfig:mod._,hashRuntimeConfigValue:snap.d});
 vm.runInContext(prior.slice(start,end)+'\nthis.match=providerConfigMatchesRuntimeSnapshot;',ctx);
 const x=cfg(),y=cfg();publish(y,y);assert.equal(ctx.match({inputConfig:x,runtimeConfig:y,provider:'p'}),true);
 y.models.providers.p.apiKey='mutated2';
 assert.equal(ctx.match({inputConfig:x,runtimeConfig:y,provider:'p'}),true);
 assert.equal(call(x,y),false);assert.equal(baseline(x,y),false);
});
const x=cfg(),y=cfg();for(const [name,fn] of [['upstream canonical hash',baseline],['stateless canonical comparison',call]]){const start=performance.now();for(let i=0;i<100;i++)assert.equal(fn(x,y),true);console.log(`${name} 100 equivalent comparisons: ${(performance.now()-start).toFixed(1)}ms`);}
clear();console.log(`PASS ${count} actual-distribution regression groups`);
