# Frontend Documentation

**2025G2**  
**October 2025**

## Introduction

The frontend is developed using Next.js with the App Router.  
Each route folder can include a consistent set of standard files:

| File Name | Purpose | Example Route Mapping |
|-----------|---------|----------------------|
| `page.tsx` | The main page component for the route | `/dashboard/page.tsx → /dashboard` |
| `layout.tsx` | Wraps pages with shared UI (e.g. navbar) | Applied to all children routes |
| `loading.tsx` | UI displayed while data loads | Automatic suspense loading state |
| `error.tsx` | UI displayed when an error occurs | Catches component or route errors |
| `not-found.tsx` | Custom 404 page | Used when route does not exist |

