import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Dashboard | MasterSpeak AI',
  description: 'Manage your speech analysis and track your communication progress.',
}

interface DashboardLayoutProps {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {children}
    </div>
  )
}