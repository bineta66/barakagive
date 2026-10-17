<template>
  <div class="font-sans text-slate-900 overflow-x-hidden">
    <!-- NAVBAR (réutilisée) -->
    <header
      class="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-slate-100 shadow-sm"
    >
      <div
        class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between"
      >
        <RouterLink to="/" class="flex items-center gap-3">
          <img
            src="@/assets/images/logologin.png"
            alt="BarakaGive"
            class="w-10 h-10 object-contain"
          />
          <div>
            <span class="text-lg font-bold text-[#061B2D]"
              >Baraka<span class="text-white">Give</span></span
            >
            <p class="text-[10px] text-slate-400 leading-none -mt-0.5">
              Ensemble pour un impact durable
            </p>
          </div>
        </RouterLink>

        <nav class="hidden lg:flex items-center gap-8">
          <RouterLink
            to="/"
            class="text-sm font-medium text-slate-600 hover:text-white transition relative group"
          >
            Accueil
            <span
              class="absolute -bottom-1 left-0 w-0 h-0.5 bg-white group-hover:w-full transition-all duration-300"
            ></span>
          </RouterLink>
          <RouterLink
            to="/"
            class="text-sm font-medium text-slate-600 hover:text-white transition relative group"
          >
            Fonctionnalités
            <span
              class="absolute -bottom-1 left-0 w-0 h-0.5 bg-white group-hover:w-full transition-all duration-300"
            ></span>
          </RouterLink>
          <RouterLink
            to="/"
            class="text-sm font-medium text-slate-600 hover:text-white transition relative group"
          >
            Avantages
            <span
              class="absolute -bottom-1 left-0 w-0 h-0.5 bg-white group-hover:w-full transition-all duration-300"
            ></span>
          </RouterLink>
          <RouterLink
            to="/"
            class="text-sm font-medium text-slate-600 hover:text-white transition relative group"
          >
            À propos
            <span
              class="absolute -bottom-1 left-0 w-0 h-0.5 bg-white group-hover:w-full transition-all duration-300"
            ></span>
          </RouterLink>
          <RouterLink
            to="/contact"
            class="text-sm font-semibold text-white transition relative"
          >
            Contact
            <span
              class="absolute -bottom-1 left-0 w-full h-0.5 bg-white"
            ></span>
          </RouterLink>
        </nav>

        <div class="flex items-center gap-3">
          <RouterLink
            to="/connexion"
            class="hidden sm:block text-sm font-semibold text-[#061B2D] border border-[#061B2D] px-4 py-2 rounded-lg hover:bg-[#061B2D] hover:text-white transition"
          >
            Se connecter
          </RouterLink>
          <RouterLink
            to="/inscription"
            class="text-sm font-semibold text-white bg-white px-4 py-2 rounded-lg hover:bg-white/90 transition shadow-sm"
          >
            Créer un compte
          </RouterLink>
        </div>
      </div>
    </header>

    <!-- HERO CONTACT -->
    <div
      class="pt-16 bg-gradient-to-br from-[#061B2D] via-[#0a2540] to-[#061B2D] py-20"
    >
      <div class="max-w-4xl mx-auto px-6 text-center">
        <div
          class="inline-flex items-center gap-2 bg-white/20 border border-white/40 rounded-full px-4 py-1.5 mb-6"
        >
          <div class="w-1.5 h-1.5 rounded-full bg-white"></div>
          
        </div>
        <h1 class="text-4xl font-extrabold text-white mb-4">
          Nous sommes à votre écoute
        </h1>
        <p class="text-slate-300 max-w-xl mx-auto">
          Notre équipe est disponible pour répondre à toutes vos questions sur
          BarakaGive et vous accompagner dans votre démarche.
        </p>
      </div>
    </div>

    <!-- CONTENU PRINCIPAL -->
    <div class="bg-white py-20">
      <div class="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-16">
        <!-- GAUCHE : Infos BarakaGive -->
        <div>
          <div class="w-12 h-0.5 bg-white mb-6"></div>
          <h2 class="text-2xl font-extrabold text-[#061B2D] mb-3">
            Informations de contact
          </h2>
          <p class="text-slate-500 text-sm leading-relaxed mb-10">
            Basée à Dakar, Sénégal, BarakaGive accompagne les ONG d'Afrique de
            l'Ouest dans leur transformation digitale. Notre équipe est là pour
            vous aider.
          </p>

          <!-- Coordonnées -->
          <div class="space-y-6">
            <div class="flex items-start gap-4">
              <div
                class="w-11 h-11 rounded-xl bg-white/10 flex items-center justify-center flex-shrink-0"
              >
                <svg
                  class="w-5 h-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </div>
              <div>
                <p class="font-semibold text-[#061B2D] text-sm">Adresse</p>
                <p class="text-slate-500 text-sm mt-0.5">
                  Dakar, Plateau — Sénégal
                </p>
                <p class="text-slate-400 text-xs mt-0.5">Afrique de l'Ouest</p>
              </div>
            </div>

            <div class="flex items-start gap-4">
              <div
                class="w-11 h-11 rounded-xl bg-white/10 flex items-center justify-center flex-shrink-0"
              >
                <svg
                  class="w-5 h-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <div>
                <p class="font-semibold text-[#061B2D] text-sm">Email</p>
                <a
                  href="mailto:contact@barakagive.org"
                  class="text-white text-sm mt-0.5 hover:underline"
                  >contact@barakagive.org</a
                >
                <p class="text-slate-400 text-xs mt-0.5">Réponse sous 24h</p>
              </div>
            </div>

            <div class="flex items-start gap-4">
              <div
                class="w-11 h-11 rounded-xl bg-white/10 flex items-center justify-center flex-shrink-0"
              >
                <svg
                  class="w-5 h-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                  />
                </svg>
              </div>
              <div>
                <p class="font-semibold text-[#061B2D] text-sm">Téléphone</p>
                <a
                  href="tel:+221770000000"
                  class="text-white text-sm mt-0.5 hover:underline"
                  >+221 77 000 00 00</a
                >
                <p class="text-slate-400 text-xs mt-0.5">Lun – Ven, 9h – 18h</p>
              </div>
            </div>

            <div class="flex items-start gap-4">
              <div
                class="w-11 h-11 rounded-xl bg-white/10 flex items-center justify-center flex-shrink-0"
              >
                <svg
                  class="w-5 h-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9"
                  />
                </svg>
              </div>
              <div>
                <p class="font-semibold text-[#061B2D] text-sm">Site web</p>
                <a
                  href="https://barakagive.org"
                  class="text-white text-sm mt-0.5 hover:underline"
                  >www.barakagive.org</a
                >
                <p class="text-slate-400 text-xs mt-0.5">
                  Plateforme SaaS pour ONG
                </p>
              </div>
            </div>
          </div>

          <!-- Réseaux sociaux -->
          <div class="mt-10 pt-8 border-t border-slate-100">
            <p class="text-sm font-semibold text-[#061B2D] mb-4">Suivez-nous</p>
            <div class="flex gap-3">
              <a
                href="#"
                class="w-10 h-10 rounded-xl bg-[#061B2D] flex items-center justify-center hover:bg-white transition"
              >
                <svg
                  class="w-4 h-4 text-white"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"
                  />
                </svg>
              </a>
              <a
                href="#"
                class="w-10 h-10 rounded-xl bg-[#061B2D] flex items-center justify-center hover:bg-white transition"
              >
                <svg
                  class="w-4 h-4 text-white"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"
                  />
                </svg>
              </a>
              <a
                href="#"
                class="w-10 h-10 rounded-xl bg-[#061B2D] flex items-center justify-center hover:bg-white transition"
              >
                <svg
                  class="w-4 h-4 text-white"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"
                  />
                </svg>
              </a>
            </div>
          </div>

          <!-- Carte / Map placeholder -->
          <div
            class="mt-10 rounded-2xl overflow-hidden border border-slate-200 h-48 bg-slate-50 flex items-center justify-center relative"
          >
            <div
              class="absolute inset-0 bg-gradient-to-br from-[#061B2D]/5 to-white/5"
            ></div>
            <div class="text-center relative z-10">
              <svg
                class="w-10 h-10 text-white/40 mx-auto mb-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.5"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <p class="text-sm font-semibold text-slate-600">Dakar, Plateau</p>
              <p class="text-xs text-slate-400">Sénégal, Afrique de l'Ouest</p>
            </div>
          </div>
        </div>

        <!-- DROITE : Formulaire -->
        <div>
          <div
            class="bg-white border border-slate-100 rounded-2xl shadow-sm p-8"
          >
            <div class="w-12 h-0.5 bg-white mb-6"></div>
            <h2 class="text-2xl font-extrabold text-[#061B2D] mb-2">
              Envoyez-nous un message
            </h2>
            <p class="text-slate-500 text-sm mb-8">
              Décrivez votre besoin et nous vous répondrons dans les plus brefs
              délais.
            </p>

            <!-- Information sur le mode d'envoi par courriel -->
            <div
              v-if="courrielPrepare"
              class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-xl flex items-center gap-3"
            >
              <svg
                class="w-5 h-5 text-blue-600 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p class="text-sm font-medium text-blue-800">
                Votre application de messagerie doit s’ouvrir. Le message ne sera
                envoyé qu’après confirmation dans cette application.
              </p>
            </div>

            <form @submit.prevent="envoyer" class="space-y-5">
              <!-- Nom + Prénom -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label
                    class="block text-xs font-bold uppercase text-slate-600 mb-1.5"
                    >Prénom *</label
                  >
                  <input
                    v-model="form.prenom"
                    type="text"
                    required
                    placeholder="Mamadou"
                    class="w-full h-11 border border-slate-200 rounded-lg px-3 text-sm focus:outline-none focus:border-white focus:ring-2 focus:ring-white/20 transition"
                  />
                </div>
                <div>
                  <label
                    class="block text-xs font-bold uppercase text-slate-600 mb-1.5"
                    >Nom *</label
                  >
                  <input
                    v-model="form.nom"
                    type="text"
                    required
                    placeholder="Diallo"
                    class="w-full h-11 border border-slate-200 rounded-lg px-3 text-sm focus:outline-none focus:border-white focus:ring-2 focus:ring-white/20 transition"
                  />
                </div>
              </div>

              <!-- Email -->
              <div>
                <label
                  class="block text-xs font-bold uppercase text-slate-600 mb-1.5"
                  >Email *</label
                >
                <input
                  v-model="form.email"
                  type="email"
                  required
                  placeholder="mamadou@ong.sn"
                  class="w-full h-11 border border-slate-200 rounded-lg px-3 text-sm focus:outline-none focus:border-white focus:ring-2 focus:ring-white/20 transition"
                />
              </div>

              <!-- Téléphone -->
              <div>
                <label
                  class="block text-xs font-bold uppercase text-slate-600 mb-1.5"
                  >Téléphone</label
                >
                <input
                  v-model="form.telephone"
                  type="tel"
                  placeholder="+221 77 000 00 00"
                  class="w-full h-11 border border-slate-200 rounded-lg px-3 text-sm focus:outline-none focus:border-white focus:ring-2 focus:ring-white/20 transition"
                />
              </div>

              <!-- Organisation -->
              <div>
                <label
                  class="block text-xs font-bold uppercase text-slate-600 mb-1.5"
                  >Nom de votre ONG</label
                >
                <input
                  v-model="form.organisation"
                  type="text"
                  placeholder="ONG Espoir Sénégal"
                  class="w-full h-11 border border-slate-200 rounded-lg px-3 text-sm focus:outline-none focus:border-white focus:ring-2 focus:ring-white/20 transition"
                />
              </div>

              <!-- Sujet -->
              <div>
                <label
                  class="block text-xs font-bold uppercase text-slate-600 mb-1.5"
                  >Sujet *</label
                >
                <select
                  v-model="form.sujet"
                  required
                  class="w-full h-11 border border-slate-200 rounded-lg px-3 text-sm focus:outline-none focus:border-white focus:ring-2 focus:ring-white/20 transition bg-white text-slate-700"
                >
                  <option value="">Sélectionnez un sujet</option>
                  <option value="demo">Demander une démo</option>
                  <option value="inscription">Inscription / Compte</option>
                  <option value="support">Support technique</option>
                  <option value="tarif">Tarifs & abonnement</option>
                  <option value="partenariat">Partenariat</option>
                  <option value="autre">Autre</option>
                </select>
              </div>

              <!-- Message -->
              <div>
                <label
                  class="block text-xs font-bold uppercase text-slate-600 mb-1.5"
                  >Message *</label
                >
                <textarea
                  v-model="form.message"
                  required
                  rows="5"
                  placeholder="Décrivez votre besoin ou votre question..."
                  class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-white focus:ring-2 focus:ring-white/20 transition resize-none"
                ></textarea>
              </div>

              <!-- Bouton envoi -->
              <button
                type="submit"
                :disabled="chargement"
                class="w-full h-12 bg-white hover:bg-white/90 text-white font-bold rounded-xl transition shadow-sm flex items-center justify-center gap-2 disabled:opacity-60 text-sm"
              >
                <span
                  v-if="chargement"
                  class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
                ></span>
                <svg
                  v-else
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
                {{ chargement ? "Envoi en cours..." : "Envoyer le message" }}
              </button>

              <p class="text-xs text-slate-400 text-center">
                En soumettant ce formulaire, vous acceptez que BarakaGive traite
                vos données pour vous répondre.
              </p>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- FOOTER -->
    <footer class="bg-[#061B2D] py-10 pb-28 lg:pb-10">
      <div
        class="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6"
      >
        <div class="flex items-center gap-3">
          <img
            src="@/assets/images/logologin.png"
            alt="BarakaGive"
            class="w-8 h-8 object-contain"
          />
          <span class="text-sm font-bold text-white"
            >Baraka<span class="text-white">Give</span></span
          >
        </div>
        <p class="text-xs text-slate-500">
          © 2026 BarakaGive · Dakar, Sénégal · Fait avec
          <span class="text-white">♡</span> pour les ONG
        </p>
        <RouterLink
          to="/"
          class="text-xs text-slate-400 hover:text-white transition"
          >← Retour à l'accueil</RouterLink
        >
      </div>
    </footer>

    <!-- Menu moderne iPhone flottant en bas pour la page Contact -->
    <LandingIPhoneBottomBar :active-section="'contact'" />
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { RouterLink } from "vue-router";
import LandingIPhoneBottomBar from "@/components/layout/LandingIPhoneBottomBar.vue";

const chargement = ref(false);
const courrielPrepare = ref(false);

const form = reactive({
  prenom: "",
  nom: "",
  email: "",
  telephone: "",
  organisation: "",
  sujet: "",
  message: "",
});

const envoyer = async () => {
  if (chargement.value) return;
  chargement.value = true;
  const sujet = encodeURIComponent(`[BarakaGive360] ${form.sujet}: ${form.prenom} ${form.nom}`);
  const corps = encodeURIComponent(
    `Nom : ${form.prenom} ${form.nom}\nEmail : ${form.email}\nTéléphone : ${form.telephone}\nOrganisation : ${form.organisation}\n\n${form.message}`
  );
  window.location.href = `mailto:contact@barakagive.org?subject=${sujet}&body=${corps}`;
  courrielPrepare.value = true;
  chargement.value = false;
};
</script>





