/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          pink: {
            DEFAULT: '#DB2777',
            50: '#FDF2F8',
            100: '#FCE7F3',
            200: '#FBCFE8',
            300: '#F699D1',
            400: '#F472B6',
            500: '#EC4899',
            600: '#DB2777',
            700: '#BE185D',
            800: '#9D174D',
            900: '#831843',
          },
          black: {
            DEFAULT: '#0B0F19',
            light: '#111827',
            muted: '#1F2937',
          },
          white: {
            DEFAULT: '#FFFFFF',
            off: '#FAFAFA',
          },
          neutral: {
            50: '#F9FAFB',
            100: '#F3F4F6',
            200: '#E5E7EB',
            300: '#D1D5DB',
            400: '#9CA3AF',
            500: '#6B7280',
            600: '#4B5563',
            700: '#374151',
            800: '#1F2937',
            900: '#111827',
          }
        }
      },
      fontFamily: {
        heading: ['Playfair Display', 'Georgia', 'serif'],
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'pink-glow': '0 4px 20px -2px rgba(219, 39, 119, 0.25)',
        'premium': '0 10px 30px -5px rgba(11, 15, 25, 0.08)',
      }
    },
  },
  plugins: [],
}
