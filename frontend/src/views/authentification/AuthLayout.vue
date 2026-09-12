<template>
  <div class="min-h-screen bg-slate-100 flex items-center justify-center p-4">
    <div class="w-[1280px] h-[1024px] bg-slate-100 inline-flex flex-col justify-start items-start">
      <div class="self-stretch min-h-[1024px] inline-flex justify-start items-start">
        <!-- Partie gauche -->
        <div class="flex-1 h-[1024px] p-16 relative bg-slate-900 inline-flex flex-col justify-between items-start overflow-hidden">
          <div class="w-[640px] h-[1024px] left-0 top-0 absolute opacity-75 overflow-hidden">
            <img
              src="@/assets/images/imagelogo.png"
              alt="Fond"
              class="w-[1538px] h-[1025px] left-[-528px] top-0 absolute object-cover"
            />
            <div class="w-96 h-40 max-w-[512px] py-10 left-[99px] top-[776px] absolute inline-flex flex-col justify-start items-center gap-3">
              <div class="size- max-w-96 px-4 flex flex-col justify-start items-center">
                <div class="text-center justify-center text-white text-lg font-extrabold font-['Poppins'] leading-6">
                  {{ leftText }}
                </div>
              </div>
              <div class="w-40 pt-8 flex flex-col justify-start items-start">
                <div class="w-40 opacity-40 inline-flex justify-center items-center">
                  <div class="w-16 h-px bg-white"></div>
                  <div class="w-4 h-1.5 pl-3 inline-flex flex-col justify-start items-start">
                    <div class="size-1.5 bg-green-700"></div>
                  </div>
                  <div class="w-20 h-px pl-3 inline-flex flex-col justify-start items-start">
                    <div class="self-stretch h-px bg-white"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Partie droite -->
        <div class="flex-1 h-[1024px] p-20 bg-white inline-flex flex-col justify-between items-start">
          <div class="self-stretch h-4"></div>

          <div class="w-[536px] flex-1 min-h-[515.50px] relative">
            <!-- Logo -->
            <div class="w-44 h-14 left-[136px] top-[46px] absolute">
              <img
                src="@/assets/images/logologin.png"
                alt="Logo"
                class="size-14 left-[-10px] top-0 absolute object-contain"
              />
              <div class="left-[46px] top-[16px] absolute text-center justify-center text-yellow-800 text-2xl font-bold font-['Poppins'] leading-9">
                BarakaGive
              </div>
            </div>

            <!-- Contenu du formulaire -->
            <div class="w-96 left-0 top-[114.50px] absolute">
              <div class="w-96 left-0 top-[32px] absolute inline-flex flex-col justify-start items-start gap-2">
                <div class="self-stretch flex flex-col justify-start items-start">
                  <div class="self-stretch justify-center text-yellow-800 text-3xl font-bold font-['Poppins'] leading-9">
                    {{ title }}
                  </div>
                </div>
                <div class="self-stretch flex flex-col justify-start items-start">
                  <div class="self-stretch justify-center text-slate-900 text-base font-semibold font-['Poppins'] leading-6">
                    {{ subtitle }}
                  </div>
                </div>
              </div>

              <!-- Formulaire -->
              <div class="w-96 left-0 top-[132px] absolute inline-flex flex-col justify-start items-start gap-6">
                <slot />
              </div>

              <!-- Bouton retour -->
              <div v-if="showBackButton" class="w-96 h-12 left-0 top-[460px] absolute bg-white rounded-md border border-yellow-800">
                <div class="w-96 h-6 left-[8px] top-[473.50px] absolute">
                  <div class="size- left-[129px] top-[3px] absolute inline-flex justify-start items-center">
                    <div class="w-5 h-3.5 pr-1.5 inline-flex flex-col justify-start items-start">
                      <div class="size-3.5 flex flex-col justify-center items-start overflow-hidden">
                        <div class="w-3.5 flex-1 relative overflow-hidden">
                          <div class="w-2.5 h-2 left-[1.75px] top-[2.92px] absolute outline outline-1 outline-offset-[-0.58px] outline-yellow-800"></div>
                        </div>
                      </div>
                    </div>
                    <div class="size- inline-flex flex-col justify-start items-center">
                      <div class="text-center justify-center text-yellow-800 text-xs font-bold font-['Poppins'] leading-4">Retour à la connexion</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="self-stretch pt-6 border-t border-slate-200 inline-flex justify-between items-center">
            <div class="size- flex justify-start items-center">
              <div class="size-3.5 relative overflow-hidden">
                <div class="size-2.5 left-[2.33px] top-[1.75px] absolute outline outline-1 outline-offset-[-0.58px] outline-gray-500"></div>
              </div>
              <div class="size- pl-1.5 inline-flex flex-col justify-start items-start">
                <div class="justify-center text-gray-800 text-xs font-normal font-['Poppins'] leading-4">
                  {{ footerLeft }}
                </div>
              </div>
            </div>
            <div class="size- inline-flex flex-col justify-start items-start">
              <div class="justify-center text-gray-800 text-xs font-normal font-['Poppins'] leading-4">
                {{ footerRight }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    required: true,
  },
  leftText: {
    type: String,
    required: true,
  },
  footerLeft: {
    type: String,
    default: "Lien de réinitialisation sécurisé à usage unique",
  },
  footerRight: {
    type: String,
    default: "Assistance : support@barakagive.org",
  },
  showBackButton: {
    type: Boolean,
    default: true,
  },
})
</script>
