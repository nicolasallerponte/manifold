/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        mono: ['"Roboto Mono"', '"Courier New"', "monospace"],
      },
      colors: {
        bg: "#050608",
        panel: "#08090c",
        border: "#1a1f2e",
        phosphor: "#00ff88",
        phosphorDim: "#00cc6a",
        phosphorFaint: "#004422",
        amber: "#ffaa00",
        red: "#ff3333",
        blue: "#4488ff",
        muted: "#2a3040",
        text: "#a0b0c0",
        textDim: "#3a4a5a",
      },
    },
  },
  plugins: [],
};