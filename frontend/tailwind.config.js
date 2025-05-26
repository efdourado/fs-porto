/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        'primary-gradient': {
          start: '#4F46E5',
          end: '#7C3AED'
        },
        'accent': {
          light: '#F9FAFB',
          dark: '#111827'
        }
      },
      animation: {
        'gradient': 'gradient 8s ease infinite',
        'fade-in': 'fadeIn 0.5s ease-out'
      },
      keyframes: {
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' }
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 }
        }
      }
    }
  },
  plugins: [require('daisyui')],
  daisyui: {
    themes: [
      {
        contratuslight: {
          "primary": "#4F46E5",
          "secondary": "#7C3AED",
          "accent": "#1FB2A6",
          "neutral": "#2B3440",
          "base-100": "#FFFFFF",
          "base-200": "#F9FAFB",
          "base-300": "#F3F4F6",
          "info": "#3ABFF8",
          "success": "#36D399",
          "warning": "#FBBD23",
          "error": "#F87272"
        },
        contratusdark: {
          "primary": "#6366F1",
          "secondary": "#8B5CF6",
          "accent": "#22D3EE",
          "neutral": "#191D24",
          "base-100": "#1F2937",
          "base-200": "#111827",
          "base-300": "#0F172A",
          "info": "#0EA5E9",
          "success": "#10B981",
          "warning": "#F59E0B",
          "error": "#EF4444"
        }
      },
      "light",
      "dark",
      "corporate"
    ]
  }
};
