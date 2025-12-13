# Frontend Setup Guide

This is a [Next.js](https://nextjs.org) dashboard for monitoring numerical machine data.

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
```n

This will install:
- **Next.js** - React framework
- **axios** - For API calls to the backend
- **recharts** - For data visualization charts
- **date-fns** - For date formatting
- **Tailwind CSS** - For styling

#### 3. Create a local variables file 
Create a file where you add your base URL for the backend connection (see backend docs)
```
NEXT_PUBLIC_API_URL= http://some_local_url
```

#### 4. Run the development server
```bash
npm run dev
```

#### 5. Test it!
Open [http://localhost:3000](http://localhost:3000) with your browser to see the dashboard.

**Important:** Make sure your backend is running on port 8000 before starting the frontend!

---

## Available Commands

- `npm run dev` - Start development server (with hot reload)
- `npm run build` - Build for production
- `npm start` - Run production build
- `npm run lint` - Check code quality