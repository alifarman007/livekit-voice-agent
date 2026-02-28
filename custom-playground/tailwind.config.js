/** @type {import('tailwindcss').Config} */

const colors = require("tailwindcss/colors");
const shades = ["50","100","200","300","400","500","600","700","800","900","950"];
const colorList = ["gray","green","cyan","amber","violet","blue","rose","pink","teal","red"];
const uiElements = ["bg","selection:bg","border","text","hover:bg","hover:border","hover:text","ring","focus:ring"];
const customColors = {
  cyan: colors.cyan,
  green: colors.green,
  amber: colors.amber,
  violet: colors.violet,
  blue: colors.blue,
  rose: colors.rose,
  pink: colors.pink,
  teal: colors.teal,
  red: colors.red,
};

let customShadows = {};
let shadowNames = [];
let textShadows = {};
let textShadowNames = [];

for (const [name, color] of Object.entries(customColors)) {
  customShadows[`${name}`] = `0px 0px 10px ${color["500"]}`;
  customShadows[`lg-${name}`] = `0px 0px 20px ${color["600"]}`;
  textShadows[`${name}`] = `0px 0px 4px ${color["700"]}`;
  textShadowNames.push(`drop-shadow-${name}`);
  shadowNames.push(`shadow-${name}`);
  shadowNames.push(`shadow-lg-${name}`);
  shadowNames.push(`hover:shadow-${name}`);
}

const safelist = [
  "bg-black", "bg-white", "transparent", "object-cover", "object-contain",
  ...shadowNames,
  ...textShadowNames,
  ...shades.flatMap((shade) => [
    ...colorList.flatMap((color) => [
      ...uiElements.flatMap((element) => [`${element}-${color}-${shade}`]),
    ]),
  ]),
  // Dashboard animation classes
  "animate-fade-in-up", "animate-fade-in-scale", "animate-pulse-ring",
  "animate-pulse-dot", "animate-connecting-pulse", "animate-spin-slow",
  "animate-bounce-dot-1", "animate-bounce-dot-2", "animate-bounce-dot-3",
  "animate-bar-1", "animate-bar-2", "animate-bar-3", "animate-bar-4", "animate-bar-5",
  "stagger-1", "stagger-2", "stagger-3", "stagger-4", "stagger-5", "stagger-6",
  "frosted-glass", "glow-cyan", "glow-green", "glow-purple",
];

module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    colors: {
      transparent: "transparent",
      current: "currentColor",
      black: colors.black,
      white: colors.white,
      gray: colors.neutral,
      ...customColors,
    },
    fontFamily: {
      sans: ['"Plus Jakarta Sans"', '-apple-system', 'sans-serif'],
      mono: ['"IBM Plex Mono"', 'monospace'],
    },
    extend: {
      dropShadow: { ...textShadows },
      boxShadow: { ...customShadows },
      keyframes: {
        "fade-in-out": {
          "0%": { opacity: "0" },
          "20%": { opacity: "1" },
          "80%": { opacity: "1" },
          "100%": { opacity: "0" },
        },
      },
      animation: {
        "fade-in-out": "fade-in-out 1s ease-in-out",
      },
    },
  },
  plugins: [],
  safelist,
};
