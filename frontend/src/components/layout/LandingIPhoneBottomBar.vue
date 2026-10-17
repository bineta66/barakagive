<template>
  <div class="lg:hidden">
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- BARRE FLOTTANTE STYLE IPHONE POUR LA LANDING PAGE                   -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <nav
      class="fixed bottom-2.5 inset-x-3 sm:inset-x-8 z-40 pointer-events-none flex justify-center pb-[env(safe-area-inset-bottom,0px)]"
      aria-label="Navigation mobile vitrine"
    >
      <div
        class="pointer-events-auto w-full max-w-md bg-[#00343D]/92 backdrop-blur-2xl border border-white/[0.18] rounded-[26px] p-1.5 shadow-[0_12px_40px_rgba(0,25,30,0.5),0_1px_0_rgba(255,255,255,0.14)_inset] flex items-center justify-around gap-1 relative select-none"
      >
        <!-- 1. Accueil -->
        <button
          type="button"
          @click="scrollTo('hero')"
          :class="[
            'relative flex flex-col items-center justify-center flex-1 min-w-0 py-1.5 px-1 rounded-2xl transition-all duration-200 active:scale-90',
            activeSection === 'hero'
              ? 'bg-white/[0.18] shadow-sm ring-1 ring-white/20 text-white'
              : 'text-white/65 hover:text-white/95 hover:bg-white/[0.06]'
          ]"
        >
          <Home
            :size="20"
            :class="[
              'transition-transform duration-200 shrink-0',
              activeSection === 'hero' ? 'scale-110 text-white' : 'text-white/75'
            ]"
            :stroke-width="activeSection === 'hero' ? 2.4 : 1.9"
          />
          <span
            class="text-[10px] tracking-tight truncate max-w-full mt-0.5"
            :class="activeSection === 'hero' ? 'font-semibold text-white' : 'font-medium text-white/70'"
          >
            Accueil
          </span>
          <span
            v-if="activeSection === 'hero'"
            class="w-1 h-1 rounded-full bg-[#D20C4F] shadow-[0_0_8px_#D20C4F] mt-0.5 shrink-0"
          />
        </button>

        <!-- 2. Solutions -->
        <button
          type="button"
          @click="scrollTo('solutions')"
          :class="[
            'relative flex flex-col items-center justify-center flex-1 min-w-0 py-1.5 px-1 rounded-2xl transition-all duration-200 active:scale-90',
            activeSection === 'solutions' || activeSection === 'fonctionnalites'
              ? 'bg-white/[0.18] shadow-sm ring-1 ring-white/20 text-white'
              : 'text-white/65 hover:text-white/95 hover:bg-white/[0.06]'
          ]"
        >
          <Layers
            :size="20"
            :class="[
              'transition-transform duration-200 shrink-0',
              activeSection === 'solutions' || activeSection === 'fonctionnalites' ? 'scale-110 text-white' : 'text-white/75'
            ]"
            :stroke-width="activeSection === 'solutions' || activeSection === 'fonctionnalites' ? 2.4 : 1.9"
          />
          <span
            class="text-[10px] tracking-tight truncate max-w-full mt-0.5"
            :class="activeSection === 'solutions' || activeSection === 'fonctionnalites' ? 'font-semibold text-white' : 'font-medium text-white/70'"
          >
            Solutions
          </span>
          <span
            v-if="activeSection === 'solutions' || activeSection === 'fonctionnalites'"
            class="w-1 h-1 rounded-full bg-[#D20C4F] shadow-[0_0_8px_#D20C4F] mt-0.5 shrink-0"
          />
        </button>

        <!-- 3. Avantages -->
        <button
          type="button"
          @click="scrollTo('avantages')"
          :class="[
            'relative flex flex-col items-center justify-center flex-1 min-w-0 py-1.5 px-1 rounded-2xl transition-all duration-200 active:scale-90',
            activeSection === 'avantages'
              ? 'bg-white/[0.18] shadow-sm ring-1 ring-white/20 text-white'
              : 'text-white/65 hover:text-white/95 hover:bg-white/[0.06]'
          ]"
        >
          <ShieldCheck
            :size="20"
            :class="[
              'transition-transform duration-200 shrink-0',
              activeSection === 'avantages' ? 'scale-110 text-white' : 'text-white/75'
            ]"
            :stroke-width="activeSection === 'avantages' ? 2.4 : 1.9"
          />
          <span
            class="text-[10px] tracking-tight truncate max-w-full mt-0.5"
            :class="activeSection === 'avantages' ? 'font-semibold text-white' : 'font-medium text-white/70'"
          >
            Avantages
          </span>
          <span
            v-if="activeSection === 'avantages'"
            class="w-1 h-1 rounded-full bg-[#D20C4F] shadow-[0_0_8px_#D20C4F] mt-0.5 shrink-0"
          />
        </button>

        <!-- 4. Contact -->
        <RouterLink
          to="/contact"
          :class="[
            'relative flex flex-col items-center justify-center flex-1 min-w-0 py-1.5 px-1 rounded-2xl transition-all duration-200 active:scale-90',
            $route.path === '/contact'
              ? 'bg-white/[0.18] shadow-sm ring-1 ring-white/20 text-white'
              : 'text-white/65 hover:text-white/95 hover:bg-white/[0.06]'
          ]"
        >
          <MessageSquare
            :size="20"
            :class="[
              'transition-transform duration-200 shrink-0',
              $route.path === '/contact' ? 'scale-110 text-white' : 'text-white/75'
            ]"
            :stroke-width="$route.path === '/contact' ? 2.4 : 1.9"
          />
          <span
            class="text-[10px] tracking-tight truncate max-w-full mt-0.5"
            :class="$route.path === '/contact' ? 'font-semibold text-white' : 'font-medium text-white/70'"
          >
            Contact
          </span>
          <span
            v-if="$route.path === '/contact'"
            class="w-1 h-1 rounded-full bg-[#D20C4F] shadow-[0_0_8px_#D20C4F] mt-0.5 shrink-0"
          />
        </RouterLink>

        <!-- 5. Menu / Accès (Feuille iOS complète) -->
        <button
          type="button"
          @click="sheetOpen = !sheetOpen"
          :class="[
            'relative flex flex-col items-center justify-center flex-1 min-w-0 py-1.5 px-1 rounded-2xl transition-all duration-200 active:scale-90',
            sheetOpen
              ? 'bg-white/[0.18] shadow-sm ring-1 ring-white/20 text-white'
              : 'text-white/65 hover:text-white/95 hover:bg-white/[0.06]'
          ]"
          :aria-expanded="sheetOpen"
          aria-label="Ouvrir le menu et les accès ONG"
        >
          <LayoutGrid
            :size="20"
            :class="[
              'transition-transform duration-200 shrink-0',
              sheetOpen ? 'scale-110 text-white' : 'text-white/75'
            ]"
            :stroke-width="sheetOpen ? 2.4 : 1.9"
          />
          <span
            class="text-[10px] tracking-tight truncate max-w-full mt-0.5"
            :class="sheetOpen ? 'font-semibold text-white' : 'font-medium text-white/70'"
          >
            Menu
          </span>
          <span
            v-if="sheetOpen"
            class="w-1 h-1 rounded-full bg-[#D20C4F] shadow-[0_0_8px_#D20C4F] mt-0.5 shrink-0"
          />
        </button>
      </div>
    </nav>

    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <!-- FEUILLE MODALE iOS POUR LA LANDING PAGE                             -->
    <!-- ═══════════════════════════════════════════════════════════════════ -->
    <transition name="fade">
      <div
        v-if="sheetOpen"
        class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
        @click="sheetOpen = false"
      />
    </transition>

    <transition name="slide-up">
      <div
        v-if="sheetOpen"
        class="fixed bottom-0 inset-x-0 z-50 max-h-[88vh] overflow-y-auto bg-[#00343D]/95 backdrop-blur-3xl border-t border-white/20 rounded-t-[32px] text-white p-5 pb-10 shadow-[0_-12px_45px_rgba(0,0,0,0.55)] flex flex-col"
        role="dialog"
        aria-modal="true"
        aria-label="Menu principal et accès BarakaGive"
      >
        <!-- Poignée iOS -->
        <button
          type="button"
          class="w-12 h-1.5 bg-white/30 rounded-full mx-auto mb-4 hover:bg-white/50 active:scale-95 transition"
          @click="sheetOpen = false"
          aria-label="Fermer le menu"
        />

        <!-- En-tête : Marque BarakaGive -->
        <div class="flex items-center justify-between pb-4 border-b border-white/[0.12]">
          <div class="flex items-center gap-3">
            <img
              src="@/assets/images/logologin.png"
              alt="Logo BarakaGive"
              class="w-10 h-10 object-contain drop-shadow"
            />
            <div>
              <span class="text-base font-bold text-white tracking-wide">
                Baraka<span class="text-rose-baraka">Give</span>
              </span>
              <p class="text-[10px] text-white/70 leading-none">
                Ensemble pour un impact durable
              </p>
            </div>
          </div>

          <button
            type="button"
            @click="sheetOpen = false"
            class="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white/80 hover:text-white transition active:scale-90"
            aria-label="Fermer"
          >
            <X :size="16" />
          </button>
        </div>

        <!-- Section 1 : Boutons d'accès VIP (Connexion & Inscription) -->
        <div class="mt-4 grid grid-cols-2 gap-2.5">
          <RouterLink
            to="/connexion"
            @click="sheetOpen = false"
            class="hidden items-center justify-center gap-2 py-3 px-3 rounded-2xl bg-white/[0.12] hover:bg-white/[0.18] border border-white/20 text-xs font-bold text-white transition active:scale-95 text-center shadow-sm"
          >
            <LogIn :size="16" /> Se connecter
          </RouterLink>

          <RouterLink
            to="/inscription"
            @click="sheetOpen = false"
            class="flex items-center justify-center gap-2 py-3 px-3 rounded-2xl bg-gradient-to-r from-rose-baraka to-[#00343D] hover:opacity-95 text-xs font-bold text-white shadow-md transition active:scale-95 text-center ring-1 ring-white/20"
          >
            <UserPlus :size="16" /> Créer un compte
          </RouterLink>
        </div>

        <!-- Section 2 : Navigation dans les sections du site -->
        <div class="mt-5">
          <p class="text-[11px] font-semibold uppercase tracking-wider text-white/50 mb-3 px-1">
            Explorer la plateforme
          </p>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <!-- Solutions -->
            <button
              type="button"
              @click="handleScrollTo('solutions')"
              class="flex items-center gap-3 p-3 rounded-2xl bg-white/[0.07] hover:bg-white/[0.12] border border-white/10 transition active:scale-[0.98] text-left"
            >
              <div class="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center shrink-0 text-white">
                <Layers :size="20" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-xs font-semibold text-white truncate">Nos solutions</p>
                <p class="text-[11px] text-white/60 truncate mt-0.5">Bénéficiaires, projets et finances</p>
              </div>
              <ChevronRight :size="16" class="text-white/40 shrink-0" />
            </button>

            <!-- Fonctionnement -->
            <button
              type="button"
              @click="handleScrollTo('fonctionnement')"
              class="flex items-center gap-3 p-3 rounded-2xl bg-white/[0.07] hover:bg-white/[0.12] border border-white/10 transition active:scale-[0.98] text-left"
            >
              <div class="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center shrink-0 text-white">
                <Workflow :size="20" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-xs font-semibold text-white truncate">Comment ça marche</p>
                <p class="text-[11px] text-white/60 truncate mt-0.5">Organisation en 3 étapes clés</p>
              </div>
              <ChevronRight :size="16" class="text-white/40 shrink-0" />
            </button>

            <!-- Avantages -->
            <button
              type="button"
              @click="handleScrollTo('avantages')"
              class="flex items-center gap-3 p-3 rounded-2xl bg-white/[0.07] hover:bg-white/[0.12] border border-white/10 transition active:scale-[0.98] text-left"
            >
              <div class="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center shrink-0 text-white">
                <ShieldCheck :size="20" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-xs font-semibold text-white truncate">Avantages ONG</p>
                <p class="text-[11px] text-white/60 truncate mt-0.5">Gain de temps et traçabilité</p>
              </div>
              <ChevronRight :size="16" class="text-white/40 shrink-0" />
            </button>

            <!-- Assistant IA -->
            <button
              type="button"
              @click="handleScrollTo('intelligence')"
              class="flex items-center gap-3 p-3 rounded-2xl bg-white/[0.07] hover:bg-white/[0.12] border border-white/10 transition active:scale-[0.98] text-left"
            >
              <div class="w-10 h-10 rounded-xl bg-amber-400/20 text-amber-300 flex items-center justify-center shrink-0 border border-amber-300/30">
                <Sparkles :size="20" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-xs font-semibold text-white truncate">Assistant IA Exécutif</p>
                <p class="text-[11px] text-white/60 truncate mt-0.5">Analyses et synthèses intelligentes</p>
              </div>
              <ChevronRight :size="16" class="text-white/40 shrink-0" />
            </button>

            <!-- Impact -->
            <button
              type="button"
              @click="handleScrollTo('impact')"
              class="flex items-center gap-3 p-3 rounded-2xl bg-white/[0.07] hover:bg-white/[0.12] border border-white/10 transition active:scale-[0.98] text-left"
            >
              <div class="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center shrink-0 text-white">
                <HeartHandshake :size="20" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-xs font-semibold text-white truncate">Impact & Éthique</p>
                <p class="text-[11px] text-white/60 truncate mt-0.5">Transparence et protection des données</p>
              </div>
              <ChevronRight :size="16" class="text-white/40 shrink-0" />
            </button>

            <!-- FAQ -->
            <button
              type="button"
              @click="handleScrollTo('faq')"
              class="flex items-center gap-3 p-3 rounded-2xl bg-white/[0.07] hover:bg-white/[0.12] border border-white/10 transition active:scale-[0.98] text-left"
            >
              <div class="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center shrink-0 text-white">
                <HelpCircle :size="20" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-xs font-semibold text-white truncate">Questions fréquentes</p>
                <p class="text-[11px] text-white/60 truncate mt-0.5">Tout savoir sur BarakaGive</p>
              </div>
              <ChevronRight :size="16" class="text-white/40 shrink-0" />
            </button>
          </div>
        </div>

        <!-- Section 3 : Contact & Démo -->
        <div class="mt-5 pt-4 border-t border-white/[0.12]">
          <RouterLink
            to="/contact"
            @click="sheetOpen = false"
            class="flex items-center justify-between p-3.5 rounded-2xl bg-white/10 hover:bg-white/15 border border-white/15 transition active:scale-[0.98]"
          >
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-rose-baraka/20 text-rose-baraka flex items-center justify-center shrink-0">
                <Mail :size="20" />
              </div>
              <div>
                <p class="text-xs font-bold text-white leading-tight">Demander une démonstration</p>
                <p class="text-[11px] text-white/65 mt-0.5">Échangez directement avec notre équipe</p>
              </div>
            </div>
            <ChevronRight :size="18" class="text-white/40" />
          </RouterLink>
        </div>

        <!-- Barre indicateur d'accueil iOS -->
        <div class="w-32 h-1 bg-white/20 rounded-full mx-auto mt-6 shrink-0" />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import {
  Home,
  Layers,
  ShieldCheck,
  MessageSquare,
  LayoutGrid,
  X,
  ChevronRight,
  LogIn,
  UserPlus,
  Sparkles,
  Workflow,
  HeartHandshake,
  HelpCircle,
  Mail,
} from "lucide-vue-next";

const props = defineProps({
  activeSection: {
    type: String,
    default: "hero",
  },
});

const emit = defineEmits(["navigate"]);

const route = useRoute();
const router = useRouter();
const sheetOpen = ref(false);

const toggleSheet = () => {
  sheetOpen.value = !sheetOpen.value;
};
const openSheet = () => {
  sheetOpen.value = true;
};
const closeSheet = () => {
  sheetOpen.value = false;
};

const scrollTo = (sectionId) => {
  emit("navigate", sectionId);
  if (route.path !== "/") {
    router.push({ path: "/", hash: `#${sectionId}` });
    return;
  }
  const el = document.getElementById(sectionId);
  if (el) {
    el.scrollIntoView({ behavior: "smooth" });
  }
};

const handleScrollTo = (sectionId) => {
  sheetOpen.value = false;
  setTimeout(() => {
    scrollTo(sectionId);
  }, 100);
};

defineExpose({
  toggleSheet,
  openSheet,
  closeSheet,
  sheetOpen,
});
</script>

<style scoped>
/* Animations fluides style iOS */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active {
  transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
}
.slide-up-leave-active {
  transition: transform 0.24s cubic-bezier(0.4, 0, 0.7, 0.2), opacity 0.2s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
