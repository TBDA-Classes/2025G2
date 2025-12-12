# Frontend Documentation

**2025G2**  
**October 2025**

Dates of interest for displaying the frontend design choices:
- 14/03/2021 Giving high spike in one temperature
- 14/09/2021 Showing Machine Status Timeline in good detail


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

## Throwing and Re-throwing Errors in React

```typescript
try {
  const data = await someFunction();
} catch (error) {
  // Option 1: Re-throw as-is
  throw error;
  
  // Option 2: Wrap with more context
  throw new Error(`Failed to load temperatures: ${error.message}`);
  
  // Option 3: Create custom error with original attached
  const newError = new Error("Temperature fetch failed");
  newError.cause = error;  // Attach original error
  throw newError;
}
```

