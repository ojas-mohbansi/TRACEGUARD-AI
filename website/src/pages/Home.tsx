import { Hero } from '../sections/Hero'
import { Problem } from '../sections/Problem'
import { HybridSection } from '../sections/HybridSection'
import { PipelineSection } from '../sections/PipelineSection'
import { ResearchSection } from '../sections/ResearchSection'

export function Home() {
  return (
    <>
      <Hero />
      <Problem />
      <HybridSection />
      <PipelineSection />
      <ResearchSection />
    </>
  )
}
