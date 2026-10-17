import test from "node:test";
import assert from "node:assert/strict";
import { getFieldValidationError } from "./liveFormValidation.js";

const makeField = (options = {}) => ({
  tagName: "INPUT",
  type: "text",
  value: "",
  name: "",
  id: "",
  labels: [],
  placeholder: "",
  required: false,
  min: "",
  max: "",
  minLength: -1,
  maxLength: -1,
  inputMode: "",
  dataset: {},
  validity: {},
  parentElement: { querySelector: () => null },
  getAttribute: () => null,
  ...options,
});

test("required fields stay quiet until touched and show a French message on blur/submit", () => {
  const field = makeField({ required: true, name: "name" });
  assert.equal(getFieldValidationError(field), "");
  assert.match(getFieldValidationError(field, { showRequired: true }), /obligatoire/);
});

test("person name rejects digits and accepts accented letters, spaces, apostrophes, and hyphens", () => {
  assert.match(getFieldValidationError(makeField({ name: "name", value: "123456" })), /nom doit contenir des lettres/);
  assert.match(getFieldValidationError(makeField({ name: "first_name", value: "42" })), /prénom doit contenir des lettres/);
  assert.equal(getFieldValidationError(makeField({ name: "name", value: "Léa O’Neil-Diallo" })), "");
});

test("email format is checked and correction clears the error", () => {
  assert.match(getFieldValidationError(makeField({ type: "email", name: "email", value: "bineta@" })), /adresse e-mail valide/);
  assert.equal(getFieldValidationError(makeField({ type: "email", name: "email", value: "bineta@example.org" })), "");
});

test("telephone fields reject letters and accept Senegalese digits with formatting", () => {
  assert.match(getFieldValidationError(makeField({ type: "tel", name: "telephone", value: "abcdef" })), /uniquement des chiffres/);
  assert.equal(getFieldValidationError(makeField({ type: "tel", name: "telephone", value: "+221 77 000 00 00" })), "");
});

test("number fields report text and negative amounts", () => {
  assert.match(getFieldValidationError(makeField({ type: "number", value: "", validity: { badInput: true } })), /nombre valide/);
  assert.match(getFieldValidationError(makeField({ type: "number", name: "montant", value: "-2" })), /supérieur à 0/);
  assert.match(getFieldValidationError(makeField({ type: "text", name: "budget", value: "abc" })), /nombre valide/);
});

test("a budget select accepts its UUID instead of treating it as an amount", () => {
  const budget = makeField({
    tagName: "SELECT",
    type: "select-one",
    name: "budget",
    value: "550e8400-e29b-41d4-a716-446655440000",
    labels: [{ textContent: "Budget associé" }],
  });
  assert.equal(getFieldValidationError(budget), "");
});

test("percentages must remain between zero and one hundred", () => {
  assert.match(getFieldValidationError(makeField({ type: "number", name: "pourcentage", value: "101" })), /entre 0 et 100/);
  assert.equal(getFieldValidationError(makeField({ type: "number", name: "pourcentage", value: "75" })), "");
});

test("URL and date fields have French errors and accept valid values", () => {
  assert.match(getFieldValidationError(makeField({ type: "url", value: "not-a-url" })), /URL valide/);
  assert.equal(getFieldValidationError(makeField({ type: "url", value: "https://example.org/path" })), "");
  assert.match(getFieldValidationError(makeField({ type: "date", value: "not-a-date" })), /date valide/);
  assert.equal(getFieldValidationError(makeField({ type: "date", value: "2026-10-06" })), "");
});

test("HTML min, max, minlength, maxlength, and pattern constraints are respected", () => {
  assert.match(getFieldValidationError(makeField({ type: "number", value: "2", min: "5", validity: { rangeUnderflow: true } })), /au moins 5/);
  assert.match(getFieldValidationError(makeField({ type: "number", value: "12", max: "10", validity: { rangeOverflow: true } })), /dépasser 10/);
  assert.match(getFieldValidationError(makeField({ value: "a", minLength: 3 })), /au moins 3 caractères/);
  assert.match(getFieldValidationError(makeField({ value: "abcdef", maxLength: 4 })), /dépasser 4 caractères/);
  assert.equal(getFieldValidationError(makeField({ value: "abc", validity: { patternMismatch: true }, dataset: { errorPattern: "Format personnalisé." } })), "Format personnalisé.");
});

test("required select, checkbox, radio, and file fields are checked", () => {
  assert.match(getFieldValidationError(makeField({ tagName: "SELECT", type: "select-one", required: true }), { showRequired: true }), /sélectionner une option/);
  assert.match(getFieldValidationError(makeField({ type: "checkbox", required: true, checked: false }), { showRequired: true }), /cocher cette case/);
  const radio = makeField({ type: "radio", name: "choice", required: true, checked: false });
  radio.form = { elements: [radio, makeField({ type: "radio", name: "choice", checked: false })] };
  assert.match(getFieldValidationError(radio, { showRequired: true }), /sélectionner une option/);
  assert.match(getFieldValidationError(makeField({ type: "file", required: true, files: [] }), { showRequired: true }), /Veuillez joindre/);
});

test("password length and confirmation rules are checked", () => {
  assert.match(getFieldValidationError(makeField({ type: "password", name: "password", value: "abc", minLength: 8 })), /au moins 8 caractères/);
  const original = makeField({ type: "password", name: "password", value: "Secure123!" });
  const confirmation = makeField({ type: "password", name: "password_confirmation", value: "Different123!" });
  confirmation.form = { querySelectorAll: () => [original, confirmation] };
  assert.match(getFieldValidationError(confirmation), /ne correspondent pas/);
});

test("optional empty fields do not show an error before use", () => {
  assert.equal(getFieldValidationError(makeField({ name: "name" })), "");
  assert.equal(getFieldValidationError(makeField({ type: "email", name: "email" })), "");
});

test("valid select and checkbox values clear required errors", () => {
  assert.equal(getFieldValidationError(makeField({ tagName: "SELECT", type: "select-one", required: true, value: "project-1" }), { showRequired: true }), "");
  assert.equal(getFieldValidationError(makeField({ type: "checkbox", required: true, checked: true }), { showRequired: true }), "");
});

test("a selected required radio option satisfies its group", () => {
  const radio = makeField({ type: "radio", name: "choice", required: true, checked: false });
  const selected = makeField({ type: "radio", name: "choice", checked: true });
  radio.form = { elements: [radio, selected] };
  assert.equal(getFieldValidationError(radio, { showRequired: true }), "");
});

test("file accept rules allow a matching PDF and reject another format", () => {
  const pdf = makeField({ type: "file", name: "document", required: true, accept: ".pdf,application/pdf", files: [{ name: "statuts.pdf", type: "application/pdf" }], value: "statuts.pdf" });
  const image = makeField({ ...pdf, files: [{ name: "photo.png", type: "image/png" }], value: "photo.png" });
  assert.equal(getFieldValidationError(pdf, { showRequired: true }), "");
  assert.match(getFieldValidationError(image, { showRequired: true }), /format demandé/);
});

test("valid phone, percentage, password, and date values clear their errors", () => {
  assert.equal(getFieldValidationError(makeField({ type: "tel", name: "phone", value: "77 000 00 00" })), "");
  assert.equal(getFieldValidationError(makeField({ type: "number", name: "percentage", value: "0" })), "");
  assert.equal(getFieldValidationError(makeField({ type: "password", name: "password", value: "secure123", minLength: 8 })), "");
  assert.equal(getFieldValidationError(makeField({ type: "date", name: "start_date", value: "2026-10-06" })), "");
});
