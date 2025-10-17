# Frontend Setup Guide

This is a [Next.js](https://nextjs.org) dashboard for monitoring CNC machine data.

---

## Setup Steps

### What you need:
- **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
- **Backend running** on http://localhost:8000

---

### How to run it:

#### 1. Navigate to the frontend folder
```bash
cd frontend
```

#### 2. Install the required packages
All dependencies are listed in `package.json`. Just run:
```bash
npm install
```

This will install:
- **Next.js** - React framework
- **axios** - For API calls to the backend
- **recharts** - For data visualization charts
- **date-fns** - For date formatting
- **Tailwind CSS** - For styling

#### 3. Run the development server
```bash
npm run dev
```

#### 4. Test it!
Open [http://localhost:3000](http://localhost:3000) with your browser to see the dashboard.

**Important:** Make sure your backend is running on port 8000 before starting the frontend!

---

## Available Commands

- `npm run dev` - Start development server (with hot reload)
- `npm run build` - Build for production
- `npm start` - Run production build
- `npm run lint` - Check code quality

---

## Next.js Documentation

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
