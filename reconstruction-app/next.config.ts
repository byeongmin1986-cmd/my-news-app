import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  basePath: '/my-news-app',
  images: { unoptimized: true },
};

export default nextConfig;
