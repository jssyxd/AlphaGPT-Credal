import type { Metadata } from 'next';
import DashboardPage from './dashboard-page';

export const metadata: Metadata = {
  title: 'AlphaGPT Dashboard',
  description: 'AlphaGPT Solana Meme Trading Dashboard',
};

export default function Page() {
  return <DashboardPage />;
}
