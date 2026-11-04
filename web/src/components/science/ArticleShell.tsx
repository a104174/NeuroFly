import type { ReactNode } from "react";
import { SiteFooter, SiteHeader } from "@/components/site/SiteChrome";
import styles from "./Article.module.css";

export interface ContentsItem { readonly id: string; readonly label: string }

/**
 * Calm long-form layout for the Science pages: a title block, a contents list that is sticky from
 * 1024 px, and an article column with a 68-character measure. Migrated to the tokens, so it
 * follows the theme and shows the theme switch.
 */
export function ArticleShell({
  eyebrow,
  title,
  lead,
  contents,
  children,
}: {
  eyebrow: string;
  title: string;
  lead: ReactNode;
  contents: readonly ContentsItem[];
  children: ReactNode;
}) {
  return (
    <div data-themed-page className={styles.page}>
      {/* Reveals the server-rendered page when JS cannot finish the root loading boundary. */}
      <SiteHeader current="/science" />
      <main id="main-content" tabIndex={-1} className={styles.main}>
        <header className={styles.hero}>
          <p className={styles.eyebrow}>{eyebrow}</p>
          <h1>{title}</h1>
          <div className={styles.lead}>{lead}</div>
        </header>
        <div className={styles.layout}>
          <nav aria-label="On this page" className={styles.contents}>
            <p className={styles.contentsTitle}>On this page</p>
            <ol>{contents.map((item) => <li key={item.id}><a href={`#${item.id}`}>{item.label}</a></li>)}</ol>
          </nav>
          <article className={styles.article}>{children}</article>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}

/** A titled section with a stable anchor. */
export function ArticleSection({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return (
    <section id={id} aria-labelledby={`${id}-title`} className={styles.section}>
      <h2 id={`${id}-title`}>{title}</h2>
      {children}
    </section>
  );
}
