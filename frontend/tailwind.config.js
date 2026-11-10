/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bimmer: {
          blue: {
            light: '#0096D6',
            dark: '#00205B',
          },
          red: '#E00034',
        },
        obsidian: '#0A0D12',
        card: '#121620',
        steel: '#1E2638',
      },
      backgroundImage: {
        'm-stripe': 'linear-gradient(90deg, #0096D6 0%, #00205B 50%, #E00034 100%)',
        'm-stripe-vertical': 'linear-gradient(180deg, #0096D6 0%, #00205B 50%, #E00034 100%)',
        'm-badge-slant': 'linear-gradient(135deg, #0096D6 0%, #00205B 50%, #E00034 100%)',
      }
    },
  },
  plugins: [],
}
