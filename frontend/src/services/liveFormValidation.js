const FIELD_SELECTOR = "input, select, textarea";
const ERROR_CLASS = "live-form-field-error";
const INVALID_BORDER_CLASS = "border-red-500";
let nextId = 0;
let lastSubmittedForm = null;
let lastSubmittedAt = 0;

const normalize = (value) => String(value || "")
  .normalize("NFD")
  .replace(/[\u0300-\u036f]/g, "")
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, " ")
  .trim();

const fieldLabel = (field) => {
  const text = field.labels?.[0]?.textContent
    || field.parentElement?.querySelector(":scope > label")?.textContent
    || field.getAttribute("aria-label")
    || field.placeholder
    || field.name
    || "Ce champ";
  return text.replace(/[＊*]/g, "").replace(/\s+/g, " ").trim();
};

const keyOf = (field) => normalize(`${field.name} ${field.id} ${field.dataset.fieldName} ${fieldLabel(field)}`);
const groupFields = (field) => {
  if (!field.name || !field.form || !["radio", "checkbox"].includes(field.type)) return [field];
  return [...field.form.elements].filter((other) => other.name === field.name && other.type === field.type);
};

const requiredError = (field) => {
  if (field.type === "radio" || field.type === "checkbox") {
    const group = groupFields(field);
    if (group.some((item) => item.required) && !group.some((item) => item.checked)) {
      return field.type === "radio" ? "Veuillez sélectionner une option." : "Veuillez cocher cette case.";
    }
    return "";
  }
  if (!field.required && field.getAttribute("aria-required") !== "true") return "";
  if (field.type === "file") return field.files?.length ? "" : `Veuillez joindre « ${fieldLabel(field)} ».`;
  if (field.type === "checkbox") return field.checked ? "" : "Veuillez cocher cette case.";
  if (field.type === "select-one" || field.tagName === "SELECT") {
    return field.value ? "" : "Veuillez sélectionner une option.";
  }
  return String(field.value ?? "").trim() ? "" : `Ce champ est obligatoire : renseignez « ${fieldLabel(field)} ».`;
};

