/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          yellow: "#FACC15",
          yellowHover: "#EAB308",
          deepNavy: "#0E1726",
          secondaryNavy: "#101B2D",
          corpBlue: "#24466F",
          softBg: "#F5F7FB",
          surface: "#FFFFFF",
          textPrimary: "#172033",
          textSecondary: "#718096",
          border: "#E5EAF1",
          success: "#16A34A",
          error: "#DC2626",
          warning: "#D97706"
        }
      },
      fontFamily: {
        sans: ["Inter", "Plus Jakarta Sans", "Manrope", "system-ui", "sans-serif"]
      }
    },
  },
  plugins: [],
}
