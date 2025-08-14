/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['localhost', 'vercel.app', 'vercel.com'],
  },
  env: {
    NEXTAUTH_URL: process.env.NEXTAUTH_URL,
    NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET,
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'}/api/:path*`,
      },
    ]
  },
  typescript: {
    // Allow builds to complete even with TypeScript errors during development
    ignoreBuildErrors: process.env.NODE_ENV === 'development',
  },
  eslint: {
    // Allow builds to complete even with ESLint errors during development
    ignoreDuringBuilds: process.env.NODE_ENV === 'development',
  },
}

module.exports = nextConfig