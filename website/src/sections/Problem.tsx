import { ShieldAlert, ZapOff, Shuffle, HelpCircle } from 'lucide-react'
import { Container } from '../components/Container'
import { Reveal } from '../components/Reveal'
import { TextLink } from '../components/Button'
import { problem } from '../content'

const problemIcons = [Shuffle, ZapOff, HelpCircle]

export function Problem() {
  return (
    <section aria-labelledby="problem-title" className="border-t border-line bg-bg-deep py-24 sm:py-32">
      <Container size="xl">
        <Reveal>
          <div className="flex flex-col items-center text-center">
            <span className="font-mono text-xs uppercase tracking-wider text-threat-soft">
              {problem.eyebrow}
            </span>
            <h2 id="problem-title" className="mt-3 text-balance text-[32px] font-semibold tracking-[-0.02em] text-white sm:text-[44px]">
              {problem.title[0]} <span className="text-threat-soft">{problem.title[1]}</span>
            </h2>
            <p className="mt-4 max-w-[760px] text-pretty text-[16px] leading-relaxed text-soft">
              {problem.body}
            </p>
          </div>
        </Reveal>

        <ul className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {problem.cards.map((card, i) => {
            const Icon = problemIcons[i % problemIcons.length]
            return (
              <Reveal as="li" key={card.id} delay={i * 0.1}>
                <div className="group relative flex h-full flex-col justify-between rounded-card border border-line bg-surface p-7 transition-all duration-300 hover:border-threat-border hover:bg-surface-2">
                  <div>
                    <div className="flex items-center justify-between pb-4">
                      <span className="rounded-control border border-threat-border bg-threat-wash px-2.5 py-0.5 font-mono text-[11px] font-medium text-threat-soft">
                        {card.tag}
                      </span>
                      <div className="grid size-9 place-items-center rounded-[12px] bg-white/[0.05] text-soft transition-colors group-hover:bg-threat-wash group-hover:text-threat-soft">
                        <Icon className="size-4" aria-hidden />
                      </div>
                    </div>
                    <h3 className="text-[18px] font-semibold text-white">{card.title}</h3>
                    <p className="mt-2.5 text-[14.5px] leading-relaxed text-muted group-hover:text-soft transition-colors">
                      {card.body}
                    </p>
                  </div>

                  <div className="mt-6 border-t border-line pt-4">
                    <span className="inline-flex items-center gap-1.5 text-xs font-mono text-faint group-hover:text-threat-soft transition-colors">
                      <ShieldAlert className="size-3.5" aria-hidden />
                      Formal DFA prevents this in O(1)
                    </span>
                  </div>
                </div>
              </Reveal>
            )
          })}
        </ul>

        <div className="mt-12 flex justify-center">
          <TextLink href="/automaton" tone="signal" className="text-sm">
            <span>Explore how the 9-state DFA catches these violations</span>
          </TextLink>
        </div>
      </Container>
    </section>
  )
}
