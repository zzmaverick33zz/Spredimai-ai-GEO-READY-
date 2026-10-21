import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: { formats: ["image/avif", "image/webp"], qualities: [75, 90] },
  poweredByHeader: false,
  // The repo root has its own lockfile (another project); trace from here.
  outputFileTracingRoot: path.join(__dirname),
};

export default nextConfig;
