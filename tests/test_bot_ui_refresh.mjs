import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,resolve} from "node:path";
import vm from "node:vm";

function harness() {
  const here=dirname(fileURLToPath(import.meta.url));
  const path=resolve(here,"../capt_bot/ui/app.js");
  const source=readFileSync(path,"utf8")
    .replace(/\nrefresh\(\);\s*setInterval\(refresh,\s*5000\);\s*$/, "\n");
  const elements=new Map();
  const element=(id)=>{
    if (!elements.has(id)) {
      elements.set(id,{
        textContent:"", disabled:false, hidden:false, open:false,
        classList:{add(){},remove(){},contains(){return false},toggle(){}},
        addEventListener(){},replaceChildren(){},append(){},focus(){},
      });
    }
    return elements.get(id);
  };
  const requests=[];
  const context=vm.createContext({
    document:{getElementById:element,addEventListener(){}},
    navigator:{clipboard:{writeText:async()=>{}}},
    window:{},console,
    setInterval(){},
    fetch:async(path)=>{
      requests.push(path);
      if (path==="/api/snapshot" && context.snapshotFailure)
        throw new Error("[Errno 2] No such file or directory");
      if (path==="/api/bots" && context.botsFailure)
        return {ok:false,status:503,json:async()=>({error:"Bot registry offline"})};
      return {ok:true,status:200,json:async()=>path==="/api/snapshot"?
        {control:{},execution:{}}:{bots:[]}};
    },
  });
  vm.runInContext(source,context,{filename:path});
  vm.runInContext(
    "renderRuntime = (_snapshot) => { document.getElementById('statusDot').classList.add('ok'); document.getElementById('statusText').textContent = 'RuntimeService connected'; };"+
    "renderBots = (_bots) => { document.getElementById('botList').textContent = 'Bot list updated'; };",
    context
  );
  return {context,element,requests,refresh:()=>vm.runInContext("refresh()",context)};
}

test("transient missing-file note clears only after authoritative snapshot recovery",async()=>{
  const h=harness();
  h.context.snapshotFailure=true;
  await h.refresh();
  assert.equal(h.element("statusText").textContent,"Runtime unavailable");
  assert.match(h.element("composerNote").textContent,/snapshot unavailable/);
  assert.doesNotMatch(h.element("composerNote").textContent,/Errno|file or directory/);
  h.context.snapshotFailure=false;
  h.context.botsFailure=true;
  await h.refresh();
  assert.equal(h.element("statusText").textContent,"RuntimeService connected");
  assert.match(h.element("composerNote").textContent,/reconnected/);
  assert.match(h.element("botList").textContent,/Bot registry temporarily unavailable/);
  assert.equal(h.requests.filter(x=>x==="/api/snapshot").length,2);
});

test("successful refresh preserves unrelated operator clarification message",async()=>{
  const h=harness();
  h.context.snapshotFailure=true;
  await h.refresh();
  h.element("composerNote").textContent="Operator must answer current clarification.";
  h.context.snapshotFailure=false;
  await h.refresh();
  assert.equal(h.element("statusText").textContent,"RuntimeService connected");
  assert.equal(h.element("composerNote").textContent,
               "Operator must answer current clarification.");
  assert.equal(h.element("botList").textContent,"Bot list updated");
});
