import test from "node:test";
import assert from "node:assert/strict";
import { profile, peak } from "../web/sea-model.mjs";

test("hourly peaks retain zero and skip missing readings", () => {
  const record = {
    entries: {
      "2025|Fall|MF": {
        Southbound: { 0: null, 8: 0, 16: 1052.1 },
        Northbound: { 17: 981.7 },
      },
    },
  };
  const day = profile(record, 2025, "Fall", "MF");
  assert.deepEqual(peak(day.Southbound), ["16", 1052.1]);
  assert.deepEqual(peak(day.Northbound), ["17", 981.7]);
  assert.deepEqual(peak({ 0: null, 6: 0 }), ["6", 0]);
  assert.equal(peak({ 0: null }), null);
  assert.deepEqual(profile(record, 2025, "Fall", "Sat"), {});
});
