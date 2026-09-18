<template>
  <main class="landing-page">
    <header class="site-header">
      <div class="header-inner">
        <RouterLink to="/" class="brand" aria-label="BarakaGive accueil">
          <img src="@/assets/images/logologin.png" alt="" class="brand-mark" />
          <span>BARAKAGIVE</span>
        </RouterLink>
        <nav class="desktop-nav" aria-label="Navigation principale">
          <a href="#accueil">Accueil</a>
          <a href="#mission">A propos</a>
          <a href="#fonctionnalites">Fonctionnalités</a>
          <a href="#contact">Contact</a>
        </nav>
        <button
          type="button"
          class="hamburger"
          :class="{ open: mobileOpen }"
          @click="mobileOpen = !mobileOpen"
          aria-label="Menu"
          aria-expanded="false"
        >
          <span></span><span></span><span></span>
        </button>
        <transition name="fade">
          <div v-if="mobileOpen" class="mobile-menu">
            <a href="#accueil" @click="mobileOpen=false">Accueil</a>
            <a href="#mission" @click="mobileOpen=false">A propos</a>
            <a href="#fonctionnalites" @click="mobileOpen=false">Fonctionnalités</a>
            <a href="#contact" @click="mobileOpen=false">Contact</a>
            <RouterLink to="/connexion" @click="mobileOpen=false">Se connecter</RouterLink>
            <RouterLink to="/inscription" @click="mobileOpen=false">S'inscrire</RouterLink>
          </div>
        </transition>
        <div class="header-actions">
          <RouterLink to="/connexion" class="login-link">Se connecter</RouterLink>
          <RouterLink to="/inscription" class="signup-link">S'inscrire</RouterLink>
        </div>
      </div>
    </header>

    <section id="accueil" class="hero">
      <div class="hero-shade"></div>
      <div class="hero-content">
        <p class="eyebrow">La solidarité, mieux organisée</p>
        <h1>Connecter les coeurs,<br /><span>Transformer des vies</span></h1>
        <p class="hero-copy">
          BarakaGive accompagne les ONG, associations et fondations dans la gestion
          transparente de leurs projets, dons, bénéficiaires et rapports d'impact.
        </p>
        <div class="hero-actions">
          <RouterLink to="/inscription" class="primary-button">S'inscrire gratuitement</RouterLink>
          <RouterLink to="/connexion" class="secondary-button">Se connecter <span aria-hidden="true">-&gt;</span></RouterLink>
        </div>
      </div>
    </section>

    <section id="mission" class="mission-section">
      <div class="mission-panel">
        <p class="eyebrow amber">BARAKAGIVE</p>
        <h2>Une solution pensée pour les acteurs de la solidarité au Sénégal</h2>
        <p class="mission-copy">
          Que vous soyez une petite association de quartier à Saint-Louis ou une grande
          fondation internationale basée à Dakar, BarakaGive s'adapte à vos besoins.
        </p>
        <div class="feature-list" id="fonctionnalites">
          <article v-for="feature in features" :key="feature.title" class="feature-item">
            <span class="feature-icon" aria-hidden="true">{{ feature.icon }}</span>
            <div>
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.text }}</p>
            </div>
          </article>
        </div>
      </div>
      <div class="mission-image-wrap">
        <img src="@/assets/images/imagelogo.png" alt="Une équipe BarakaGive au service d'une communauté" />
      </div>
    </section>

    <section class="steps-section">
      <div class="section-heading">
       
        <h2>Rejoindre   BarakaGive</h2>
         <p class="section-kicker">COMMENT CA FONCTIONNE ?</p>
        <p>Rejoignez BarakaGive en quelques clics et commencez à gérer vos actions humanitaires en toute simplicité.</p>
      </div>

      <div class="steps">
        <article v-for="(step, index) in steps" :key="step.title" class="step" :class="step.type">
          <div class="step-number">{{ index + 1 }}</div>

          <div class="step-row" :class="{ reverse: step.type === 'mail' }">
            <div class="step-copy">
              <h3>{{ step.title }}</h3>
              <p>{{ step.text }}</p>
            </div>

            <div class="step-visual" :class="step.type">
              <template v-if="step.type === 'form'">
                <div class="mock-form">
                  <div class="mock-form__heading">Créer mon compte</div>
                  <div class="mock-input"></div>
                  <div class="mock-input"></div>
                  <div class="mock-input"></div>
                  <div class="mock-input"></div>
                  <RouterLink to="/inscription" class="mock-action-button">S'inscrire</RouterLink>
                </div>
                <div class="mock-illustration illustration-person">
                  <div class="avatar-head"></div>
                  <div class="avatar-body"></div>
                  <div class="avatar-laptop"></div>
                  <div class="avatar-leaf leaf-one"></div>
                  <div class="avatar-leaf leaf-two"></div>
                </div>
              </template>

              <template v-else-if="step.type === 'mail'">
                <div class="mock-mail">
                  <div class="mail-card">
                    <div class="mail-title">Activer mon compte</div>
                    <div class="mail-line short"></div>
                    <div class="mail-line"></div>
                    <button>Activer mon compte</button>
                  </div>
                </div>
              </template>

              <template v-else>
                <div class="mock-login">
                  <div class="mock-form__heading">Connexion</div>
                  <div class="mock-input"></div>
                  <div class="mock-input"></div>
                  <button>Se connecter</button>
                  <small>Mot de passe oublié ?</small>
                </div>
                <div class="mock-illustration illustration-person small">
                  <div class="avatar-head"></div>
                  <div class="avatar-body"></div>
                  <div class="avatar-laptop"></div>
                  <div class="avatar-leaf leaf-one"></div>
                  <div class="avatar-leaf leaf-two"></div>
                </div>
              </template>
            </div>
          </div>
        </article>
      </div>
    </section>

    <section id="contact" class="contact-section">
      <div class="contact-intro">
        <h2>Parlons de votre mission</h2>
        <p>Notre équipe est basée à Dakar et se déplace dans tout le Sénégal pour vous accompagner dans votre transformation digitale.</p>
        <div class="contact-details">
          <div class="contact-detail">
            <span class="contact-icon" aria-hidden="true">*</span>
            <div><h3>Notre Bureau</h3><p>Plateau, Avenue Léopold Sédar Senghor, Dakar, Sénégal</p></div>
          </div>
          <div class="contact-detail">
            <span class="contact-icon" aria-hidden="true">@</span>
            <div><h3>Téléphone</h3><a href="tel:+221338000000">+221 33 800 00 00</a></div>
          </div>
          <div class="contact-detail">
            <span class="contact-icon" aria-hidden="true">@</span>
            <div><h3>Email</h3><a href="mailto:contact@barakagive.sn">contact@barakagive.sn</a></div>
          </div>
        </div>
      </div>
      <form class="contact-card" @submit.prevent="submitContactForm">
        <div class="form-row">
          <label>Nom complet<input v-model="contactForm.name" type="text" placeholder="Amadou Sow" required /></label>
          <label>Organisation<input v-model="contactForm.organization" type="text" placeholder="ONG Solidarité Plus" required /></label>
        </div>
        <div class="form-row">
          <label>Email professionnel<input v-model="contactForm.email" type="email" placeholder="contact@ong.sn" required /></label>
          <label>Téléphone<input v-model="contactForm.phone" type="tel" placeholder="+221 77 000 00 00" /></label>
        </div>
        <label>Sujet<input v-model="contactForm.subject" type="text" placeholder="Demande de démo personnalisée" required /></label>
        <label>Message<textarea v-model="contactForm.message" placeholder="Décrivez brièvement vos besoins..." rows="4" required></textarea></label>
        <button type="submit">{{ contactSent ? "Message envoyé" : "Envoyer le message" }}</button>
        <p v-if="contactSent" class="form-success" role="status">Merci, votre demande a bien été prise en compte.</p>
      </form>
    </section>

    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-brand-wrap">
          <div class="footer-brand"><span>BARAKAGIVE</span></div>
          <p>Agir ensemble, changer des vies.</p>
          <p class="footer-description">Plateforme digitale dédiée aux ONG, associations et fondations pour mieux piloter leurs projets, mobiliser les dons et rendre leur impact visible.</p>
        </div>

        <div class="footer-column">
          <h3>Navigation</h3>
          <div class="footer-links">
            <a href="#accueil">Accueil</a>
            <a href="#mission">A propos</a>
            <a href="#fonctionnalites">Fonctionnalités</a>
            <a href="#contact">Contact</a>
          </div>
        </div>

        <div class="footer-column">
          <h3>Solutions</h3>
          <ul>
            <li>Suivi de projets</li>
            <li>Gestion des dons</li>
            <li>Rapports d'impact</li>
            <li>Administration ONG</li>
          </ul>
        </div>

        <div class="footer-column">
          <h3>Contact</h3>
          <ul>
            <li><a href="tel:+221338000000">+221 33 800 00 00</a></li>
            <li><a href="mailto:contact@barakagive.sn">contact@barakagive.sn</a></li>
            <li>Dakar, Sénégal</li>
          </ul>
        </div>

        <div class="footer-column">
          <h3>Réseaux</h3>
          <ul>
            <li>LinkedIn</li>
            <li>Facebook</li>
            <li>Instagram</li>
          </ul>
        </div>
      </div>

      <small>© 2025 BarakaGive SN. Tous droits réservés.</small>
    </footer>
  </main>
