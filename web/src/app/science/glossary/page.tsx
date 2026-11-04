import type { Metadata } from "next";
import { ArticleSection, ArticleShell } from "@/components/science/ArticleShell";
import { GLOSSARY, GLOSSARY_GROUPS, type GlossaryGroup } from "@/content/science-copy";
import styles from "@/components/science/Article.module.css";

export const metadata: Metadata = {
  title: "Glossary · NeuroFly",
  description: "The words NeuroFly uses for its objects, its kinds of data and the neuroscience behind the model.",
};

const GROUPS: readonly GlossaryGroup[] = ["objects", "kinds", "science"];

export default function GlossaryPage() {
  return (
    <ArticleShell
      eyebrow="Science"
      title="Glossary"
      contents={GROUPS.map((group) => ({ id: group, label: GLOSSARY_GROUPS[group].title }))}
      lead={<p>One word for each concept, used the same way on every page.</p>}
    >
      {GROUPS.map((group) => (
        <ArticleSection key={group} id={group} title={GLOSSARY_GROUPS[group].title}>
          <p>{GLOSSARY_GROUPS[group].intro}</p>
          <dl className={styles.glossary}>
            {GLOSSARY.filter((entry) => entry.group === group).map((entry) => (
              <div key={entry.id} id={entry.id}>
                <dt><a href={`#${entry.id}`}>{entry.term}</a></dt>
                <dd>{entry.meaning}</dd>
              </div>
            ))}
          </dl>
        </ArticleSection>
      ))}
    </ArticleShell>
  );
}