const getError = (field, { showRequired = false } = {}) => {
  const value = field.value == null ? "" : String(field.value).trim();
  const label = fieldLabel(field);
  const key = keyOf(field);
  if (field.validity?.badInput) {
    if (field.type === "number") return "Veuillez saisir un nombre valide.";
    if (field.type === "date") return "Veuillez saisir une date valide.";
    return `Saisissez une valeur valide pour « ${label} ».`;
  }
  const required = requiredError(field);
  if (required) return showRequired ? required : "";

  const validity = field.validity;
  if (!value && field.type !== "file") return "";
  if (validity?.typeMismatch) {
    if (field.type === "email") return "Veuillez saisir une adresse e-mail valide.";
    if (field.type === "url") return "Veuillez saisir une URL valide.";
  }
  if (validity?.patternMismatch) {
    if (field.type === "tel" || /(^| )(phone|telephone|tel|numero telephone)( |$)/.test(key)) {
      return "Le numéro de téléphone doit contenir uniquement des chiffres.";
    }
    if (/(^| )(name|nom|last name|lastname|nom complet|first name|firstname|prenom)( |$)/.test(key)) {
      return field.name?.includes("prenom") || key.includes("first name") || key.includes("prenom")
        ? "Le prénom doit contenir des lettres."
        : "Le nom doit contenir des lettres.";
    }
    return field.dataset.errorPattern || `Le format de « ${label} » n’est pas valide.`;
  }
  if (validity?.rangeUnderflow) return `La valeur doit être au moins ${field.min}.`;
  if (validity?.rangeOverflow) return `La valeur ne doit pas dépasser ${field.max}.`;
  if (validity?.stepMismatch) return `Choisissez une valeur autorisée pour « ${label} ».`;
  if (field.type === "password" && field.minLength > 0 && value.length < field.minLength) {
    return `Le mot de passe doit contenir au moins ${field.minLength} caractères.`;
  }
  if (field.minLength >= 0 && value.length < field.minLength) {
    return `Ce champ doit contenir au moins ${field.minLength} caractères.`;
  }
  if (field.maxLength >= 0 && value.length > field.maxLength) {
    return `Ce champ ne doit pas dépasser ${field.maxLength} caractères.`;
  }

  const isName = /(^| )(name|nom|last name|lastname|nom complet|first name|firstname|prenom)( |$)/.test(key);
  if (isName && field.type === "text" && !/^\p{L}+(?:[ '\u2019-]\p{L}+)*$/u.test(value)) {
    return field.name?.includes("prenom") || key.includes("first name") || key.includes("prenom")
      ? "Le prénom doit contenir des lettres."
      : "Le nom doit contenir des lettres.";
  }

  const isPhone = /(^| )(phone|telephone|tel|numero telephone)( |$)/.test(key) || field.type === "tel";
  if (isPhone && !/^[+\d() .-]+$/.test(value)) {
    return "Le numéro de téléphone doit contenir uniquement des chiffres.";
  }
  if (isPhone && value.replace(/\D/g, "").length < 7) {
    return "Saisissez un numéro de téléphone valide.";
  }

  if (field.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value)) {
    return "Veuillez saisir une adresse e-mail valide.";
  }
  if (field.type === "url" && !/^https?:\/\/[^\s.]+(?:\.[^\s.]+)+(?:\/[^\s]*)?$/i.test(value)) {
    return "Veuillez saisir une URL valide.";
  }

  if (field.type === "file" && field.files?.length && field.accept) {
    const accepted = field.accept.split(",").map((item) => item.trim().toLowerCase());
    const file = field.files[0];
    const matches = accepted.some((rule) => rule.startsWith(".")
      ? file.name.toLowerCase().endsWith(rule)
      : rule.endsWith("/*") ? file.type.startsWith(rule.slice(0, -1)) : file.type === rule);
    if (!matches) return `Le fichier « ${label} » doit respecter le format demandé.`;
  }

  if (field.type === "number" || field.inputMode === "numeric" || field.inputMode === "decimal"
    || (field.tagName !== "SELECT" && field.tagName !== "TEXTAREA"
      && /(^| )(amount|montant|budget|percentage|pourcentage|taux)( |$)/.test(key))) {
    const number = Number(value);
    if (!Number.isFinite(number)) return "Veuillez saisir un nombre valide.";
    const isPercentage = /(^| )(percentage|pourcentage|taux)( |$)/.test(key);
    const isAmount = /(^| )(amount|montant|budget)( |$)/.test(key);
    if (isPercentage && (number < 0 || number > 100)) {
      return "Le pourcentage doit être compris entre 0 et 100.";
    }
    if (isAmount && number <= 0) return "Le montant doit être supérieur à 0.";
  }

  if (field.type === "password" && /(^| )(confirm|confirmation|password confirm)( |$)/.test(key)) {
    const original = [...(field.form?.querySelectorAll('input[type="password"]') || [])]
      .find((other) => other !== field && !/(confirm|confirmation)/.test(keyOf(other)));
    if (original && value !== original.value) return "Les mots de passe ne correspondent pas.";
  }
  if (field.type === "date" && Number.isNaN(Date.parse(value))) return "Veuillez saisir une date valide.";
  return "";
};

export const getFieldValidationError = getError;

const ensureId = (field) => {
  if (!field.id) field.id = `live-form-field-${++nextId}`;
  return field.id;
};

const renderError = (field, message, host = field.parentElement, { force = false } = {}) => {
  if (!host) return;
  const id = ensureId(field);
  const errorId = `${id}-error`;
  let error = host.querySelector(`:scope > .${ERROR_CLASS}[id="${errorId}"]`);
  const hasCustomMessage = [...host.querySelectorAll(":scope > p")]
    .some((item) => item !== error
      && (item.getAttribute("role") === "alert" || /text-red-(500|600)/.test(item.className))
      && item.textContent.trim());
  if (hasCustomMessage && !force) {
    error?.remove();
    return;
  }
  if (!message) {
    error?.remove();
    field.removeAttribute("aria-invalid");
    field.classList.remove(INVALID_BORDER_CLASS);
    const describedBy = (field.getAttribute("aria-describedby") || "").split(/\s+/).filter((item) => item && item !== errorId);
    if (describedBy.length) field.setAttribute("aria-describedby", describedBy.join(" "));
    else field.removeAttribute("aria-describedby");
    return;
  }
  if (!error) {
    error = document.createElement("p");
    error.id = errorId;
    error.className = `${ERROR_CLASS} mt-1 text-xs text-red-600 flex items-center gap-1`;
    error.setAttribute("role", "alert");
    const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    icon.setAttribute("class", "w-4 h-4 text-red-500 shrink-0");
    icon.setAttribute("fill", "none");
    icon.setAttribute("viewBox", "0 0 24 24");
    icon.setAttribute("stroke", "currentColor");
    icon.setAttribute("stroke-width", "2.5");
    icon.setAttribute("aria-hidden", "true");
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("stroke-linecap", "round");
    path.setAttribute("stroke-linejoin", "round");
    path.setAttribute("d", "M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z");
    const text = document.createElement("span");
    error.append(icon, text);
    host.append(error);
  }
  error.querySelector("span").textContent = message;
  field.setAttribute("aria-invalid", "true");
  field.classList.add(INVALID_BORDER_CLASS);
  const describedBy = new Set((field.getAttribute("aria-describedby") || "").split(/\s+/).filter(Boolean));
  describedBy.add(errorId);
  field.setAttribute("aria-describedby", [...describedBy].join(" "));
};

const isFormField = (field) => field instanceof Element
  && field.matches(FIELD_SELECTOR)
  && field.closest("form")
  && !field.disabled
  && !field.readOnly
  && !["hidden", "submit", "button", "reset"].includes(field.type)
  && !field.hasAttribute("data-live-validation-ignore");

const validateEventField = (field, showRequired) => {
  if (!isFormField(field)) return;
  if (["radio", "checkbox"].includes(field.type) && groupFields(field)[0] !== field) return;
  const host = field.type === "radio" || field.type === "checkbox"
    ? (field.closest("fieldset") || field.parentElement)
    : field.parentElement;
  renderError(field, getError(field, { showRequired }), host);
};

export function installLiveFormValidation() {
  const setNoValidate = (node) => {
    if (node instanceof HTMLFormElement) node.noValidate = true;
    node.querySelectorAll?.("form").forEach((form) => { form.noValidate = true; });
  };
  setNoValidate(document);
  const formObserver = new MutationObserver((records) => {
    for (const record of records) {
      for (const node of record.addedNodes) {
        if (node instanceof Element) setNoValidate(node);
      }
    }
  });
  formObserver.observe(document.documentElement, { childList: true, subtree: true });

  const onInput = (event) => {
    const field = event.target;
    if (!isFormField(field)) return;
    field.closest("form")?.querySelector(":scope > .live-form-error-summary")?.remove();
    validateEventField(field, true);
  };
  const onBlur = (event) => validateEventField(event.target, true);
  const onSubmit = (event) => {
    let hasInvalidField = false;
    const handledGroups = new Set();
    for (const field of event.target.querySelectorAll(FIELD_SELECTOR)) {
      if (!isFormField(field)) continue;
      if (["radio", "checkbox"].includes(field.type)) {
        const groupKey = `${field.type}:${field.name || field.id}`;
        if (handledGroups.has(groupKey)) continue;
        handledGroups.add(groupKey);
      }
      const message = getError(field, { showRequired: true });
      if (message) hasInvalidField = true;
      validateEventField(field, true);
    }
    lastSubmittedForm = event.target;
    lastSubmittedAt = Date.now();
    if (hasInvalidField) {
      event.preventDefault();
      event.stopImmediatePropagation();
    }
  };

  document.addEventListener("input", onInput, true);
  document.addEventListener("change", onInput, true);
  document.addEventListener("focusout", onBlur, true);
  document.addEventListener("submit", onSubmit, true);

  return () => {
    formObserver.disconnect();
    document.removeEventListener("input", onInput, true);
    document.removeEventListener("change", onInput, true);
    document.removeEventListener("focusout", onBlur, true);
    document.removeEventListener("submit", onSubmit, true);
  };
}

export function showServerValidationErrors(error) {
  if (!lastSubmittedForm?.isConnected || Date.now() - lastSubmittedAt > 60000) return false;
  const body = error?.response?.data;
  if (!body || typeof body !== "object") return false;
  let displayed = false;

  for (const [key, rawMessages] of Object.entries(body)) {
    const messages = Array.isArray(rawMessages) ? rawMessages : [rawMessages];
    const message = messages.filter((item) => typeof item === "string").join(" ");
    if (!message) continue;
    const normalizedKey = normalize(key.replace(/_/g, " "));
    const fields = [...lastSubmittedForm.querySelectorAll(FIELD_SELECTOR)].filter(isFormField);
    const aliases = {
      name: ["nom"],
      first_name: ["prenom", "prénom"],
      last_name: ["nom"],
      phone: ["telephone", "téléphone", "tel"],
      telephone: ["phone", "tel"],
      amount: ["montant"],
      project: ["projet"],
      campaign: ["campagne"],
      region: ["région"],
      password_confirm: ["confirmation", "confirmer"],
    };
    const candidateLabels = [key, ...(aliases[key.replace(/\s+/g, "_")] || [])].map(normalize);
    const field = fields.find((item) => normalize(`${item.name} ${item.id} ${item.dataset.fieldName}`) === normalizedKey)
      || fields.find((item) => candidateLabels.some((candidate) => normalize(fieldLabel(item)) === candidate))
      || fields.find((item) => candidateLabels.some((candidate) => candidate.length > 2 && normalize(fieldLabel(item)).includes(candidate)));
    if (field) {
      validateEventField(field, false);
      const host = field.type === "radio" || field.type === "checkbox"
        ? (field.closest("fieldset") || field.parentElement)
        : field.parentElement;
      renderError(field, message, host, { force: true });
      displayed = true;
    } else if (["non field errors", "detail", "error"].includes(normalizedKey)) {
      let summary = lastSubmittedForm.querySelector(":scope > .live-form-error-summary");
      if (!summary) {
        summary = document.createElement("p");
        summary.className = "live-form-error-summary mb-3 text-sm text-red-600";
        summary.setAttribute("role", "alert");
        lastSubmittedForm.prepend(summary);
      }
      summary.textContent = message;
      displayed = true;
    }
  }
  return displayed;
}