</template>

<script setup>
import { ref } from "vue"
const mobileOpen = ref(false)
import { RouterLink } from "vue-router"

const features = [
  { icon: "+", title: "Organisation des projets", text: "Planification et suivi en temps réel de vos actions sur le terrain." },
  { icon: "o", title: "Gestion des bénéficiaires", text: "Une base de données sécurisée pour un meilleur ciblage social." },
  { icon: "ok", title: "Transparence financière", text: "Des rapports détaillés pour rassurer vos bailleurs de fonds." },
]

const steps = [
  { title: "Inscrivez-vous", text: "Remplissez le formulaire d'inscription avec les informations de votre ONG et du gérant. Aucun mot de passe n'est demandé.", type: "form" },
  { title: "Activez votre compte", text: "Vous recevez un email contenant un lien d'activation et un mot de passe temporaire.", type: "mail" },
  { title: "Connectez-vous", text: "Une fois votre compte activé, connectez-vous avec l'email et le mot de passe reçus. Vous serez automatiquement redirigé vers votre tableau de bord.", type: "login" },
]

const contactSent = ref(false)
const contactForm = ref({ name: "", organization: "", email: "", phone: "", subject: "", message: "" })

function submitContactForm() {
  contactSent.value = true
}
</script>

<style scoped>
:global(*) { box-sizing: border-box; }
:global(html) { scroll-behavior: smooth; }
.landing-page { color: #0f172a; background: #FFFF; font-family: "Segoe UI", "Noto Sans", Arial, sans-serif; }
.site-header { position: fixed; z-index: 50; top: 0; left: 0; right: 0; display: flex; align-items: center; justify-content: center; height: 72px; color: white; background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(148, 163, 184, 0.12); }
.header-inner { display: flex; align-items: center; justify-content: space-between; width: 100%; max-width: 1280px; gap: 14px; padding: 0 24px; }
.brand, .footer-brand { display: flex; align-items: center; gap: 10px; color: inherit; text-decoration: none; font-weight: 800; letter-spacing: .04em; }
.brand span { white-space: nowrap; line-height: 1; }
.brand-mark { width: 32px; height: 32px; object-fit: contain; filter: brightness(0) invert(1); }
.desktop-nav, .header-actions, .footer-links { display: flex; align-items: center; gap: 16px; flex-wrap: nowrap; }
.desktop-nav { margin-left: auto; margin-right: 8px; }
.desktop-nav a, .login-link { color: rgba(255,255,255,.82); text-decoration: none; font-size: 12.5px; font-weight: 600; white-space: nowrap; }
.desktop-nav a:hover, .login-link:hover { color: #744D03; }
.signup-link, .primary-button { background: #744D03; color: white; text-decoration: none; font-weight: 700; border-radius: 12px; padding: 10px 16px; white-space: nowrap; }
.header-actions { white-space: nowrap; }
.hero { position: relative; min-height: 824px; display: flex; align-items: center; background: url("@/assets/images/imagelogo.png") center/cover; }
.hero-shade { position: absolute; inset: 0; background: linear-gradient(90deg, rgba(15,23,42,.98) 0%, rgba(15,23,42,.82) 42%, rgba(15,23,42,.08) 100%); }
.hero-content { position: relative; z-index: 1; width: min(1160px, 100%); margin: auto; padding: 130px 32px 70px; }
.eyebrow { margin: 0 0 18px; color: #f8fafc; font-size: 12px; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }
.eyebrow.amber { color: #744D03; }
h1, h2, h3 { font-family: "Segoe UI", "Noto Sans", Arial, sans-serif; }
h1 { max-width: 720px; margin: 0; color: white; font-size: clamp(42px, 5.4vw, 76px); line-height: 1.04; letter-spacing: -.04em; }
h1 span { color: #e09407; }
.hero-copy { max-width: 650px; margin: 28px 0 0; color: rgba(255,255,255,.92); font-size: 18px; line-height: 1.7; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 34px; }
.secondary-button { display: inline-flex; gap: 12px; align-items: center; padding: 13px 22px; border-radius: 12px; color: #0f172a; background: white; text-decoration: none; font-weight: 700; }
.mission-section { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, .9fr); gap: 56px; align-items: center; max-width: 1280px; margin: auto; padding: 110px 32px; }
.mission-panel { padding: 48px 40px; border-radius: 28px; background: #0f172a; color: white; }
h2 { margin: 0; font-size: clamp(30px, 3vw, 46px); line-height: 1.12; letter-spacing: -.035em; }
.mission-copy, .section-heading > p:last-child, .contact-section p { color: #64748b; font-size: 17px; line-height: 1.7; }
.mission-copy { color: #cbd5e1; margin: 22px 0 42px; }
.feature-list { display: grid; gap: 26px; }
.feature-item { display: flex; gap: 16px; align-items: flex-start; }
.feature-icon { display: grid; place-items: center; flex: 0 0 40px; height: 40px; border-radius: 12px; color: #744D03; background: rgba(245,158,11,.18); font-size: 22px; font-weight: 700; }
.feature-item h3 { margin: 0 0 5px; font-size: 17px; }
.feature-item p { margin: 0; color: #cbd5e1; line-height: 1.5; }
.mission-image-wrap { padding: 8px; border-radius: 28px; background: #e2e8f0; box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05); }
.mission-image-wrap img { display: block; width: 100%; height: 500px; border-radius: 22px; object-fit: cover; }
.steps-section { padding: 110px 32px 90px; color: white; background: #081d31; }
.section-heading { max-width: 900px; margin: 0 auto 54px; text-align: center; }
.section-kicker { display: inline-block; margin-bottom: 12px; color: #f8fafc; font-size: 12px; font-weight: 800; letter-spacing: .18em; text-transform: uppercase; }
.section-heading h2 { margin: 0 0 16px; font-size: clamp(34px, 3vw, 56px); line-height: 1.08; }
.section-heading > p:last-child { max-width: 780px; margin: 0 auto; color: #cbd5e1; font-size: 18px; line-height: 1.7; }
.steps { position: relative; max-width: 1200px; margin: 0 auto; }
.steps::before { content: ""; position: absolute; left: 64px; top: 10px; bottom: 18px; width: 2px; background: rgba(255,255,255,0.2); }
.step { position: relative; display: grid; grid-template-columns: 120px 1fr; gap: 34px; align-items: center; padding: 8px 0 28px; }
.step:last-child { padding-bottom: 0; }
.step-number { position: relative; z-index: 1; display: grid; place-items: center; width: 58px; height: 58px; margin-left: 12px; border: 6px solid #081d31; border-radius: 50%; background: #744D03; color: white; font-size: 24px; font-weight: 800; }
.step-row { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(360px, 1fr); align-items: center; gap: 20px; background: rgba(255,255,255,0.02); border-radius: 20px; }
.step-row.reverse { grid-template-columns: minmax(360px, 1fr) minmax(0, 1.1fr); }
.step-row.reverse .step-copy { order: 2; }
.step-row.reverse .step-visual { order: 1; }
.step-copy { padding: 12px 8px 12px 0; }
.step-copy h3 { margin: 0 0 10px; font-size: clamp(26px, 2.4vw, 36px); line-height: 1.15; }
.step-copy p { margin: 0; color: #dbe4ef; font-size: 18px; line-height: 1.6; }
.step-visual { position: relative; display: flex; align-items: center; justify-content: center; height: 200px; padding: 14px; border-radius: 22px; background: #dfe7f0; }
.step-visual.form, .step-visual.login { background: linear-gradient(135deg, #edf3fb 0%, #dfeaf8 100%); }
.step-visual.mail { background: linear-gradient(135deg, #e8eff9 0%, #d6e5f5 100%); }
.step-visual.mail { flex-direction: row; }
.mock-form, .mock-login { width: 100%; max-width: 310px; padding: 14px 16px 12px; border-radius: 16px; background: rgba(255,255,255,0.7); }
.mock-form__heading { margin-bottom: 8px; color: #0f172a; font-size: 16px; font-weight: 700; }
.mock-input { height: 18px; margin-bottom: 6px; border-radius: 8px; background: rgba(15,23,42,0.06); }
.mock-form button, .mock-login button, .mail-card button, .mock-action-button { display: block; width: 100%; margin-top: 7px; border: none; border-radius: 9px; padding: 7px 12px; background: #0f172a; color: white; font-size: 12px; font-weight: 700; text-align: center; text-decoration: none; cursor: pointer; }
.mock-illustration { position: relative; width: 145px; height: 160px; margin-left: 8px; transform: scale(.84); transform-origin: center; }
.illustration-person .avatar-head { position: absolute; left: 56px; top: 26px; width: 54px; height: 54px; border-radius: 50%; background: #f4c59d; }
.illustration-person .avatar-head::before { content: ""; position: absolute; left: 8px; top: -10px; width: 38px; height: 24px; border-radius: 50% 50% 40% 40%; background: #744D03; }
.illustration-person .avatar-body { position: absolute; left: 36px; top: 78px; width: 96px; height: 90px; border-radius: 32px 32px 18px 18px; background: #744D03; }
.illustration-person .avatar-laptop { position: absolute; left: 18px; top: 128px; width: 132px; height: 52px; border-radius: 12px; background: #0f172a; }
.illustration-person .avatar-laptop::before { content: ""; position: absolute; inset: 8px 10px auto 10px; height: 10px; background: rgba(255,255,255,.25); border-radius: 6px; }
.illustration-person .avatar-leaf { position: absolute; border-radius: 60% 0 60% 0; background: #7db64d; }
.illustration-person .leaf-one { right: 8px; bottom: 20px; width: 42px; height: 60px; transform: rotate(24deg); }
.illustration-person .leaf-two { left: 8px; bottom: 26px; width: 36px; height: 54px; transform: rotate(-18deg); }
.mock-mail { width: 100%; max-width: 310px; }
.mail-card { position: relative; min-height: 164px; padding: 16px 16px 17px; border-radius: 16px; background: rgba(255,255,255,.7); }
.mail-card::before { content: ""; position: absolute; left: 26px; top: 10px; width: 90px; height: 64px; border-radius: 16px; background: linear-gradient(135deg, #744D03, #744D03); transform: rotate(-18deg); }
.mail-card::after { content: ""; position: absolute; right: 38px; top: 22px; width: 18px; height: 18px; border-radius: 50%; background: rgba(15,23,42,.12); }
.mail-title { position: relative; z-index: 1; margin-bottom: 18px; color: #0f172a; font-size: 16px; font-weight: 700; }
.mail-line { position: relative; z-index: 1; height: 12px; margin-bottom: 12px; border-radius: 8px; background: rgba(15,23,42,0.08); }
.mail-line.short { width: 55%; }
.mail-card button { position: relative; z-index: 1; }
.mock-text-panel { margin-left: 6px; max-width: 300px; }
.mock-text-panel h4 { margin: 0 0 8px; color: #0f172a; font-size: 20px; }
.mock-text-panel p { margin: 0; color: #475569; font-size: 16px; line-height: 1.6; }
.mock-login { max-width: 310px; padding: 18px 16px 14px; border-radius: 16px; background: rgba(255,255,255,.72); }
.mock-login small { display: block; margin-top: 12px; text-align: center; color: #475569; }
.contact-section { display: grid; grid-template-columns: 1fr .9fr; gap: 44px; align-items: stretch; max-width: 1180px; margin: auto; padding: 110px 32px; }
.contact-intro { display: flex; flex-direction: column; justify-content: flex-start; height: 100%; min-height: 100%; padding-top: 8px; }
.contact-section h2 { max-width: 570px; }
.contact-section p { max-width: 600px; }
.contact-card { display: grid; gap: 14px; padding: 30px 26px; border-radius: 24px; background: white; align-self: center; }
.form-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.contact-card label { display: grid; gap: 8px; margin: 0; font-size: 12px; line-height: 1.3; font-weight: 700; color: #334155; }
.contact-card input, .contact-card textarea { width: 100%; padding: 11px 12px; border: 1px solid #cbd5e1; border-radius: 12px; background: #f8fafc; color: #0f172a; font-size: 13.5px; line-height: 1.4; transition: border-color .2s ease, box-shadow .2s ease; }
.contact-card input::placeholder, .contact-card textarea::placeholder { color: #94a3b8; font-size: 12px; }
.contact-card input:focus, .contact-card textarea:focus { outline: none; border-color: #744D03; box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05); }
.contact-card textarea { min-height: 110px; resize: vertical; }
.contact-card button { padding: 12px 18px; border: none; border-radius: 12px; background: #744D03; color: white; font-size: 14px; font-weight: 700; cursor: pointer; }
.contact-card a { color: #0f172a; font-weight: 600; text-decoration: none; }
.site-footer { background: #0f172a; color: white; }
.footer-inner { display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr 1fr; gap: 28px; width: 100%; max-width: 1280px; margin: 0 auto; padding: 56px 24px 30px; }
.footer-brand-wrap { display: flex; flex-direction: column; gap: 12px; }
.footer-brand { display: block; }
.footer-brand-wrap p { margin: 0; color: #94a3b8; font-size: 14px; }
.footer-description { line-height: 1.7; max-width: 360px; }
.footer-column { display: flex; flex-direction: column; gap: 14px; }
.footer-column h3 { margin: 0; color: white; font-size: 16px; }
.footer-column ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; color: #94a3b8; font-size: 14px; }
.footer-links { display: flex; flex-direction: column; align-items: flex-start; gap: 10px; }
.footer-links a, .footer-column a, .footer-column li { color: #94a3b8; text-decoration: none; font-size: 14px; }
.site-footer small { display: block; max-width: 1280px; margin: 0 auto; padding: 22px 24px 28px; border-top: 1px solid rgba(255,255,255,.08); color: #64748b; }
@media (max-width: 800px) {
  .desktop-nav { display: none; }
  .hamburger {
    display: flex !important;
    flex-direction: column;
    gap: 5px;
    background: none;
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 8px;
    padding: 8px 9px;
    cursor: pointer;
    margin-left: auto;
  }
  .hamburger span {
    display: block;
    width: 20px;
    height: 2px;
    background: white;
    transition: transform 0.2s ease, opacity 0.2s ease;
  }
  .hamburger.open span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
  .hamburger.open span:nth-child(2) { opacity: 0; }
  .hamburger.open span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }
  .mobile-menu {
    position: absolute;
    top: 72px;
    left: 0;
    right: 0;
    background: rgba(15, 23, 42, 0.97);
    backdrop-filter: blur(10px);
    display: flex;
    flex-direction: column;
    padding: 16px 24px 20px;
    gap: 14px;
  }
  .mobile-menu a, .mobile-menu router-link {
    color: rgba(255,255,255,0.85);
    text-decoration: none;
    font-size: 15px;
    font-weight: 600;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
  }
  .mobile-menu a:last-child, .mobile-menu router-link:last-child { border-bottom: none; }
  .site-header { padding: 0 20px; }
  .login-link { display: none; }
  .hero { min-height: 720px; }
  .hero-content { padding: 120px 24px 60px; }
  .mission-section, .contact-section { grid-template-columns: 1fr; padding: 70px 20px; }
  .mission-panel { padding: 32px 24px; }
  .mission-image-wrap img { height: 330px; }
  .section-heading h2 { white-space: normal; }
  .steps { grid-template-columns: 1fr; gap: 42px; margin-top: 55px; }
  .step h3 { white-space: normal; }
  .step p { white-space: normal; }
  .form-row { grid-template-columns: 1fr; }
  .contact-card { padding: 22px 18px; }
  .footer-inner { grid-template-columns: 1fr; padding: 45px 24px 24px; }
  .footer-links { flex-wrap: wrap; gap: 18px; }
}
</style>

