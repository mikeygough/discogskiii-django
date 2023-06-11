/** @type {import('tailwindcss').Config} */

// Create an array for all of the colors you want to use
const colorClasses = [
  'slate', 'gray', 'zinc', 'neutral', 'stone', 'red', 'orange', 'amber', 'yellow', 'lime', 'green', 'emerald',
  'teal', 'cyan', 'sky', 'blue', 'indigo', 'violet', 'purple', 'fuchsia', 'pink', 'rose'
  ];

// tailwind.config.js
module.exports = {
  content: ["./discogskiii/**/*.{html,js}",
            "./firstapp/**/*.{html,js}"],
  // Map over the labels and add them to the safelist
  safelist: [
      ...colorClasses.map((color) => `from-${color}-600`)
  ],
  theme: {
    extend: {
    },
  },
  plugins: [],
}

