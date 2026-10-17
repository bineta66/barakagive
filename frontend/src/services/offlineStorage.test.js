import test from "node:test";
import assert from "node:assert/strict";

const values = new Map();
globalThis.localStorage = {
  getItem: (key) => values.get(key) ?? null,
  setItem: (key, value) => values.set(key, String(value)),
  removeItem: (key) => values.delete(key),
};

const { offlineStorage } = await import("./offlineStorage.js");
const { default: syncDatabase } = await import("../stores/syncDB.js");

const setUser = (id, organization_id) => {
  localStorage.setItem("user", JSON.stringify({ id, organization_id }));
};

test("offline campaign, zone and form caches are isolated by organization and user", () => {
  values.clear();
  setUser(101, 11);
  offlineStorage.saveCachedCampaigns([{ id: "campaign-a", name: "ONG A" }]);
  offlineStorage.saveCachedZones([{ id: "zone-a", name: "ONG A" }]);
  offlineStorage.saveCachedForm("campaign-a", { id: "form-a", title: "ONG A" });

  setUser(202, 22);
  assert.deepEqual(offlineStorage.getCachedCampaigns(), []);
  assert.deepEqual(offlineStorage.getCachedZones(), []);
  assert.equal(offlineStorage.getCachedForm("campaign-a"), null);

  setUser(101, 11);
  assert.equal(offlineStorage.getCachedCampaigns()[0].id, "campaign-a");
  assert.equal(offlineStorage.getCachedZones()[0].id, "zone-a");
  assert.equal(offlineStorage.getCachedForm("campaign-a").id, "form-a");
});

test("legacy unscoped offline caches are not exposed to a signed-in user", () => {
  values.clear();
  values.set("bg_cached_campaigns", JSON.stringify([{ id: "foreign-campaign" }]));
  values.set("bg_cached_zones", JSON.stringify([{ id: "foreign-zone" }]));
  values.set("bg_cached_forms", JSON.stringify({ campaign: { id: "foreign-form" } }));
  setUser(303, 33);

  assert.deepEqual(offlineStorage.getCachedCampaigns(), []);
  assert.deepEqual(offlineStorage.getCachedZones(), []);
  assert.equal(offlineStorage.getCachedForm("campaign"), null);
});

test("offline caches are separated after logout, organization changes, and account changes", () => {
  values.clear();
  localStorage.setItem("user", JSON.stringify({ id: 404, organization: { id: 44 } }));
  offlineStorage.saveCachedCampaigns([{ id: "campaign-44" }]);

  localStorage.removeItem("user");
  assert.deepEqual(offlineStorage.getCachedCampaigns(), []);
  assert.deepEqual(offlineStorage.getCachedZones(), []);
  assert.equal(offlineStorage.getCachedForm("campaign-44"), null);

  localStorage.setItem("user", JSON.stringify({ id: 404, organization: { id: 55 } }));
  assert.deepEqual(offlineStorage.getCachedCampaigns(), []);
  offlineStorage.saveCachedCampaigns([{ id: "campaign-55" }]);

  localStorage.setItem("user", JSON.stringify({ id: 505, organization: { id: 55 } }));
  assert.deepEqual(offlineStorage.getCachedCampaigns(), []);

  localStorage.setItem("user", JSON.stringify({ id: 404, organization: { id: 44 } }));
  assert.equal(offlineStorage.getCachedCampaigns()[0].id, "campaign-44");
  localStorage.setItem("user", JSON.stringify({ id: 404, organization: { id: 55 } }));
  assert.equal(offlineStorage.getCachedCampaigns()[0].id, "campaign-55");
});

test("offline sync database namespace changes on logout, organization change, and account change", () => {
  values.clear();
  localStorage.setItem("user", JSON.stringify({ id: 606, organization: { id: 66 } }));
  const organizationA = syncDatabase.name;

  localStorage.removeItem("user");
  assert.throws(() => syncDatabase.name, /session utilisateur/);

  localStorage.setItem("user", JSON.stringify({ id: 606, organization: { id: 77 } }));
  const organizationB = syncDatabase.name;
  assert.notEqual(organizationA, organizationB);

  localStorage.setItem("user", JSON.stringify({ id: 707, organization: { id: 77 } }));
  const otherUser = syncDatabase.name;
  assert.notEqual(organizationB, otherUser);
});
