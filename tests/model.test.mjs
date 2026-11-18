import test from "node:test";
import assert from "node:assert/strict";
import {profile} from "../web/model.mjs";
test("averages weight observed dates and distinguish zero from missing",()=>{
  const cells=[["A","2025-01",0,7,20,2],["A","2025-02",0,7,60,3],["A","2025-02",6,8,0,1],["B","2025-02",0,7,55,1]];
  assert.equal(profile(cells,"A","work","all")[7].mean,16);
  assert.equal(profile(cells,"A","0","2025-01")[7].mean,10);
  const weekend=profile(cells,"A","weekend","all");
  assert.equal(weekend[8].mean,0);assert.equal(weekend[7].mean,null);
});
