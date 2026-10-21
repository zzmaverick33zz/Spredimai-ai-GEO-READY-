import { Poppins, Unbounded } from "next/font/google";

// `subsets` only controls preloading: latin-ext (Lithuanian letters) is still
// declared via unicode-range and loads on demand on /lt.

export const unbounded = Unbounded({
  subsets: ["latin"],
  weight: ["600", "800"],
  variable: "--font-unbounded",
  display: "swap",
});

export const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-poppins",
  display: "swap",
});
