import type { Config } from 'tailwindcss'

export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f2f8ff', 100: '#e6f1ff', 200: '#cce3ff', 300: '#99c7ff', 400: '#66abff', 500: '#338fff', 600: '#0a75ff', 700: '#005fd6', 800: '#004aa6', 900: '#003575'
        }
      }
    },
  },
  plugins: [],
} satisfies Config


