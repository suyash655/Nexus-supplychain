import { render } from '@testing-library/react';
import LandingPage from './page';
import { describe, it, expect, vi } from 'vitest';

// Mock the components since they are imported from @/app/... which might cause resolution issues in simple tests without full setup
vi.mock('@/app/components/ui/saas-marketing', () => ({
  Navigation: () => <div data-testid="navigation" />,
  Hero: () => <div data-testid="hero" />,
  HowItWorks: () => <div data-testid="how-it-works" />,
  FeaturesGrid: () => <div data-testid="features-grid" />,
  Integrations: () => <div data-testid="integrations" />,
  Pricing: () => <div data-testid="pricing" />,
  Footer: () => <div data-testid="footer" />,
}));

describe('LandingPage', () => {
  it('renders correctly', () => {
    const { getByTestId } = render(<LandingPage />);
    expect(getByTestId('navigation')).toBeInTheDocument();
    expect(getByTestId('hero')).toBeInTheDocument();
  });
});
