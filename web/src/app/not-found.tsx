import { PageShell } from "@/components/site/PageShell";
import { SITE_LINKS } from "@/components/site/siteContent";
import { ButtonLink, StatePanel } from "@/components/ui";

export default function NotFound() {
  return (
    <PageShell title="Page not found">
      <StatePanel state="not-found" links={SITE_LINKS.map((link) => <ButtonLink key={link.href} variant="quiet" href={link.href}>{link.label}</ButtonLink>)} />
    </PageShell>
  );
}
