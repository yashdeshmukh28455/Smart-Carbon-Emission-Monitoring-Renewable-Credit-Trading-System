import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark theme colors
        'dark-bg': '#0a0e1a',
        'dark-surface': '#141824',
        'dark-elevated': '#1e2330',

        // Eco-green accents
        'eco-green': {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
        },

        // Status colors
        'status-safe': '#10b981',
        'status-warning': '#fbbf24',
        'status-exceeded': '#ef4444',
      },
    },
  },
  plugins: [],
};

export default config;
