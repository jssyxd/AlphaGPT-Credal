import type { Metadata } from 'next';
import { Inspector } from 'react-dev-inspector';
import './globals.css';

export const metadata: Metadata = {
  title: {
    default: 'AlphaGPT Dashboard',
    template: '%s | AlphaGPT',
  },
  description: 'AlphaGPT - AI驱动的 Solana Meme 币交易仪表板',
  keywords: [
    'AlphaGPT',
    'Solana',
    'Meme Coin',
    'AI Trading',
    'Quantitative Trading',
    'DeFi',
  ],
  authors: [{ name: 'AlphaGPT Team' }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const isDev = process.env.NODE_ENV === 'development';

  return (
    <html lang="zh-CN" className="dark">
      <body className={`antialiased bg-slate-900`}>
        {isDev && <Inspector />}
        {children}
      </body>
    </html>
  );
}
