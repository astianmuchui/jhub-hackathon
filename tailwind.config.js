/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/*.html',
    './**/*.django',
  ],
  theme: {
    extend: {
      colors: {
        darkBlue: "#1B3C73",
        lightPink: "#FFCAD4",
        primaryPink: "#FF407D",
        lightBlue: "#40679E"
      },
    },
  },
  plugins: [require('flowbite')],
}
