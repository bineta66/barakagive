<template>
  <div class="font-sans text-slate-900 overflow-x-hidden">
    <!-- ═══════════════════════════════════════════
         NAVBAR
    ═══════════════════════════════════════════ -->
    <header
      class="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-slate-100 shadow-sm"
    >
      <div
        class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between"
      >
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center gap-3">
          <img
            src="@/assets/images/logologin.png"
            alt="BarakaGive"
            class="w-10 h-10 object-contain"
          />
          <div>
            <span class="text-lg font-bold text-[#061B2D]"
              >Baraka<span class="text-[#061B2D]">Give</span></span
            >
            <p class="text-[10px] text-slate-400 leading-none -mt-0.5">
              Ensemble pour un impact durable
            </p>
          </div>
        </RouterLink>

        <!-- Nav links -->
        <nav class="hidden lg:flex items-center gap-8">
          <a
            href="#hero"
            @click="setActive('accueil')"
            class="text-sm font-medium transition relative pb-1"
            :class="
              activeLink === 'accueil'
                ? 'text-[#061B2D]'
                : 'text-slate-600 hover:text-[#061B2D]'
            "
          >
            Accueil
            <span
              class="absolute bottom-0 left-0 h-0.5 bg-[#061B2D] transition-all duration-300"
              :class="activeLink === 'accueil' ? 'w-full' : 'w-0'"
            ></span>
          </a>
          <a
            href="#fonctionnalites"
            @click="setActive('fonctionnalites')"
            class="text-sm font-medium transition relative pb-1"
            :class="
              activeLink === 'fonctionnalites'
                ? 'text-[#061B2D]'
                : 'text-slate-600 hover:text-[#061B2D]'
            "
          >
            Fonctionnalités
            <span
              class="absolute bottom-0 left-0 h-0.5 bg-[#061B2D] transition-all duration-300"
              :class="activeLink === 'fonctionnalites' ? 'w-full' : 'w-0'"
            ></span>
          </a>
          <a
            href="#avantages"
            @click="setActive('avantages')"
            class="text-sm font-medium transition relative pb-1"
            :class="
              activeLink === 'avantages'
                ? 'text-[#061B2D]'
                : 'text-slate-600 hover:text-[#061B2D]'
            "
          >
            Avantages
            <span
              class="absolute bottom-0 left-0 h-0.5 bg-[#061B2D] transition-all duration-300"
              :class="activeLink === 'avantages' ? 'w-full' : 'w-0'"
            ></span>
          </a>
          <a
            href="#impact"
            @click="setActive('apropos')"
            class="text-sm font-medium transition relative pb-1"
            :class="
              activeLink === 'apropos'
                ? 'text-[#061B2D]'
                : 'text-slate-600 hover:text-[#061B2D]'
            "
          >
            À propos
            <span
              class="absolute bottom-0 left-0 h-0.5 bg-[#061B2D] transition-all duration-300"
              :class="activeLink === 'apropos' ? 'w-full' : 'w-0'"
            ></span>
          </a>
          <RouterLink
            to="/contact"
            class="text-sm font-medium transition relative pb-1 text-slate-600 hover:text-[#061B2D]"
          >
            Contact
            <span
              class="absolute bottom-0 left-0 w-0 h-0.5 bg-[#061B2D] transition-all duration-300 hover:w-full"
            ></span>
          </RouterLink>
        </nav>

        <!-- CTA -->
        <div class="flex items-center gap-3">
          <RouterLink
            to="/connexion"
            class="hidden sm:block text-sm font-semibold text-[#061B2D] border border-[#061B2D] px-4 py-2 rounded-lg hover:bg-[#061B2D] hover:text-white transition"
          >
            Se connecter
          </RouterLink>
          <RouterLink
            to="/inscription"
            class="text-sm font-semibold text-white bg-[#061B2D] px-4 py-2 rounded-lg hover:bg-[#0a2540] transition shadow-sm"
          >
            Créer un compte
          </RouterLink>
        </div>
      </div>
    </header>

    <!-- ═══════════════════════════════════════════
         HERO
    ═══════════════════════════════════════════ -->
    <section id="hero" class="pt-16 min-h-screen flex">
      <!-- Gauche : fond bleu nuit -->
      <div
        class="flex-1 bg-gradient-to-br from-[#061B2D] via-[#0a2540] to-[#061B2D] flex items-center px-8 lg:px-16 xl:px-24 py-20"
      >
        <div class="max-w-xl">
          <!-- Titre -->
          <h1
            class="hero-title text-4xl xl:text-5xl font-extrabold text-white leading-tight mb-6"
          >
            Simplifiez la gestion<br />
            de votre ONG et maximisez<br />
            <span class="text-white">votre impact</span>
          </h1>

          <!-- Sous-titre -->
          <p
            class="hero-sub text-slate-300 text-base leading-relaxed mb-10 max-w-md"
          >
            BarakaGive est une plateforme tout-en-un qui permet aux ONG de gérer
            leurs projets, leurs dons, leurs bénéficiaires et de suivre leur
            impact, le tout en toute simplicité et en toute sécurité.
          </p>

          <!-- Boutons -->
          <div class="hero-cta flex flex-col sm:flex-row gap-4">
            <RouterLink
              to="/inscription"
              class="inline-flex items-center justify-center gap-2 bg-[#061B2D] hover:bg-[#0a2540] text-white font-bold px-7 py-3.5 rounded-xl transition shadow-lg text-sm"
            >
              Créer un compte gratuitement
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M17 8l4 4m0 0l-4 4m4-4H3"
                />
              </svg>
            </RouterLink>
            <a
              href="#avantages"
              class="inline-flex items-center justify-center gap-2 border border-white/30 text-white hover:bg-white/10 font-semibold px-7 py-3.5 rounded-xl transition text-sm"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
              >
                <circle cx="12" cy="12" r="10" />
                <polygon fill="white" stroke="none" points="10,8 16,12 10,16" />
              </svg>
              Voir la démo
            </a>
          </div>
        </div>
      </div>

      <!-- Droite : photo -->
      <div
        class="hero-img hidden lg:block w-[45%] xl:w-[42%] relative overflow-hidden"
      >
        <img
          src="@/assets/images/imagelogo.png"
          alt="ONG BarakaGive"
          class="absolute inset-0 w-full h-full object-cover object-center"
        />
        <!-- Overlay léger -->
        <div
          class="absolute inset-0 bg-gradient-to-r from-[#061B2D]/60 via-transparent to-transparent"
        ></div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════
         COMMENT ÇA MARCHE
    ═══════════════════════════════════════════ -->
    <section class="bg-white py-24">
      <div class="max-w-4xl mx-auto px-6 text-center">
        <div class="reveal w-12 h-0.5 bg-[#061B2D] mx-auto mb-6"></div>
        <h2
          class="reveal text-3xl xl:text-4xl font-extrabold text-[#061B2D] mb-4"
        >
          Comment ça marche ?
        </h2>
        <p class="reveal text-slate-500 mb-14 max-w-lg mx-auto">
          En 3 étapes simples, votre ONG est opérationnelle sur BarakaGive.
        </p>

        <div class="grid md:grid-cols-3 gap-8">
          <div
            v-for="(step, i) in steps"
            :key="step.num"
            :class="`reveal reveal-delay-${i + 1}`"
            class="bg-white rounded-2xl p-8 border border-slate-100 shadow-sm hover:-translate-y-1 transition-transform duration-300"
          >
            <div
              class="w-10 h-10 rounded-xl bg-[#061B2D] text-white font-extrabold text-lg flex items-center justify-center mx-auto mb-5"
            >
              {{ step.num }}
            </div>
            <h3 class="font-bold text-[#061B2D] mb-3">{{ step.titre }}</h3>
            <p class="text-sm text-slate-500 leading-relaxed">
              {{ step.texte }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════
         FEATURES RAPIDES
    ═══════════════════════════════════════════ -->
    <section
      id="fonctionnalites"
      class="bg-[#061B2D] py-16 border-b border-white/10"
    >
      <div class="max-w-7xl mx-auto px-6">
        <div
          class="grid grid-cols-2 lg:grid-cols-4 gap-0 divide-x divide-white/10"
        >
          <div class="px-8 py-6 group reveal reveal-delay-1">
            <div
              class="icon-pop w-12 h-12 rounded-full bg-white/10 flex items-center justify-center mb-4 group-hover:bg-white/20 transition"
            >
              <svg
                class="w-6 h-6 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.8"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 class="font-bold text-white mb-2">Dons & Finances</h3>
            <p class="text-sm text-slate-300 leading-relaxed">
              Centralisez vos dons, suivez vos financements en temps réel.
            </p>
          </div>

          <div class="px-8 py-6 group reveal reveal-delay-2">
            <div
              class="icon-pop w-12 h-12 rounded-full bg-white/10 flex items-center justify-center mb-4 group-hover:bg-white/20 transition"
            >
              <svg
                class="w-6 h-6 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.8"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </div>
            <h3 class="font-bold text-white mb-2">Bénéficiaires</h3>
            <p class="text-sm text-slate-300 leading-relaxed">
              Identifiez, suivez et accompagnez vos bénéficiaires.
            </p>
          </div>

          <div class="px-8 py-6 group reveal reveal-delay-2">
            <div
              class="icon-pop w-12 h-12 rounded-full bg-white/10 flex items-center justify-center mb-4 group-hover:bg-white/20 transition"
            >
              <svg
                class="w-6 h-6 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.8"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <h3 class="font-bold text-white mb-2">Impact</h3>
            <p class="text-sm text-slate-300 leading-relaxed">
              Mesurez vos résultats et montrez votre impact.
            </p>
          </div>
          <div class="px-8 py-6 group reveal reveal-delay-3">
            <div class="icon-pop w-12 h-12 rounded-full bg-white/10 flex items-center justify-center mb-4 group-hover:bg-white/20 transition">
              <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 8.5A1.5 1.5 0 014.5 7H10l2 2h7.5A1.5 1.5 0 0121 10.5v7a1.5 1.5 0 01-1.5 1.5h-15A1.5 1.5 0 013 17.5v-9zM3 11h18" />
              </svg>
            </div>
            <h3 class="font-bold text-white mb-2">Projets</h3>
            <p class="text-sm text-slate-300 leading-relaxed">
              Planifiez, gérez et suivez vos projets humanitaires au même endroit.
            </p>
          </div>        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════
         SECTION PLATEFORME
    ═══════════════════════════════════════════ -->
    <section id="avantages" class="bg-slate-50 py-24">
      <div
        class="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-16 items-center"
      >
        <!-- Gauche : texte -->
        <div class="reveal-left">
          <div class="w-12 h-0.5 bg-[#061B2D] mb-6"></div>
          <h2
            class="text-3xl xl:text-4xl font-extrabold text-[#061B2D] leading-tight mb-5"
          >
            Une solution complète<br />pour les ONG
          </h2>
          <p class="text-slate-500 text-base leading-relaxed mb-8">
            BarakaGive offre un espace unique pour piloter votre organisation,
            de la gestion des projets à la collecte de dons, en passant par le
            suivi des bénéficiaires et la mesure de l'impact.
          </p>

          <ul class="space-y-4 mb-10">
            <li
              v-for="item in avantages"
              :key="item"
              class="flex items-start gap-3"
            >
              <div
                class="w-5 h-5 rounded-full bg-[#061B2D]/15 flex items-center justify-center flex-shrink-0 mt-0.5"
              >
                <svg
                  class="w-3 h-3 text-[#061B2D]"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="3"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <span class="text-slate-700 text-sm font-medium">{{ item }}</span>
            </li>
          </ul>

          <RouterLink
            to="/inscription"
            class="inline-flex items-center gap-2 bg-[#061B2D] hover:bg-[#0a2540] text-white font-bold px-6 py-3 rounded-xl transition shadow-sm text-sm"
          >
            Découvrir toutes les fonctionnalités
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M17 8l4 4m0 0l-4 4m4-4H3"
              />
            </svg>
          </RouterLink>
        </div>

        <!-- Droite : mockup dashboard -->
        <div class="relative reveal-right">
          <!-- Laptop -->
          <div class="relative z-10">
            <img
              src="@/assets/images/ordi.png"
              alt="Dashboard BarakaGive"
              class="w-full rounded-2xl"
            />
          </div>
          <!-- Décoration -->
          <div
            class="absolute -bottom-6 -right-6 w-32 h-32 bg-white/10 rounded-3xl -z-10"
          ></div>
          <div
            class="absolute -top-6 -left-6 w-20 h-20 bg-[#061B2D]/10 rounded-2xl -z-10"
          ></div>

          <!-- Badge flottant -->
          <div
            class="absolute -left-8 top-1/2 -translate-y-1/2 bg-white rounded-2xl shadow-xl p-4 border border-slate-100"
          >
            <div class="flex items-center gap-3">
              <div
                class="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center"
              >
                <svg
                  class="w-5 h-5 text-emerald-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                  />
                </svg>
              </div>
              <div>
                <p class="text-xs font-bold text-slate-900">Impact mesuré</p>
                <p class="text-lg font-extrabold text-emerald-600">+34%</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════
         SECTION IMPACT / TEMOIGNAGE
    ═══════════════════════════════════════════ -->
    <section id="impact" class="bg-[#061B2D] py-24 relative overflow-hidden">
      <!-- Drapeau Sénégal discret en bg -->
      <div
        class="absolute inset-0 flex items-center justify-end pr-16 opacity-5 pointer-events-none"
      >
        <img src="@/assets/images/sn.svg" alt="" class="w-64 h-auto" />
      </div>

      <div
        class="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-16 items-center relative z-10"
      >
        <!-- Gauche : stats + témoignage -->
        <div>
          <div class="w-12 h-0.5 bg-[#061B2D] mb-6"></div>
          <h2
            class="text-3xl xl:text-4xl font-extrabold text-white leading-tight mb-10"
          >
            Des ONG déjà engagées<br />pour un meilleur avenir
          </h2>

          <!-- Stats -->
          <div class="grid grid-cols-3 gap-6 mb-12">
            <div
              class="reveal reveal-scale bg-white/5 border border-white/10 rounded-2xl p-5 text-center"
            >
              <p class="text-3xl font-extrabold text-white" data-counter="120">
                +0
              </p>
              <p class="text-xs text-slate-400 mt-1">ONG partenaires</p>
            </div>
            <div
              class="reveal reveal-scale reveal-delay-1 bg-white/5 border border-white/10 rounded-2xl p-5 text-center"
            >
              <p class="text-3xl font-extrabold text-white" data-counter="500">
                +0
              </p>
              <p class="text-xs text-slate-400 mt-1">Projets soutenus</p>
            </div>
            <div
              class="reveal reveal-scale reveal-delay-2 bg-white/5 border border-white/10 rounded-2xl p-5 text-center"
            >
              <p class="text-3xl font-extrabold text-white" data-counter="250K">
                0+
              </p>
              <p class="text-xs text-slate-400 mt-1">Bénéficiaires</p>
            </div>
          </div>

          <!-- Témoignage -->
          <div class="bg-white/5 border border-white/10 rounded-2xl p-6">
            <svg
              class="w-8 h-8 text-white mb-4 opacity-60"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z"
              />
            </svg>
            <p class="text-white/80 text-sm leading-relaxed mb-5 italic">
              « BarakaGive a transformé la façon dont nous gérons nos projets.
              La plateforme est intuitive, les données sont sécurisées et notre
              équipe a gagné un temps précieux. C'est exactement ce dont les ONG
              africaines ont besoin. »
            </p>
            <div class="flex items-center gap-3">
              <div
                class="w-10 h-10 rounded-full bg-[#061B2D]/30 flex items-center justify-center text-white font-bold text-sm"
              >
                AF
              </div>
              <div>
                <p class="text-white font-semibold text-sm">Aminata Faye</p>
                <p class="text-slate-400 text-xs">
                  Directrice, ONG Espoir Sénégal
                </p>
              </div>
              <div class="ml-auto flex gap-0.5">
                <span v-for="i in 5" :key="i" class="text-white text-sm"
                  >★</span
                >
              </div>
            </div>
          </div>
        </div>

        <!-- Droite : photo + texte -->
        <div
          class="relative overflow-hidden rounded-3xl"
          style="max-height: 540px"
        >
          <img
            src="@/assets/images/femme.png"
            alt="Impact BarakaGive en Afrique"
            class="w-full h-full object-cover object-top shadow-2xl"
          />
          <!-- Overlay gradient bas -->
          <div
            class="absolute bottom-0 left-0 right-0 h-32 rounded-b-3xl bg-gradient-to-t from-[#061B2D] to-transparent"
          ></div>
          <!-- Texte élégant -->
          <p
            class="absolute bottom-6 left-0 right-0 text-center text-white font-semibold text-base tracking-wide"
          >
            Ensemble pour un impact durable
            <span class="text-white">♡</span>
          </p>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════
         CTA — PRÊT À FAIRE GRANDIR VOTRE IMPACT
    ═══════════════════════════════════════════ -->
    <section id="contact" class="bg-white py-24">
      <div class="max-w-2xl mx-auto px-6 text-center">
        <h2
          class="text-3xl xl:text-4xl font-extrabold text-[#061B2D] leading-tight mb-5"
        >
          Prêt à faire grandir<br />votre impact ?
        </h2>

        <p class="text-or text-base leading-relaxed mb-10 max-w-md mx-auto">
          Rejoignez des centaines d'ONG qui nous font déjà confiance et donnez
          plus de force à vos actions humanitaires.
        </p>

        <!-- Boutons -->
        <div
          class="flex flex-col sm:flex-row items-center justify-center gap-4 mb-5"
        >
          <RouterLink
            to="/inscription"
            class="inline-flex items-center gap-2 bg-[#061B2D] text-white font-extrabold px-8 py-3.5 rounded-xl hover:bg-[#0a2540] transition shadow-md text-sm"
          >
            Créer un compte gratuitement
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M17 8l4 4m0 0l-4 4m4-4H3"
              />
            </svg>
          </RouterLink>
          <RouterLink
            to="/connexion"
            class="inline-flex items-center gap-2 text-[#061B2D] font-semibold border border-[#061B2D]/30 px-7 py-3.5 rounded-xl hover:bg-slate-50 transition text-sm"
          >
            Se connecter
          </RouterLink>
        </div>

        <p class="text-or text-xs">
          Essai gratuit 30 jours · Aucune carte bancaire requise
        </p>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════
         FOOTER
    ═══════════════════════════════════════════ -->
    <footer class="bg-[#061B2D] py-14">
      <div class="max-w-7xl mx-auto px-6">
        <div
          class="flex flex-col md:flex-row items-center justify-between gap-8 pb-10 border-b border-white/10"
        >
          <!-- Logo + baseline -->
          <div class="flex items-center gap-3">
            <img
              src="@/assets/images/logologin.png"
              alt="BarakaGive"
              class="w-10 h-10 object-contain"
            />
            <div>
              <span class="text-lg font-bold text-white"
                >Baraka<span class="text-white">Give</span></span
              >
              <p class="text-[10px] text-slate-500 -mt-0.5">
                Ensemble pour un impact durable
              </p>
            </div>
          </div>

          <!-- Liens -->
          <nav class="flex flex-wrap items-center gap-6">
            <a
              href="#hero"
              class="text-sm text-slate-400 hover:text-white transition"
              >Accueil</a
            >
            <a
              href="#fonctionnalites"
              class="text-sm text-slate-400 hover:text-white transition"
              >Fonctionnalités</a
            >
            <a
              href="#avantages"
              class="text-sm text-slate-400 hover:text-white transition"
              >À propos</a
            >
            <a
              href="#contact"
              class="text-sm text-slate-400 hover:text-white transition"
              >Contact</a
            >
          </nav>

          <!-- Socials -->
          <div class="flex items-center gap-4">
            <a
              href="#"
              class="w-9 h-9 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center transition"
            >
              <svg
                class="w-4 h-4 text-slate-300"
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
              class="w-9 h-9 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center transition"
            >
              <svg
                class="w-4 h-4 text-slate-300"
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
              class="w-9 h-9 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center transition"
            >
              <svg
                class="w-4 h-4 text-slate-300"
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

        <div
          class="pt-6 flex flex-col md:flex-row items-center justify-between gap-4"
        >
          <p class="text-xs text-slate-500">
            © 2026 BarakaGive. Tous droits réservés.
          </p>
          <p class="text-xs text-slate-600">
            Fait avec <span class="text-white">♡</span> pour les ONG d'Afrique
            de l'Ouest
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { RouterLink } from "vue-router";

// ── Compteur animé ──────────────────────────────────────────
const animateCounter = (el, target, duration = 1400) => {
  const isK = String(target).includes("K");
  const raw = isK ? parseFloat(target) * 1000 : parseInt(target);
  const start = performance.now();
  const step = (now) => {
    const p = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    const val = Math.round(ease * raw);
    if (isK) {
      el.textContent = val >= 1000 ? (val / 1000).toFixed(0) + "K+" : val + "";
    } else {
      el.textContent = "+" + val;
    }
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
};

// ── Scroll reveal ───────────────────────────────────────────
let revealObserver = null;

const activeLink = ref("accueil");

const setActive = (link) => {
  activeLink.value = link;
};

// Détection automatique de la section visible via IntersectionObserver
let observer = null;

onMounted(() => {
  const sections = [
    { id: "hero", key: "accueil" },
    { id: "fonctionnalites", key: "fonctionnalites" },
    { id: "avantages", key: "avantages" },
    { id: "impact", key: "apropos" },
  ];

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const found = sections.find((s) => s.id === entry.target.id);
          if (found) activeLink.value = found.key;
        }
      });
    },
    { rootMargin: "-40% 0px -55% 0px", threshold: 0 }
  );

  sections.forEach(({ id }) => {
    const el = document.getElementById(id);
    if (el) observer.observe(el);
  });

  // ── Scroll reveal ─────────────────────────────────────────
  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          if (entry.target.hasAttribute("data-counter")) {
            animateCounter(
              entry.target,
              entry.target.getAttribute("data-counter")
            );
          }
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );
  document
    .querySelectorAll(".reveal, .reveal-left, .reveal-right, .reveal-scale")
    .forEach((el) => {
      revealObserver.observe(el);
    });
});

