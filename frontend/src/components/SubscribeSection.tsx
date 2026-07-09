import { type FormEvent, useState } from "react";

import { ApiError, apiPost } from "../api/client";
import type { ThemeMode } from "../types/theme";

export function SubscribeSection({ themeMode }: { themeMode: ThemeMode }) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setStatus(null);

    try {
      await apiPost("/subscribers", { email: email.trim() });
      setEmail("");
      setStatus("You're in. The Daily Yorker will land in your inbox soon.");
    } catch (error: unknown) {
      if (error instanceof ApiError && error.status === 422) {
        setStatus("That email address does not look right. Check it and try again.");
      } else if (error instanceof TypeError) {
        setStatus(
          "Outside Edge cannot reach the subscription service right now. Try again shortly.",
        );
      } else {
        setStatus(
          "The subscription service could not complete your request. Try again shortly.",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section
      id="subscribe"
      className={
        themeMode === "dark"
          ? "mt-12 border-y border-white/10 bg-[#d7ff3f] px-5 py-8 text-[#17211b] sm:px-8 sm:py-10"
          : "mt-12 border-y border-black/10 bg-[#17211b] px-5 py-8 text-white sm:px-8 sm:py-10"
      }
    >
      <div className="grid gap-6 lg:grid-cols-[1fr_1.2fr] lg:items-end">
        <div>
          <p className="text-xs font-black uppercase tracking-[0.2em] opacity-60">
            The Daily Yorker
          </p>
          <h2 className="mt-2 text-3xl font-black tracking-normal sm:text-4xl">
            One sharp read. Every morning.
          </h2>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-2 sm:grid-cols-[1fr_auto]">
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              placeholder="you@example.com"
              className="min-h-12 w-full border border-current/20 bg-white px-4 text-[#17211b] outline-none focus:border-current"
            />
            <button
              type="submit"
              disabled={isSubmitting}
              className="min-h-12 bg-[#5fc47d] px-6 font-black text-[#17211b] disabled:opacity-60"
            >
              {isSubmitting ? "Joining..." : "Subscribe"}
            </button>
          </div>
          {status && <p className="mt-3 text-sm font-bold">{status}</p>}
        </form>
      </div>
    </section>
  );
}
