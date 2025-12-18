"use client"
import { usePathname, useSearchParams } from "next/navigation"
import Link from "next/link";

// SVG icons for each nav item
const icons: Record<string, React.ReactNode> = {
  '/dashboard': (
    // Grid/Dashboard icon (4 squares)
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zM14 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
    </svg>
  ),
  '/dashboard/energy': (
    // Lightning bolt icon
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  ),
  '/dashboard/alerts': (
    // Warning triangle icon
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  ),
};

// Typescript Object containing key-value pairs of our routes
const items = [ 
    {href: '/dashboard', label: "Dashboard"},
    {href: '/dashboard/energy', label : "Energy"},
    {href: '/dashboard/alerts', label : "Alerts"}    
];


export default function SideBar(){
    const pathname = usePathname();
    const searchParams = useSearchParams();
    
    // Preserve the date query parameter when navigating
    const date = searchParams.get('date');
    const queryString = date ? `?date=${date}` : '';

    return (
        <aside className="sticky top-0 w-64 h-screen bg-[#1e3a5f] text-slate-200 p-6 flex flex-col">
          <div className="text-2xl font-bold mb-10 tracking-wide">CNC Monitor</div>
          <nav className="space-y-3">
            {items.map((item) => {
              const active = pathname === item.href;
              return(
                <Link 
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-colors ${
                  active 
                    ? 'bg-blue-500 text-white font-semibold' 
                    : 'hover:bg-blue-500/20'
                }`}
                href={`${item.href}${queryString}`}
                key={item.href}>
                  {icons[item.href]}
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </aside>
      );
}