onUnmounted(() => {
  if (observer) observer.disconnect();
  if (revealObserver) revealObserver.disconnect();
});

const avantages = [
  "Interface simple et intuitive",
  "Sécurité et confidentialité des données",
  "Accessible sur ordinateur, tablette et mobile",
  "Support dédié et accompagnement personnalisé",
];

const steps = [
  {
    num: "1",
    titre: "Inscrivez votre ONG",
    texte:
      "Remplissez le formulaire d'inscription avec les informations de votre ONG. Aucune carte bancaire requise pour commencer.",
  },
  {
    num: "2",
    titre: "Configurez votre espace",
    texte:
      "Ajoutez vos projets, votre équipe et vos bénéficiaires. Notre interface guidée vous accompagne pas à pas.",
  },
  {
    num: "3",
    titre: "Pilotez et mesurez",
    texte:
      "Suivez vos indicateurs en temps réel, générez des rapports et partagez votre impact avec vos partenaires.",
  },
];
</script>

<style scoped>
html {
  scroll-behavior: smooth;
}

/* ── Reveal base (fade up) ───────────────────────────────── */
.reveal {
  opacity: 0;
  transform: translateY(28px);
  transition: opacity 0.65s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.65s cubic-bezier(0.22, 1, 0.36, 1);
}
.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.reveal-delay-1 {
  transition-delay: 0.08s;
}
.reveal-delay-2 {
  transition-delay: 0.18s;
}
.reveal-delay-3 {
  transition-delay: 0.28s;
}
.reveal-delay-4 {
  transition-delay: 0.38s;
}

