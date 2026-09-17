const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
function load(id, config, initialVault) {
 const hooks={}, writes=[], reads=[];
 const api={pluginConfig:config,on:(name,fn)=>hooks[name]=fn,logger:{info(){},debug(){}}};
 const sandbox={definePluginEntry:x=>x,existsSync:()=>true,
 readFileSync:p=>{reads.push(p);return JSON.stringify(initialVault??{current_timezone:'Asia/Tokyo'});},
 writeFileSync:(...a)=>writes.push(a),mkdirSync(){},homedir:()=>'/synthetic',
 resolve:require('node:path').resolve,dirname:require('node:path').dirname};
 let src=fs.readFileSync(`/root/.openclaw/workspace/main/plugins/${id}/dist/index.js`,'utf8').replace(/^import .*;\n/gm,'');
 src=src.replace('export default definePluginEntry(', 'globalThis.entry = definePluginEntry(').replace('export default plugin;', 'globalThis.entry = plugin;');
 vm.runInNewContext(src,sandbox);sandbox.entry.register(api);
 return {hooks,writes,reads};
}
const cv=load('context-vault',{vaultPath:'/synthetic/custom.json'}, {messages:[],savedAt:'synthetic'});
cv.hooks.before_compaction({messageCount:1,messages:[{role:'user',content:'Always preserve this synthetic directive.'}]},{agentId:'synthetic'});
assert.equal(cv.writes.length,0);
const ti=load('time-inject',{timezone:'Europe/Rome',useTravelTimezone:false});
const time=ti.hooks.before_prompt_build({}, {agentId:'synthetic'}).prependSystemContext;
assert(time.includes('timezone: Asia/Tokyo'));
assert(time.includes('source: travel_status'));
const result={test:'isolated actual plugin code with stubbed filesystem; no real conversation or travel file read',contextVault:{standardBeforeCompactionMessages:1,writes:cv.writes.length,verdict:'FAIL: event.messages ignored because plugin reads event.context'},timeInject:{configuredUseTravelTimezone:false,observedTravelRead:ti.reads.length>0,verdict:'FAIL: typed hook context lacks pluginConfig; configured false ignored'},productionFilesChanged:false};
console.log(JSON.stringify(result,null,2));
