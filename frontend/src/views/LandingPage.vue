<template>
  <div class="landing-page font-sans text-slate-900 overflow-x-hidden">
    <!-- ═══════════════════════════════════════════
         NAVBAR
    ═══════════════════════════════════════════ -->
    <header
      class="landing-nav fixed inset-x-0 top-0 z-50 w-full border-b border-white/75"
    >
      <div
        class="relative mx-auto flex h-16 w-full min-w-0 items-center gap-4 px-5 sm:px-6 lg:px-8 xl:px-12"
      >
        <!-- Logo -->
        <RouterLink to="/" class="flex shrink-0 items-center gap-3 whitespace-nowrap">
          <img
            src="@/assets/images/logologin.png"
            alt="BarakaGive"
            class="w-10 h-10 object-contain"
          />
          <div>
            <span class="text-lg font-bold text-[#00343D]"
              >Baraka<span class="text-[#00343D]">Give</span></span
            >
            <p class="text-[10px] text-slate-400 leading-none -mt-0.5">
              Ensemble pour un impact durable
            </p>
          </div>
        </RouterLink>

        <!-- Nav links (Desktop uniquement, la version mobile est gérée par la barre iPhone flottante en bas) -->
        <nav
          id="landing-navigation"
          class="hidden xl:flex xl:flex-1 xl:flex-row xl:items-center xl:justify-center xl:gap-8 xl:border-0 xl:bg-transparent xl:p-0 xl:shadow-none"
        >
          <a
            href="#hero"
            @click="setActive('accueil')"
            class="relative whitespace-nowrap pb-1 text-sm font-medium transition"
            :class="
              activeLink === 'accueil'
                ? 'text-[#00343D]'
                : 'text-slate-600 hover:text-[#00343D]'
            "
          >
            Accueil
            <span
              class="absolute bottom-0 left-0 h-0.5 bg-[#00343D] transition-all duration-300"
              :class="activeLink === 'accueil' ? 'w-full' : 'w-0'"
            ></span>
          </a>
          <a
            href="#fonctionnalites"
            @click="setActive('fonctionnalites')"
            class="relative whitespace-nowrap pb-1 text-sm font-medium transition"
            :class="
              activeLink === 'fonctionnalites'
                ? 'text-[#00343D]'
                : 'text-slate-600 hover:text-[#00343D]'
            "
          >
            Fonctionnalités
            <span
              class="absolute bottom-0 left-0 h-0.5 bg-[#00343D] transition-all duration-300"
              :class="activeLink === 'fonctionnalites' ? 'w-full' : 'w-0'"
            ></span>
          </a>
          <a
            href="#avantages"
            @click="setActive('avantages')"
            class="relative whitespace-nowrap pb-1 text-sm font-medium transition"
            :class="
              activeLink === 'avantages'
                ? 'text-[#00343D]'
                : 'text-slate-600 hover:text-[#00343D]'
            "
          >
            Avantages
            <span
              class="absolute bottom-0 left-0 h-0.5 bg-[#00343D] transition-all duration-300"
              :class="activeLink === 'avantages' ? 'w-full' : 'w-0'"
            ></span>
          </a>
          <a
            href="#impact"
            @click="setActive('apropos')"
            class="relative whitespace-nowrap pb-1 text-sm font-medium transition"
            :class="
              activeLink === 'apropos'
                ? 'text-[#00343D]'
                : 'text-slate-600 hover:text-[#00343D]'
            "
          >
            À propos
            <span
              class="absolute bottom-0 left-0 h-0.5 bg-[#00343D] transition-all duration-300"
              :class="activeLink === 'apropos' ? 'w-full' : 'w-0'"
            ></span>
          </a>
          <RouterLink
            to="/contact"
            class="relative whitespace-nowrap pb-1 text-sm font-medium text-slate-600 transition hover:text-[#00343D]"
          >
            Contact
            <span
              class="absolute bottom-0 left-0 w-0 h-0.5 bg-[#00343D] transition-all duration-300 hover:w-full"
            ></span>
          </RouterLink>
        </nav>

        <!-- CTA (Boutons Connexion / Inscription) -->
        <div class="ml-auto flex shrink-0 items-center gap-2 sm:gap-3 xl:ml-0">
          <RouterLink
            to="/connexion"
            class="hidden h-10 w-36 items-center justify-center whitespace-nowrap text-sm font-semibold text-[#00343D] border border-[#00343D]/25 rounded-full hover:border-[#00343D] hover:bg-[#00343D] hover:text-white transition xl:inline-flex"
          >
            Se connecter
          </RouterLink>
          <RouterLink
            to="/inscription"
            class="hidden h-10 w-36 items-center justify-center whitespace-nowrap text-sm font-semibold text-white bg-[#00343D] rounded-full hover:bg-[#002A31] transition shadow-sm xl:inline-flex"
          >
            Créer un compte
          </RouterLink>
        </div>
      </div>
    </header>

    <!-- ═══════════════════════════════════════════
         HERO
    ═══════════════════════════════════════════ -->
    <section id="hero" class="px-0 pt-20">
      <div class="hero-shell mx-auto w-full px-3 pb-3 sm:px-4 sm:pb-4 lg:px-5 lg:pb-5">
        <div class="hero-layout grid grid-cols-1 items-stretch gap-3 lg:h-[460px] lg:grid-cols-2">
          <div class="hero-copy relative isolate flex w-full min-w-0 flex-col justify-center p-5 sm:p-8 lg:p-8 xl:p-10">
            <span class="mb-5 inline-flex items-center gap-2 rounded-full border border-[#00343D]/10 bg-white/80 px-3.5 py-1.5 text-xs font-bold uppercase tracking-[0.14em] text-[#00343D] backdrop-blur">
              BarakaGive &middot; au service des ONG
            </span>
            <h1 class="hero-title text-3xl font-extrabold leading-[1.08] tracking-tight text-[#00343D] sm:text-5xl xl:text-5xl">
              Mieux <br class="sm:hidden" />accompagner.<br class="hidden sm:block" /><br class="sm:hidden" />
              <span class="text-[#00343D]">Mieux agir.</span>
            </h1>
            <p class="hero-sub mt-6 max-w-lg text-base leading-7 text-slate-700 sm:text-lg">
              La plateforme pour organiser vos projets humanitaires, suivre les b&eacute;n&eacute;ficiaires et renforcer la transparence de vos actions.
            </p>
            <div class="hero-cta mt-8 flex w-full max-w-full flex-col gap-3 sm:w-auto sm:flex-row lg:flex-col xl:flex-row">
              <a
                href="#solutions"
                class="inline-flex items-center justify-center gap-2 rounded-full bg-[#00343D] px-6 py-3.5 text-sm font-bold text-white shadow-lg shadow-[#00343D]/20 transition hover:-translate-y-0.5 hover:bg-[#002A31]"
              >
                D&eacute;couvrir la plateforme
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14m-6-6 6 6-6 6" /></svg>
              </a>
              <RouterLink
                to="/contact"
                class="inline-flex items-center justify-center gap-2 rounded-full border border-[#00343D]/30 bg-white/85 px-6 py-3.5 text-sm font-semibold text-[#00343D] transition hover:border-[#00343D] hover:bg-white"
              >
                Demander une d&eacute;mo
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14m-6-6 6 6-6 6" /></svg>
              </RouterLink>
            </div>
          </div>
          <img
            src="@/assets/images/imagelogo.png"
            alt="Une &eacute;quipe d&rsquo;ONG d&eacute;couvre le tableau de bord BarakaGive"
            class="hero-photo h-64 w-full rounded-none object-cover object-center sm:h-80 lg:h-full"
            fetchpriority="high"
          />
        </div>
        <div class="relative z-10 mt-3 mb-4 grid gap-2 rounded-2xl border border-white/75 bg-white/82 p-3 shadow-sm backdrop-blur-xl sm:grid-cols-3 sm:p-2">
          <a href="#solutions" class="flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold text-[#00343D] transition hover:bg-[#00343D]/5 sm:justify-center">
            <svg class="h-6 w-6 shrink-0 text-[#00343D]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M16 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2m16 0v-2a4 4 0 00-3-3.87M14 3.13a4 4 0 010 7.75M14 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
            Suivi des b&eacute;n&eacute;ficiaires
          </a>
          <a href="#solutions" class="flex items-center gap-3 rounded-xl border-[#00343D]/10 px-3 py-3 text-sm font-semibold text-[#00343D] transition hover:bg-[#00343D]/5 sm:justify-center sm:border-x">
            <svg class="h-6 w-6 shrink-0 text-[#00343D]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M3 7.5A1.5 1.5 0 014.5 6H10l2 2h7.5A1.5 1.5 0 0121 9.5v9a1.5 1.5 0 01-1.5 1.5h-15A1.5 1.5 0 013 18.5v-11z" /></svg>
            Gestion des projets
          </a>
          <a href="#solutions" class="flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold text-[#00343D] transition hover:bg-[#00343D]/5 sm:justify-center">
            <svg class="h-6 w-6 shrink-0 text-[#00343D]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M12 3l8 3v5c0 5-3.4 8.5-8 10-4.6-1.5-8-5-8-10V6l8-3zm-3 9 2 2 4-4" /></svg>
            Transparence des actions
          </a>
        </div>
      </div>
    </section>
    <section id="solutions" class="bg-white px-4 py-12 sm:px-6 lg:py-16">
      <div id="fonctionnalites" class="mx-auto max-w-7xl">
        <div class="mx-auto mb-10 max-w-2xl text-center">
          <span class="rounded-full bg-[#00343D]/10 px-3 py-1 text-[11px] font-bold uppercase tracking-wide text-[#00343D]">Nos solutions</span>
          <h2 class="mt-4 text-3xl font-extrabold text-[#00343D] sm:text-4xl">Les outils pour organiser et suivre vos actions</h2>
          <p class="mt-3 text-slate-600">BarakaGive rassemble les informations utiles au suivi de vos projets et de vos actions.</p>
        </div>
        <div class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          <article class="editorial-card group overflow-hidden rounded-3xl border border-slate-100 bg-white p-3 transition hover:-translate-y-1">
            <img src="@/assets/images/beneficiaire.png" alt="Des bénéficiaires réunis autour d’un point d’eau" class="h-48 w-full rounded-2xl object-cover object-center" loading="lazy" />
            <div class="px-3 pb-3 pt-5">
              <span class="rounded-full bg-[#00343D]/10 px-3 py-1 text-[11px] font-bold uppercase tracking-wide text-[#00343D]">Bénéficiaires</span>
              <h3 class="mt-4 text-xl font-bold leading-snug text-[#00343D]">Suivre les personnes accompagnées</h3>
              <p class="mt-2 text-sm leading-6 text-slate-600">Consignez les besoins et les actions de suivi pour mieux organiser l’accompagnement.</p>
            </div>
          </article>
          <article class="editorial-card group overflow-hidden rounded-3xl border border-slate-100 bg-white p-3 transition hover:-translate-y-1">
            <img src="@/assets/images/imagelogo.png" alt="Équipe de projet consultant un tableau de suivi" class="h-48 w-full rounded-2xl object-cover object-center" loading="lazy" />
            <div class="px-3 pb-3 pt-5">
              <span class="rounded-full bg-[#00343D]/10 px-3 py-1 text-[11px] font-bold uppercase tracking-wide text-[#00343D]">Projets et campagnes</span>
              <h3 class="mt-4 text-xl font-bold leading-snug text-[#00343D]">Organiser les activités de terrain</h3>
              <p class="mt-2 text-sm leading-6 text-slate-600">Structurez les projets, les campagnes et les informations utiles à leur suivi.</p>
            </div>
          </article>
          <article class="editorial-card group overflow-hidden rounded-3xl border border-slate-100 bg-white p-3 transition hover:-translate-y-1">
            <img src="@/assets/images/ordi.png" alt="Tableau de bord de suivi financier et de rapports" class="h-48 w-full rounded-2xl object-cover object-center" loading="lazy" />
            <div class="px-3 pb-3 pt-5">
              <span class="rounded-full bg-[#00343D]/10 px-3 py-1 text-[11px] font-bold uppercase tracking-wide text-[#00343D]">Financements et rapports</span>
              <h3 class="mt-4 text-xl font-bold leading-snug text-[#00343D]">Suivre les ressources et rendre compte</h3>
              <p class="mt-2 text-sm leading-6 text-slate-600">Centralisez les informations financières et préparez le suivi destiné à vos équipes et partenaires.</p>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section id="fonctionnement" class="bg-white py-20">
      <div class="mx-auto max-w-4xl px-6 text-center">
        <div class="reveal mx-auto mb-6 h-0.5 w-12 bg-[#00343D]"></div>
        <h2 class="reveal mb-4 text-3xl font-extrabold text-[#00343D] xl:text-4xl">Comment ça fonctionne ?</h2>
        <p class="reveal mx-auto mb-12 max-w-lg text-slate-500">Une organisation claire, du suivi des besoins à l’analyse des résultats.</p>
        <div class="grid gap-6 md:grid-cols-3">
          <article v-for="(step, i) in steps" :key="step.num" :class="`reveal reveal-delay-${i + 1}`" class="rounded-2xl border border-slate-100 bg-white p-8 shadow-sm transition-transform duration-300 hover:-translate-y-1">
            <div class="mx-auto mb-5 flex h-10 w-10 items-center justify-center rounded-xl bg-[#00343D] text-lg font-extrabold text-white">{{ step.num }}</div>
            <h3 class="mb-3 font-bold text-[#00343D]">{{ step.titre }}</h3>
            <p class="text-sm leading-relaxed text-slate-500">{{ step.texte }}</p>
          </article>
        </div>
      </div>
    </section>

    <section id="avantages" class="bg-slate-50 py-20">
      <div class="mx-auto grid max-w-7xl items-center gap-12 px-6 lg:grid-cols-2 lg:gap-16">
        <div class="reveal-left">
          <div class="mb-6 h-0.5 w-12 bg-[#00343D]"></div>
          <h2 class="mb-5 text-3xl font-extrabold leading-tight text-[#00343D] xl:text-4xl">Les avantages de BarakaGive</h2>
          <p class="mb-8 text-base leading-relaxed text-slate-600">Retrouvez les informations de vos actions dans un même espace pour mieux organiser le travail de vos équipes et gagner du temps au quotidien.</p>
          <ul class="mb-8 space-y-4">
            <li v-for="item in avantages" :key="item" class="flex items-start gap-3">
              <span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[#00343D]/15">
                <svg class="h-3 w-3 text-[#00343D]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" /></svg>
              </span>
              <span class="text-sm font-medium text-slate-700">{{ item }}</span>
            </li>
          </ul>
          <RouterLink to="/contact" class="inline-flex items-center gap-2 rounded-xl bg-[#00343D] px-6 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-[#002A31]">Parler à l’équipe</RouterLink>
        </div>
        <div class="reveal-right">
          <img src="@/assets/images/ordi.png" alt="Tableau de bord BarakaGive pour suivre les projets et les ressources" class="w-full rounded-2xl" loading="lazy" />
        </div>
      </div>
    </section>

    <section id="intelligence" class="bg-white py-20">
      <div class="mx-auto grid max-w-7xl items-center gap-10 px-6 lg:grid-cols-2 lg:gap-16">
        <div class="reveal-left order-2 lg:order-1">
          <span class="rounded-full bg-[#00343D]/10 px-3 py-1 text-[11px] font-bold uppercase tracking-wide text-[#00343D]">Assistant IA</span>
          <h2 class="mb-5 mt-4 text-3xl font-extrabold leading-tight text-[#00343D] xl:text-4xl">L’intelligence artificielle au service des ONG</h2>
          <p class="mb-6 text-base leading-relaxed text-slate-600">L’assistant peut s’appuyer sur les informations disponibles dans BarakaGive pour aider à analyser une situation, prioriser les besoins et préparer des rapports.</p>
          <p class="mb-8 text-sm leading-relaxed text-slate-500">Les réponses dépendent des informations accessibles à l’assistant et restent à vérifier par votre équipe.</p>
          <RouterLink to="/gerant/assistant" class="inline-flex items-center gap-2 rounded-xl bg-[#00343D] px-6 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-[#002A31]">Découvrir l’assistant IA</RouterLink>
        </div>
        <div class="reveal-right order-1 lg:order-2">
          <img src="@/assets/images/ai.png" alt="Illustration de l’assistant IA BarakaGive" class="w-full rounded-2xl" loading="lazy" />
        </div>
      </div>
    </section>

    <section id="impact" class="relative overflow-hidden bg-[#00343D] py-20">
      <div class="pointer-events-none absolute inset-0 flex items-center justify-end pr-16 opacity-5"><img src="@/assets/images/sn.svg" alt="" class="h-auto w-64" /></div>
      <div class="relative z-10 mx-auto max-w-7xl px-6">
        <div class="mx-auto mb-10 max-w-3xl text-center">
          <div class="mx-auto mb-6 h-0.5 w-12 bg-white/70"></div>
          <h2 class="mb-4 text-3xl font-extrabold leading-tight text-white xl:text-4xl">Nos engagements et notre impact</h2>
          <p class="text-base leading-7 text-white/75">BarakaGive aide les organisations à suivre leurs actions avec attention, à partager des informations utiles et à éclairer leurs décisions.</p>
        </div>
        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <article class="rounded-2xl border border-white/15 bg-white/5 p-6 text-white"><h3 class="mb-2 font-bold">Protection</h3><p class="text-sm leading-6 text-white/75">Organisez les informations de suivi dans le cadre défini par votre organisation.</p></article>
          <article class="rounded-2xl border border-white/15 bg-white/5 p-6 text-white"><h3 class="mb-2 font-bold">Accompagnement</h3><p class="text-sm leading-6 text-white/75">Suivez les besoins et les actions auprès des personnes accompagnées.</p></article>
          <article class="rounded-2xl border border-white/15 bg-white/5 p-6 text-white"><h3 class="mb-2 font-bold">Transparence</h3><p class="text-sm leading-6 text-white/75">Rassemblez les éléments de suivi et facilitez la préparation des rapports.</p></article>
          <article class="rounded-2xl border border-white/15 bg-white/5 p-6 text-white"><h3 class="mb-2 font-bold">Aide à la décision</h3><p class="text-sm leading-6 text-white/75">Consultez les informations disponibles pour mieux orienter les actions.</p></article>
        </div>
      </div>
    </section>

    <section id="faq" class="bg-white py-20">
      <div class="mx-auto max-w-4xl px-6">
        <div class="mx-auto mb-10 max-w-2xl text-center">
          <span class="rounded-full bg-[#00343D]/10 px-3 py-1 text-[11px] font-bold uppercase tracking-wide text-[#00343D]">FAQ</span>
          <h2 class="mb-4 mt-4 text-3xl font-extrabold text-[#00343D] xl:text-4xl">Questions fréquentes</h2>
        </div>
        <div class="space-y-3">
          <details class="rounded-2xl border border-slate-100 bg-white p-5"><summary class="cursor-pointer font-semibold text-[#00343D]">À quoi sert BarakaGive ?</summary><p class="mt-3 text-sm leading-6 text-slate-600">BarakaGive aide les organisations à organiser leurs projets, campagnes, bénéficiaires et ressources, puis à préparer leur suivi.</p></details>
          <details class="rounded-2xl border border-slate-100 bg-white p-5"><summary class="cursor-pointer font-semibold text-[#00343D]">À qui s’adresse la plateforme ?</summary><p class="mt-3 text-sm leading-6 text-slate-600">Aux ONG, associations, équipes de projet et partenaires institutionnels qui collaborent au suivi des actions.</p></details>
          <details class="rounded-2xl border border-slate-100 bg-white p-5"><summary class="cursor-pointer font-semibold text-[#00343D]">Comment l’assistant IA peut-il aider ?</summary><p class="mt-3 text-sm leading-6 text-slate-600">Il peut analyser les informations disponibles, aider à prioriser les besoins et contribuer à la préparation de rapports. Votre équipe vérifie les réponses.</p></details>
          <details class="rounded-2xl border border-slate-100 bg-white p-5"><summary class="cursor-pointer font-semibold text-[#00343D]">Comment demander une démonstration ?</summary><p class="mt-3 text-sm leading-6 text-slate-600">Écrivez à l’équipe via la page Contact pour présenter votre organisation et demander une démonstration.</p></details>
        </div>
      </div>
    </section>

    <section id="contact" class="bg-slate-50 py-20">
      <div class="mx-auto max-w-2xl px-6 text-center">
        <h2 class="mb-5 text-3xl font-extrabold leading-tight text-[#00343D] xl:text-4xl">Parlons de vos projets</h2>
        <p class="mx-auto mb-8 max-w-lg text-base leading-relaxed text-slate-600">Contactez l’équipe BarakaGive pour demander une démonstration ou poser vos questions.</p>
        <div class="flex flex-col items-center justify-center gap-4 sm:flex-row">
          <RouterLink to="/contact" class="inline-flex items-center gap-2 rounded-xl bg-[#00343D] px-8 py-3.5 text-sm font-extrabold text-white shadow-md transition hover:bg-[#002A31]">Demander une démonstration</RouterLink>
          <a href="mailto:contact@barakagive.org" class="inline-flex items-center gap-2 rounded-xl border border-[#00343D]/30 px-7 py-3.5 text-sm font-semibold text-[#00343D] transition hover:bg-white">Contacter l’équipe</a>
        </div>
      </div>
    </section>
<footer class="landing-footer relative isolate py-14 pb-28 lg:pb-14">
      <div class="mx-auto max-w-7xl px-6">
        <div class="flex flex-col items-center justify-between gap-8 border-b border-white/10 pb-10 md:flex-row">
          <div class="flex items-center gap-3">
            <img src="@/assets/images/logologin.png" alt="BarakaGive" class="h-10 w-10 object-contain" />
            <div>
              <span class="text-lg font-bold text-white">BarakaGive</span>
              <p class="-mt-0.5 text-[10px] text-slate-500">Ensemble pour un impact durable</p>
            </div>
          </div>
          <nav aria-label="Navigation de pied de page" class="flex flex-wrap items-center justify-center gap-x-5 gap-y-3">
            <a href="#solutions" class="text-sm text-slate-400 transition hover:text-white">Nos solutions</a>
            <a href="#fonctionnement" class="text-sm text-slate-400 transition hover:text-white">Fonctionnement</a>
            <a href="#avantages" class="text-sm text-slate-400 transition hover:text-white">Avantages</a>
            <a href="#intelligence" class="text-sm text-slate-400 transition hover:text-white">Assistant IA</a>
            <a href="#public" class="text-sm text-slate-400 transition hover:text-white">Publics</a>
            <a href="#faq" class="text-sm text-slate-400 transition hover:text-white">FAQ</a>
          </nav>
          <address class="flex flex-col items-center gap-2 text-center text-sm not-italic text-slate-300 md:items-end md:text-right">
            <a href="mailto:contact@barakagive.org" class="transition hover:text-white">contact@barakagive.org</a>
            <a href="tel:+221770000000" class="transition hover:text-white">+221 77 000 00 00</a>
          </address>
        </div>
        <div class="flex flex-col items-center justify-between gap-3 pt-6 text-center md:flex-row md:text-left">
          <p class="text-xs text-slate-500">&copy; 2026 BarakaGive. Tous droits réservés.</p>
          <a href="#contact" class="text-xs text-slate-400 transition hover:text-white">Contacter l’équipe BarakaGive</a>
        </div>
      </div>
    </footer>

    <!-- Menu moderne iPhone flottant en bas pour la Landing Page -->
    <LandingIPhoneBottomBar
      ref="landingBottomBarRef"
      :active-section="currentSectionId"
      @navigate="onMobileNavigate"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { RouterLink } from "vue-router";
import LandingIPhoneBottomBar from "@/components/layout/LandingIPhoneBottomBar.vue";

const landingBottomBarRef = ref(null);

const toggleMobileSheet = () => {
  if (landingBottomBarRef.value?.toggleSheet) {
    landingBottomBarRef.value.toggleSheet();
  } else {
    menuOpen.value = !menuOpen.value;
  }
};

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
const menuOpen = ref(false);

const setActive = (link) => {
  activeLink.value = link;
};

const currentSectionId = computed(() => {
  if (activeLink.value === "accueil") return "hero";
  if (activeLink.value === "fonctionnalites" || activeLink.value === "solutions") return "solutions";
  if (activeLink.value === "avantages") return "avantages";
  if (activeLink.value === "apropos" || activeLink.value === "impact") return "impact";
  return activeLink.value;
});

const onMobileNavigate = (sectionId) => {
  if (sectionId === "hero") activeLink.value = "accueil";
  else if (sectionId === "solutions" || sectionId === "fonctionnalites") activeLink.value = "fonctionnalites";
  else if (sectionId === "avantages") activeLink.value = "avantages";
  else if (sectionId === "impact") activeLink.value = "apropos";
};

// Détection automatique de la section visible via IntersectionObserver
let observer = null;

onMounted(() => {
  const sections = [
    { id: "hero", key: "accueil" },
    { id: "solutions", key: "fonctionnalites" },
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
  "Projets, campagnes et b\u00e9n\u00e9ficiaires r\u00e9unis dans un m\u00eame espace.",
  "Informations plus faciles \u00e0 retrouver et \u00e0 partager avec l'\u00e9quipe.",
  "Suivi des besoins et des r\u00e9sultats pour gagner du temps au quotidien.",
];

const steps = [
  {
    num: "1",
    titre: "Enregistrez votre organisation",
    texte: "Renseignez les informations de votre ONG pour ouvrir son espace BarakaGive.",
  },
  {
    num: "2",
    titre: "Organisez vos actions",
    texte: "Ajoutez vos projets, vos campagnes, vos \u00e9quipes et les besoins \u00e0 suivre.",
  },
  {
    num: "3",
    titre: "Suivez les r\u00e9sultats",
    texte: "Consultez les informations disponibles et pr\u00e9parez le suivi de vos actions et ressources.",
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
.landing-nav {
  background: rgb(255 255 255 / 84%);
  -webkit-backdrop-filter: blur(18px) saturate(125%);
  backdrop-filter: blur(18px) saturate(125%);
  box-shadow: 0 8px 28px rgb(0 52 61 / 7%), inset 0 1px 0 rgb(255 255 255 / 88%);
}
.hero-copy {
  width: 100%;
  max-width: none;
}
.hero-copy::before {
  position: absolute;
  z-index: -1;
  inset: 0;
  border: 1px solid rgb(255 255 255 / 72%);
  border-radius: 0;
  background: linear-gradient(145deg, rgb(255 255 255 / 76%), rgb(255 255 255 / 66%));
  box-shadow: 0 12px 32px rgb(0 52 61 / 10%), inset 0 1px 0 rgb(255 255 255 / 84%);
  backdrop-filter: blur(10px) saturate(112%);
  -webkit-backdrop-filter: blur(10px) saturate(112%);
  content: "";
}
.landing-page .landing-footer {
  border-top: 1px solid rgb(255 255 255 / 24%);
  background: linear-gradient(125deg, rgb(0 52 61 / 96%), rgb(0 52 61 / 88%));
  -webkit-backdrop-filter: blur(18px) saturate(120%);
  backdrop-filter: blur(18px) saturate(120%);
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 12%);
}
.landing-footer > div {
  position: relative;
  z-index: 1;
}
.editorial-card,
.solution-card {
  box-shadow: 0 12px 36px rgb(0 52 61 / 7%);
}
.editorial-card-featured {
  box-shadow: 0 18px 42px rgb(0 52 61 / 18%);
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
    #00343d 30%,
    #002A31 50%,
    #00343d 70%
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

.landing-page :is(a, button):focus-visible {
  outline: 3px solid rgb(0 52 61 / 52%);
  outline-offset: 3px;
}

.landing-page :is(a, button):active {
  transform: translateY(1px) scale(0.99);
}

.landing-page #solutions,
.landing-page #fonctionnement,
.landing-page #faq,
.landing-page #contact {
  background-image:
    radial-gradient(ellipse at 12% 15%, rgb(0 52 61 / 3%), transparent 48%),
    radial-gradient(ellipse at 88% 85%, rgb(0 52 61 / 2.5%), transparent 45%);
}

@media (max-width: 639px) {
  .landing-page,
  .landing-page header,
  .landing-page section {
    max-width: 100vw;
    width: 100%;
  }
  .landing-page header > div {
    min-width: 0;
    width: 100%;
  }
  .hero-shell {
    max-width: 100%;
    width: 100%;
  }
  .hero-cta {
    max-width: min(calc(100vw - 5rem), 19rem);
    width: min(calc(100vw - 5rem), 19rem);
  }
  .hero-shell h1,
  .hero-shell p,
  .hero-cta > a {
    max-width: 100%;
    overflow-wrap: anywhere;
  }
  .hero-copy::before {
    inset: 0;
    border-radius: 0;
    background: rgb(255 255 255 / 84%);
    backdrop-filter: blur(10px) saturate(110%);
    -webkit-backdrop-filter: blur(10px) saturate(110%);
  }
}

@media (prefers-reduced-motion: reduce) {
  .landing-page *,
  .landing-page *::before,
  .landing-page *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
  }
}

/* Verre discret pour les panneaux des sections après le Hero. */
.landing-page #solutions .editorial-card,
.landing-page #fonctionnement article,
.landing-page #faq details {
  background: linear-gradient(
    145deg,
    rgb(255 255 255 / 88%),
    rgb(255 255 255 / 72%)
  );
  border-color: rgb(255 255 255 / 92%);
  backdrop-filter: blur(14px) saturate(112%);
  -webkit-backdrop-filter: blur(14px) saturate(112%);
  box-shadow:
    0 12px 30px rgb(0 52 61 / 6%),
    inset 0 1px 0 rgb(255 255 255 / 85%);
}

.landing-page #avantages ul,
.landing-page #intelligence .reveal-left,
.landing-page #contact .max-w-2xl {
  border: 1px solid rgb(255 255 255 / 86%);
  border-radius: 1.25rem;
  background: rgb(255 255 255 / 62%);
  backdrop-filter: blur(16px) saturate(110%);
  -webkit-backdrop-filter: blur(16px) saturate(110%);
  box-shadow:
    0 14px 32px rgb(0 52 61 / 5%),
    inset 0 1px 0 rgb(255 255 255 / 82%);
}

.landing-page #avantages ul {
  padding: 1.25rem;
}

