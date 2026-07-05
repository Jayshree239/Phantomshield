// import { ShieldCheck, BarChart3, BookOpen, Radar } from 'lucide-react'
// import { NavLink } from 'react-router-dom'

// const links = [
//   { to: '/', label: 'Scanner', icon: Radar },
//   { to: '/dashboard', label: 'Dashboard', icon: BarChart3 },
//   { to: '/education', label: 'Education', icon: BookOpen },
// ]

// function linkClass({ isActive }) {
//   return [
//     'inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition-all duration-200',
//     isActive
//       ? 'bg-blue-500/15 text-blue-400 border border-blue-500/30 shadow-[0_0_12px_rgba(59,130,246,0.25)]'
//       : 'text-slate-300 border border-transparent hover:bg-white/5 hover:border-white/10 hover:text-white',
//   ].join(' ')
// }

// export default function Navbar() {
//   return (
//     <header className="sticky top-0 z-50 border-b border-white/10 bg-[#0b1220]/90 backdrop-blur-xl">
//       <nav className="mx-auto flex w-full max-w-[1300px] items-center justify-between px-6 py-4">

//         {/* LEFT */}
//         <NavLink
//           to="/"
//           className="flex items-center gap-3"
//         >
//           <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 shadow-lg">
//             <ShieldCheck size={22} />
//           </div>

//           <div className="leading-none">
//             <p className="text-lg font-semibold tracking-[0.18em] uppercase text-white">
//               PhantomShield
//             </p>

//             <p className="text-[10px] uppercase tracking-[0.25em] text-slate-400 mt-1">
//               Detect • Explain • Educate
//             </p>
//           </div>
//         </NavLink>

//         {/* CENTER */}
//         <div className="hidden md:flex items-center gap-3">
//           {links.map((link) => {
//             const Icon = link.icon

//             return (
//               <NavLink
//                 key={link.to}
//                 to={link.to}
//                 className={linkClass}
//               >
//                 <Icon size={16} />
//                 <span>{link.label}</span>
//               </NavLink>
//             )
//           })}
//         </div>

//         {/* RIGHT */}
//         <div className="flex items-center gap-3">
//           <NavLink
//             to="/"
//             className="
//               rounded-xl
//               bg-blue-600
//               px-5
//               py-2.5
//               text-sm
//               font-semibold
//               text-white
//               shadow-lg
//               transition-all
//               duration-200
//               hover:bg-blue-500
//               hover:shadow-blue-500/30
//               hover:scale-[1.02]
//               active:scale-[0.98]
//             "
//           >
//             Scan Now
//           </NavLink>
//         </div>

//       </nav>
//     </header>
//   )
// }



import { ShieldCheck, BarChart3, BookOpen, Radar } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Scanner', icon: Radar },
  { to: '/dashboard', label: 'Dashboard', icon: BarChart3 },
  { to: '/education', label: 'Education', icon: BookOpen },
]

function linkClass({ isActive }) {
  return [
    `
    group
    relative
    inline-flex
    items-center
    justify-center
    gap-2.5
    min-w-[130px]
    rounded-2xl
    px-5
    py-3
    text-sm
    font-medium
    transition-all
    duration-300
    ease-out
    `,
    isActive
      ? `
        border border-blue-500/30
        bg-blue-500/10
        text-blue-400
        shadow-[0_0_20px_rgba(59,130,246,0.22)]
      `
      : `
        border border-transparent
        text-slate-300
        hover:border-white/10
        hover:bg-white/5
        hover:text-white
      `,
  ].join(' ')
}

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-[#0f172a]/90 backdrop-blur-xl">
      <nav className="mx-auto flex w-full max-w-[1200px] flex-wrap items-center justify-between gap-4 px-6 py-4 lg:px-8">

        {/* Logo */}
        <NavLink to="/" className="flex items-center gap-3 shrink-0">
          <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-500/15 border border-blue-500/20 text-blue-400 shadow-lg shadow-blue-500/10">
            <ShieldCheck size={20} />
          </span>

          <div className="leading-none">
            <p className="text-lg font-semibold tracking-wide text-white">
              PhantomShield
            </p>

            <p className="text-[11px] uppercase tracking-[0.22em] text-slate-400">
              Detect • Explain • Educate
            </p>
          </div>
        </NavLink>

        {/* Navigation */}
        <div className="flex flex-1 items-center justify-center">
          <div className="flex items-center gap-4 md:gap-7 lg:gap-9">
          {links.map((link) => {
            const Icon = link.icon

            return (
              <NavLink
                key={link.to}
                to={link.to}
                className={linkClass}
              >
                <Icon size={16} />
                <span>{link.label}</span>
              </NavLink>
            )
          })}
        </div>
        </div>

        {/* CTA Button */}
        <div className="flex items-center">
          <NavLink
            to="/"
            className="rounded-2xl bg-blue-500 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition-all duration-200 hover:bg-blue-400 hover:shadow-blue-500/40"
          >
            Scan Now
          </NavLink>
        </div>
      </nav>
    </header>
  )
}