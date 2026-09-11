/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        neza: {
          earth: '#0F2043',      // American Earth (deep surfaces, sidebar, dark canvas)
          royal: '#162F65',      // Royal Navy Blue (major panels, headers, dark cards)
          cobalt: '#3361AC',     // Light Cobalt Blue (primary interactive, active nav)
          buttercup: '#E8AF30',  // Buttercup (primary attention, important CTAs, priority highlights)
          gold: '#E8C766',       // Pastel Deep Gold (secondary highlights, chart accents)
          vintage: '#E7E6DD',    // Vintage White (light backgrounds, readable surfaces)
          success: '#16A34A',
          error: '#DC2626',
          warning: '#E8AF30',
        }
      },
      fontFamily: {
        sans: ['Geist', 'Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        'neza-sm': '6px',
        'neza': '8px',
        'neza-md': '10px',
        'neza-lg': '12px',
      },
      boxShadow: {
        'neza-subtle': '0 1px 3px 0 rgba(15, 32, 67, 0.1), 0 1px 2px -1px rgba(15, 32, 67, 0.1)',
        'neza-card': '0 4px 6px -1px rgba(15, 32, 67, 0.08), 0 2px 4px -2px rgba(15, 32, 67, 0.06)',
        'neza-panel': '0 10px 15px -3px rgba(15, 32, 67, 0.12), 0 4px 6px -4px rgba(15, 32, 67, 0.08)',
      },
      backgroundImage: {
        'noir': 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0f0f0f 100%)',
        'noir-card': 'linear-gradient(145deg, #1c1c1c 0%, #141414 100%)',
        'noir-hero': 'linear-gradient(135deg, #111 0%, #1f1f1f 40%, #111 100%)',
      }
    },
  },
  plugins: [],
};