.landing-page #intelligence .reveal-left {
  padding: clamp(1.25rem, 3vw, 2rem);
}

.landing-page #contact .max-w-2xl {
  padding: clamp(1.5rem, 4vw, 2.5rem);
}

.landing-page #impact article {
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: inset 0 1px 0 rgb(255 255 255 / 8%);
}

.landing-page #solutions .editorial-card,
.landing-page #fonctionnement article,
.landing-page #faq details,
.landing-page #impact article {
  transition:
    transform 180ms ease,
    border-color 180ms ease,
    box-shadow 180ms ease,
    background-color 180ms ease;
}

.landing-page #solutions .editorial-card:hover,
.landing-page #fonctionnement article:hover,
.landing-page #faq details[open] {
  border-color: rgb(0 52 61 / 14%);
  box-shadow:
    0 16px 34px rgb(0 52 61 / 9%),
    inset 0 1px 0 rgb(255 255 255 / 92%);
}

@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .landing-nav {
    background: rgb(255 255 255 / 97%);
  }

  .landing-page .landing-footer {
    background: #00343D;
  }

  .hero-copy::before,
  .landing-page #solutions .editorial-card,
  .landing-page #fonctionnement article,
  .landing-page #faq details,
  .landing-page #avantages ul,
  .landing-page #intelligence .reveal-left,
  .landing-page #contact .max-w-2xl {
    background: rgb(255 255 255 / 96%);
  }

  .landing-page #impact article {
    background: rgb(255 255 255 / 12%);
  }
}

@media (prefers-reduced-transparency: reduce) {
  .landing-nav,
  .hero-copy::before,
  .landing-page #solutions .editorial-card,
  .landing-page #fonctionnement article,
  .landing-page #faq details,
  .landing-page #avantages ul,
  .landing-page #intelligence .reveal-left,
  .landing-page #contact .max-w-2xl {
    background: rgb(255 255 255 / 96%);
    -webkit-backdrop-filter: none;
    backdrop-filter: none;
  }

  .landing-page #impact article {
    -webkit-backdrop-filter: none;
    backdrop-filter: none;
  }

  .landing-page .landing-footer {
    background: #00343D;
    -webkit-backdrop-filter: none;
    backdrop-filter: none;
  }
}
</style>








