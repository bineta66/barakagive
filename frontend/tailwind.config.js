/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bleu-nuit': '#00313C',
        'rose-baraka': '#D20C4F',
        'or': '#0a3a5c',        // bleu secondaire (remplace le doré)
        'bleu-accent': '#1a6fad', // bleu vif pour les accents
      },
      fontFamily: {
        poppins: ['Poppins', 'sans-serif'],
      },
      boxShadow: {
        xs: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
      },
    },
  },
  plugins: [],
}
