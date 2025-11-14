"use client"
import { usePathname } from "next/navigation"
import Link from "next/link";

// Typescript Object containing key-value pairs of our routes
const items = [ 
    {href: '/dashboard', label: "Dashboard"},
    {href: '/dashboard/alerts', label : "Alerts"},
    {href: '/dashboard/energy', label : "Energy"}    
];


export default function SideBar(){
    const pathname = usePathname()
    return (
        <aside className="sticky top-0 w-64 h-screen bg-slate-900 text-slate-200 p-4 flex flex-col">
          <div className="text-3xl font-bold mb-10">CNC Monitor</div>
          <nav className="space-y-2">
            {items.map((item) => {
              const active = pathname === item.href;
              return(
                <Link 
                className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
                  active 
                    ? 'bg-blue-600 text-white font-semibold' 
                    : 'hover:bg-slate-800'
                }`}
                href={item.href}
                key={item.href}>
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </aside>
      );
}