import { redirect } from "next/navigation";

export default function Home() {
  // Default to English; users can switch via the language toggle.
  redirect("/en");
}
