/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"SF Pro Text"', '"Inter Variable"', 'Inter', '"Segoe UI"', 'Roboto', 'sans-serif'],
        display: ['-apple-system', 'BlinkMacSystemFont', '"SF Pro Display"', '"Inter Variable"', 'Inter', '"Segoe UI"', 'Roboto', 'sans-serif']
      },
      // Cores vêm das variáveis CSS em app.css, que mudam sozinhas no modo escuro do sistema
      colors: {
        bg: 'rgb(var(--bg) / <alpha-value>)',
        surface: 'rgb(var(--surface) / <alpha-value>)',
        elevated: 'rgb(var(--elevated) / <alpha-value>)',
        ink: 'rgb(var(--ink) / <alpha-value>)',
        muted: 'rgb(var(--muted) / <alpha-value>)',
        // "line" (bordas finas) fica em app.css porque já inclui opacidade
        accent: 'rgb(var(--accent) / <alpha-value>)',
        danger: 'rgb(var(--danger) / <alpha-value>)'
      },
      maxWidth: {
        page: '980px'
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-400px 0' },
          '100%': { backgroundPosition: '400px 0' }
        },
        pulseDot: {
          '0%, 80%, 100%': { opacity: '0.25' },
          '40%': { opacity: '1' }
        }
      },
      animation: {
        shimmer: 'shimmer 1.4s linear infinite',
        'pulse-dot': 'pulseDot 1.2s ease-in-out infinite'
      }
    }
  },
  plugins: []
};