/* Depuis la gauche */
.reveal-left {
  opacity: 0;
  transform: translateX(-36px);
  transition: opacity 0.7s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.7s cubic-bezier(0.22, 1, 0.36, 1);
}
.reveal-left.is-visible {
  opacity: 1;
  transform: translateX(0);
}

/* Depuis la droite */
.reveal-right {
  opacity: 0;
  transform: translateX(36px);
  transition: opacity 0.7s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.7s cubic-bezier(0.22, 1, 0.36, 1);
}
.reveal-right.is-visible {
  opacity: 1;
  transform: translateX(0);
}

/* Scale-up */
.reveal-scale {
  opacity: 0;
  transform: scale(0.93);
  transition: opacity 0.6s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}
.reveal-scale.is-visible {
  opacity: 1;
  transform: scale(1);
}

/* ── Hero (chargement initial) ───────────────────────────── */
@keyframes heroFadeUp {
  from {
    opacity: 0;
    transform: translateY(24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
@keyframes heroFadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
@keyframes badgeFloat {
  0%,
  100% {
    transform: translateY(-50%);
  }
  50% {
    transform: translateY(calc(-50% - 6px));
  }
}

.hero-title {
  animation: heroFadeUp 0.7s 0.05s cubic-bezier(0.22, 1, 0.36, 1) both;
}
.hero-sub {
  animation: heroFadeUp 0.7s 0.2s cubic-bezier(0.22, 1, 0.36, 1) both;
}
.hero-cta {
  animation: heroFadeUp 0.7s 0.35s cubic-bezier(0.22, 1, 0.36, 1) both;
}
.hero-img {
  animation: heroFadeIn 1s 0.15s ease both;
}
.badge-float {
  animation: badgeFloat 3.2s 1s ease-in-out infinite;
}

/* ── Shimmer bouton CTA ──────────────────────────────────── */
@keyframes shimmer {
  0% {
    background-position: -200% center;
  }
  100% {
    background-position: 200% center;
  }
}
.btn-shimmer:hover {
  background-image: linear-gradient(
    110deg,
    #061b2d 30%,
    #1a5080 50%,
    #061b2d 70%
  );
  background-size: 200% auto;
  animation: shimmer 1s linear;
}

/* ── Pulse icône features au hover ──────────────────────── */
@keyframes iconPop {
  0% {
    transform: scale(1);
  }
  40% {
    transform: scale(1.15);
  }
  100% {
    transform: scale(1);
  }
}
.icon-pop:hover {
  animation: iconPop 0.35s ease;
}
</style>








