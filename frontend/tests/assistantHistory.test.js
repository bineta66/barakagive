import test from "node:test"
import assert from "node:assert/strict"
import {
  assistantIdentityKey,
  clearAssistantHistoryStorage,
  redactHistoryText,
} from "../src/services/assistantHistory.js"

test("assistant histories get distinct keys per user and organization", () => {
  const userA = assistantIdentityKey({ id: 10, organization: 3 })
  const userB = assistantIdentityKey({ id: 11, organization: 3 })
  const otherOrg = assistantIdentityKey({ id: 10, organization: 4 })
  assert.notEqual(userA, userB)
  assert.notEqual(userA, otherOrg)
})

test("stored history masks contact PII while preserving finance figures", () => {
  const safe = redactHistoryText("Budget 15 000 000 FCFA; mail test@example.test; tel 770000000")
  assert.match(safe, /15 000 000 FCFA/)
  assert.doesNotMatch(safe, /test@example\.test|770000000/)
})

test("logout cleanup clears assistant histories and saved audio databases", () => {
  const values = new Map([
    ["barakagive_assistant_history:3:10", "history"],
    ["barakagive_finance_assistant_history:3:10", "finance"],
    ["barakagive_assistant_session:3:10", "session"],
    ["unrelated-setting", "keep"],
  ])
  const deletedDatabases = []
  globalThis.localStorage = {
    get length() { return values.size },
    key(index) { return [...values.keys()][index] ?? null },
    getItem(key) { return values.get(key) ?? null },
    setItem(key, value) { values.set(key, value) },
    removeItem(key) { values.delete(key) },
  }
  globalThis.indexedDB = { deleteDatabase(name) { deletedDatabases.push(name) } }
  clearAssistantHistoryStorage()
  assert.deepEqual([...values.keys()], ["unrelated-setting"])
  assert.deepEqual(deletedDatabases.sort(), ["BarakaGiveAssistantAudio", "BarakaGiveFinanceVoice"])
  delete globalThis.localStorage
  delete globalThis.indexedDB
})
