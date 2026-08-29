module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}', // Ensure all your files are scanned
  ],
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)', // Map --color-primary to Tailwind's primary color
      },
    },
  },
  plugins: [],
};