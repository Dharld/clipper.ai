const { fontFamily } = require('tailwindcss/defaultTheme');

/**** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: ['index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        slate: {
          950: '#050507'
        },
        clipper: {
          primary: '#6d5dfc',
          secondary: '#9d4dff',
          accent: '#5ce1e6'
        }
      },
      fontFamily: {
        sans: ['"General Sans"', 'Inter', ...fontFamily.sans]
      },
      backgroundImage: {
        'gradient-glass': 'linear-gradient(135deg, rgba(109,93,252,0.08) 0%, rgba(157,77,255,0.08) 100%)'
      },
      boxShadow: {
        glow: '0 0 45px rgba(109,93,252,0.45)'
      }
    }
  },
  plugins: []
};
