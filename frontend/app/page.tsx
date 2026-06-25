"use client";

import {
    Navigation,
    Hero,
    HowItWorks,
    FeaturesGrid,
    Pricing,
    Footer,
} from "@/app/components/ui/saas-marketing";

export default function LandingPage() {
    return (
        <main style={{ minHeight: "100vh", background: "#000", color: "#fff" }}>
            {/* Public Marketing Layer */}
            <Navigation />
            <Hero />
            <HowItWorks />
            <FeaturesGrid />
            <Pricing />
            <Footer />
        </main>
    );
}
