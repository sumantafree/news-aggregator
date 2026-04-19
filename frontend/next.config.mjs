/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [{ protocol: "https", hostname: "**" }, { protocol: "http", hostname: "**" }],
  },
  async rewrites() {
    const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return [
      { source: "/sitemap.xml", destination: `${api}/sitemap.xml` },
      { source: "/robots.txt", destination: `${api}/robots.txt` },
    ];
  },
};

export default nextConfig;
