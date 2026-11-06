/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        pitch: {
          900: '#0b0f17',
          800: '#111827',
          700: '#1f2937',
          600: '#374151',
        },
        accent: {
          green: '#10b981',
          red: '#ef4444',
          yellow: '#f59e0b',
          blue: '#3b82f6',
        }
      }
    },
  },
  plugins: [],
}

