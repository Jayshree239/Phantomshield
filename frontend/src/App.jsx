import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Navbar from './components/ui/Navbar'
import Dashboard from './pages/Dashboard'
import Education from './pages/Education'
import Landing from './pages/Landing'
import ScanResultPage from './pages/ScanResult'

function AppShell() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[var(--paper-base)] text-[var(--ink-primary)]">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-24 top-16 h-72 w-72 rounded-full bg-[rgba(92,61,46,0.12)] blur-3xl" />
        <div className="absolute right-0 top-1/3 h-80 w-80 rounded-full bg-[rgba(156,123,94,0.14)] blur-3xl" />
        <div className="grid-overlay absolute inset-0" />
      </div>

      <Navbar />

      <main className="relative z-10">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/education" element={<Education />} />
          <Route path="/result" element={<ScanResultPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  )
}
